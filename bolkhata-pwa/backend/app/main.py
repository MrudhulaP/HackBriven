"""BolKhata API + /ws/voice relay (browser <-> backend <-> Gnani)."""
import asyncio
import contextlib
import csv
import io
import json
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from . import gnani
from .ai.llm_brain import build_brain
from .dialogue import Conversation, pending_text
from .gnani import FRAME, FrameSplitter, GnaniError
from .prompts import ARRIVED_MSG, REMINDER, UI, say
from .store import Crypto, Store

IST = timezone(timedelta(hours=5, minutes=30))
MAX_REST_BYTES = 30 * 16000 * 2  # Gnani REST takes 30 s max


def create_app(db=None, brain="env") -> FastAPI:
    if db is None:
        from pymongo import MongoClient
        db = MongoClient(os.environ.get("MONGO_URL", "mongodb://localhost:27017"), tz_aware=True)[os.environ.get("MONGO_DB", "bolkhata")]
    if not os.environ.get("ENCRYPTION_KEY"):
        raise RuntimeError("Set ENCRYPTION_KEY (32 random bytes, base64). See README.")
    store = Store(db, Crypto(os.environ["ENCRYPTION_KEY"]))
    seed = os.environ.get("SEED_DEMO", "true").lower() != "false"
    if seed:
        store.seed_demo()
    app = FastAPI(title="BolKhata")
    app.state.store = store
    app.state.brain = build_brain() if brain == "env" else brain  # None = rules only

    def key():
        return os.environ.get("GNANI_API_KEY", "")

    # ---------- REST
    @app.get("/api/meta")
    def meta():
        b = app.state.brain
        return {"seed_demo": seed, "gnani": bool(key()), "ui": UI,
                "llm": [c.name for c in b.clients] if b is not None and hasattr(b, "clients") else bool(b)}

    @app.get("/api/customers")
    def customers():
        return store.customers()

    @app.get("/api/customers/{cid}")
    def customer(cid: str):
        c = store.customer(cid)
        if not c:
            raise HTTPException(404, "customer not found")
        running, hist = 0, []
        for e in store.entries(cid):
            running += e["amount"] if e["type"] == "credit" else -e["amount"]
            hist.append({**e, "running": running})
        return {**c, "history": hist[::-1]}

    @app.put("/api/customers/{cid}")
    def update_customer(cid: str, body: dict):
        if not store.customer(cid):
            raise HTTPException(404, "customer not found")
        phone = None
        if "phone" in body:
            phone = "".join(ch for ch in str(body["phone"] or "") if ch.isdigit())[-10:]
            if phone and len(phone) != 10:
                raise HTTPException(422, "phone must be 10 digits")
        note = str(body["note"]).strip()[:60] if "note" in body else None
        store.update_customer(cid, phone=phone, note=note)
        return store.customer(cid)

    @app.get("/api/customers/{cid}/reminder")
    def reminder(cid: str, lang: str = "hi"):
        c, s = store.customer(cid), store.settings()
        if not c or c["balance"] <= 0 or not c["phone"]:
            raise HTTPException(422, "needs a phone number and a balance above 0")
        upi = (f"upi://pay?pa={quote(s['upi_vpa'])}&pn={quote(s['shop_name'])}&am={c['balance']}&cu=INR"
               if s["upi_vpa"] else "")
        text = REMINDER.get(lang, REMINDER["hi"]).format(name=c["name"], shop=s["shop_name"], amount=c["balance"], upi=upi)
        return {"url": f"https://wa.me/91{c['phone']}?text={quote(text)}"}

    @app.get("/api/customers/{cid}/arrived-message")
    def arrived_message(cid: str, lang: str = "hi"):
        c, s = store.customer(cid), store.settings()
        orders = store.orders("arrived", cid)
        if not c or not c["phone"] or not orders:
            raise HTTPException(422, "needs a phone number and an arrived order")
        items = ", ".join(o["items"] for o in orders)
        text = ARRIVED_MSG.get(lang, ARRIVED_MSG["hi"]).format(name=c["name"], items=items, shop=s["shop_name"])
        return {"url": f"https://wa.me/91{c['phone']}?text={quote(text)}"}

    @app.get("/api/orders")
    def orders():
        return [o for o in store.orders() if o["status"] != "closed"][::-1]

    @app.put("/api/orders/{oid}")
    def set_order(oid: str, body: dict):
        try:
            ok = store.set_order_status(oid, body.get("status"))
        except ValueError as e:
            raise HTTPException(422, str(e)) from e
        if not ok:
            raise HTTPException(404, "order not found")
        return {"ok": True}

    @app.get("/api/evening")
    def evening(lang: str = "hi"):
        return evening_summary(store, lang)

    def ledger_rows():
        names = {c["id"]: (c["name"] + (f" ({c['note']})" if c["note"] else "")) for c in store.customers()}
        return [{**e, "customer": names.get(e["customer_id"], "?"),
                 "created_at": e["created_at"].replace(tzinfo=timezone.utc).astimezone(IST).isoformat(timespec="seconds")}
                for e in reversed(store.entries())]

    @app.get("/api/ledger")
    def ledger():
        rows = ledger_rows()
        today = datetime.now(IST).date().isoformat()
        t = [r for r in rows if r["created_at"].startswith(today)]
        credit = sum(r["amount"] for r in t if r["type"] == "credit")
        paid = sum(r["amount"] for r in t if r["type"] == "payment")
        return {"today": {"credit": credit, "payment": paid, "net": credit - paid}, "entries": rows}

    @app.get("/api/ledger.csv")
    def ledger_csv():
        out = io.StringIO()
        w = csv.writer(out)
        w.writerow(["time", "customer", "type", "amount", "language", "said"])
        for r in ledger_rows():
            w.writerow([r["created_at"], r["customer"], r["type"], r["amount"], r["language"], r["raw_text"]])
        return Response("﻿" + out.getvalue(), media_type="text/csv; charset=utf-8",  # BOM so Excel shows Hindi
                        headers={"Content-Disposition": "attachment; filename=bolkhata-ledger.csv"})

    @app.get("/api/settings")
    def get_settings():
        return store.settings()

    @app.put("/api/settings")
    def put_settings(body: dict):
        try:
            return store.save_settings(body)
        except ValueError as e:
            raise HTTPException(422, str(e)) from e

    # ---------- voice
    @app.websocket("/ws/voice")
    async def ws_voice(ws: WebSocket):
        await ws.accept()
        await VoiceSession(ws, store, key(), app.state.brain).run()

    dist = Path(os.environ.get("FRONTEND_DIST", Path(__file__).resolve().parents[2] / "frontend" / "dist"))
    if dist.is_dir():
        app.mount("/assets", StaticFiles(directory=dist / "assets"), name="assets")

        @app.get("/{path:path}")
        def spa(path: str):
            f = dist / path
            return FileResponse(f if path and f.is_file() and dist in f.resolve().parents else dist / "index.html")

    return app


def evening_summary(store, lang):
    """Customers without a phone number and pending orders, for the end-of-day reminder."""
    missing = [{"id": c["id"], "name": c["name"], "note": c["note"]} for c in store.customers() if not c["phone"]]
    pending = store.orders("pending")
    parts = []
    if missing:
        names = ", ".join(c["name"] + (f" ({c['note']})" if c["note"] else "") for c in missing)
        parts.append(say(lang, "missingPhones", count=len(missing), names=names))
    if pending:
        parts.append(say(lang, "pendingList", list=pending_text(pending)))
    return {"missing": missing, "orders": pending, "text": " ".join(parts)}


class VoiceSession:
    """One browser connection. Engines: live (Gnani WS), rest (Gnani REST), browser (Web Speech, text only here)."""

    def __init__(self, ws: WebSocket, store: Store, api_key: str, brain=None):
        self.ws, self.store, self.key = ws, store, api_key
        self.brain, self.brain_on = brain, brain is not None
        s = store.settings()
        self.conv = Conversation(store, "auto", "hi" if s["default_language"] == "auto" else s["default_language"])
        self.engine, self.barge_in = "live", False
        self.lock = asyncio.Lock()
        self.stt = None
        self.stt_reader = None
        self.tts_task = None
        self.splitter = FrameSplitter()
        self.rest_buf = bytearray()
        self.bias_pending = False

    async def send(self, obj):
        async with self.lock:
            if isinstance(obj, bytes):
                await self.ws.send_bytes(obj)
            else:
                await self.ws.send_text(json.dumps(obj, ensure_ascii=False, default=str))

    async def run(self):
        try:
            while True:
                msg = await self.ws.receive()
                if msg["type"] == "websocket.disconnect":
                    break
                if msg.get("bytes") is not None:
                    await self.on_audio(msg["bytes"])
                elif msg.get("text"):
                    await self.on_command(json.loads(msg["text"]))
        except WebSocketDisconnect:
            pass
        finally:
            await self.stop_tts()
            await self.close_stt()

    async def on_command(self, m):
        t = m.get("type")
        if t == "start":
            self.engine = m.get("engine", "live")
            self.barge_in = bool(m.get("bargeIn"))
            self.conv.set_mode(m.get("lang", "auto"))
            await self.reply(self.conv.greeting())
        elif t == "config":
            if "bargeIn" in m:
                self.barge_in = bool(m["bargeIn"])
            if "lang" in m:
                self.conv.set_mode(m["lang"])
            if "brain" in m:
                self.brain_on = bool(m["brain"]) and self.brain is not None
            if m.get("engine") and m["engine"] != self.engine:
                await self.close_stt()
                self.engine = m["engine"]
        elif t == "mic_on":
            self.rest_buf.clear()
            if self.engine == "live":
                await self.open_stt()
        elif t == "commit":
            if self.engine == "live" and self.stt:
                for f in self.splitter.flush():
                    await self.stt.send(f)
                await self.stt.send(json.dumps({"type": "commit"}))
            elif self.engine == "rest":
                await self.rest_transcribe()
        elif t == "mic_off":
            if self.stt:
                asyncio.get_running_loop().call_later(2.0, lambda: asyncio.ensure_future(self.close_stt()))
        elif t == "text":
            await self.on_transcript(str(m.get("text", ""))[:500], None, None, speak=m.get("speak", True), spoken=False)
        elif t == "evening":  # spoken end-of-day reminder; does not touch the dialogue state
            text = evening_summary(self.store, self.conv.lang)["text"]
            if text:
                await self.reply({"type": "reply", "key": "evening", "text": text, "lang": self.conv.lang,
                                  "state": self.conv.state, "card": None, "options": [], "saved": False, "evening": True})
        elif t == "tap":
            a = m.get("action")
            r = (self.conv.tap_confirm(True) if a == "save" else self.conv.tap_confirm(False) if a == "cancel"
                 else self.conv.tap_choose(int(m.get("index", -1))) if a == "choose"
                 else self.conv.tap_amount(int(m.get("amount", 0))) if a == "amount"
                 else self.conv.undo() if a == "undo" else None)
            if r:
                await self.reply(r)

    async def on_audio(self, data: bytes):
        if self.engine == "live" and self.stt:
            for f in self.splitter.feed(data):
                await self.stt.send(f)
        elif self.engine == "rest" and len(self.rest_buf) < MAX_REST_BYTES:
            self.rest_buf += data[:MAX_REST_BYTES - len(self.rest_buf)]

    # ---------- STT
    async def open_stt(self):
        if self.stt:
            return
        try:
            if not self.key:
                raise GnaniError("GNANI_API_KEY not set")
            self.stt = await gnani.stt_connect(self.key, self.conv.mode, self.store.settings()["regional_language"])
        except Exception as e:  # noqa: BLE001 - any failure means fall back to the next engine
            await self.send({"type": "engine_failed", "engine": "live", "reason": str(e)[:200]})
            return
        self.splitter = FrameSplitter()
        self.stt_reader = asyncio.create_task(self.read_stt(self.stt))

    async def close_stt(self):
        stt, self.stt = self.stt, None
        if stt:
            with contextlib.suppress(Exception):
                await stt.close()

    async def read_stt(self, stt):
        try:
            async for raw in stt:
                m = json.loads(raw)
                t = m.get("type")
                if t == "connected":
                    words = sorted({w for c in self.store.customers() for w in c["name"].split() if w.isalpha()})[:100]
                    if words:
                        self.bias_pending = True
                        await stt.send(json.dumps({"type": "update_settings", "bias": {"list": words, "score": 1.5}}))
                elif t == "settings_updated":
                    self.bias_pending = False
                elif t == "speech_start":
                    if self.barge_in:
                        await self.stop_tts()
                    await self.send({"type": "speech_start"})
                elif t == "transcript" and (m.get("text") or "").strip():
                    await self.on_transcript(m["text"].strip(), m.get("detected_language_code"), m.get("latency"))
                elif t == "error":
                    if self.bias_pending:
                        self.bias_pending = False
                        await self.send({"type": "warning", "key": "biasWarning", "detail": m.get("message")})
                    else:
                        await self.send({"type": "warning", "key": None, "detail": m.get("message")})
        except Exception as e:  # noqa: BLE001
            if self.stt is stt:
                await self.send({"type": "engine_failed", "engine": "live", "reason": str(e)[:200]})
        finally:
            if self.stt is stt:
                self.stt = None

    async def rest_transcribe(self):
        pcm, self.rest_buf = bytes(self.rest_buf), bytearray()
        if len(pcm) < 3200:  # < 0.1 s
            return
        try:
            if not self.key:
                raise GnaniError("GNANI_API_KEY not set")
            t0 = time.perf_counter()
            r = await gnani.stt_rest(self.key, gnani.pcm_to_wav(pcm), self.conv.mode,
                                     self.store.settings()["regional_language"])
        except Exception as e:  # noqa: BLE001
            await self.send({"type": "engine_failed", "engine": "rest", "reason": str(e)[:200]})
            return
        ms = round((r.get("processing_time") or (time.perf_counter() - t0)) * 1000)
        if r.get("transcript", "").strip():
            await self.on_transcript(r["transcript"].strip(), r.get("detected_language_code"), ms)

    # ---------- dialogue + TTS
    async def on_transcript(self, text, detected, stt_ms, speak=True, spoken=True):
        if not text:
            return
        await self.send({"type": "transcript", "text": text, "detected": detected, "stt_ms": stt_ms})
        r, source, ms = await self.conv.handle_smart(text, detected, self.brain if self.brain_on else None, spoken)
        if r is None:
            return  # junk ('hmm', noise): ignored, no reply
        await self.reply({**r, "source": source, "brain_ms": ms}, speak)

    async def reply(self, r, speak=True):
        await self.send(r)
        await self.stop_tts()
        if not speak:
            return
        if self.engine == "browser":
            await self.send({"type": "tts_failed", "text": r["text"], "lang": r["lang"]})  # browser speaks it
        else:
            self.tts_task = asyncio.create_task(self.speak(r["text"], r["lang"]))

    async def stop_tts(self):
        task, self.tts_task = self.tts_task, None
        if task and not task.done():
            task.cancel()  # closes the Gnani TTS socket (no cancel message exists)
            with contextlib.suppress(BaseException):
                await task
            await self.send({"type": "tts_end", "interrupted": True})

    async def speak(self, text, lang):
        started = False
        try:
            if not self.key:
                raise GnaniError("GNANI_API_KEY not set")
            if self.engine == "live":
                try:
                    gen = gnani.tts_stream(self.key, text, lang)
                    try:
                        async for chunk in gen:
                            if not started:
                                started = True
                                await self.send({"type": "tts_start", "rate": gnani.TTS_RATE})
                            await self.send(chunk)
                    finally:
                        await gen.aclose()
                    await self.send({"type": "tts_end"})
                    return
                except asyncio.CancelledError:
                    raise
                except Exception:  # noqa: BLE001 - fall through to REST unless audio already played
                    if started:
                        raise
            rate, pcm = await gnani.tts_rest(self.key, text, lang)
            await self.send({"type": "tts_start", "rate": rate})
            for i in range(0, len(pcm), 8192):
                await self.send(pcm[i:i + 8192])
            await self.send({"type": "tts_end"})
        except asyncio.CancelledError:
            raise
        except Exception as e:  # noqa: BLE001 - browser speechSynthesis is the last fallback
            await self.send({"type": "tts_failed", "text": text, "lang": lang, "reason": str(e)[:200]})


app = create_app() if os.environ.get("BOLKHATA_NO_APP") != "1" else None
