"""Frame splitter, WAV fix and the /ws/voice relay, with Gnani mocked."""
import asyncio
import json
import random
import struct

import pytest
from fastapi.testclient import TestClient

from app import gnani, main
from app.gnani import FRAME, FrameSplitter, fix_wav, pcm_to_wav, wav_pcm


@pytest.mark.parametrize("seed", range(5))
def test_frame_splitter_always_1024(seed):
    rnd = random.Random(seed)
    s, total, out = FrameSplitter(), 0, []
    for _ in range(200):
        n = rnd.randint(0, 5000)
        total += n
        out += s.feed(bytes(n))
    out += s.flush()
    assert out and all(len(f) == FRAME for f in out)
    assert len(out) == -(-total // FRAME)


def test_fix_wav_rewrites_ffffffff_sizes():
    wav = bytearray(pcm_to_wav(b"\x01\x00" * 1000, 22050))
    struct.pack_into("<I", wav, 4, 0xFFFFFFFF)
    struct.pack_into("<I", wav, 40, 0xFFFFFFFF)
    fixed = fix_wav(bytes(wav))
    assert struct.unpack_from("<I", fixed, 4)[0] == len(fixed) - 8
    rate, pcm = wav_pcm(bytes(wav))
    assert rate == 22050 and len(pcm) == 2000


class FakeSTT:
    """Pretends to be the Gnani STT socket: says connected, then one transcript per commit."""

    def __init__(self, transcripts):
        self.q = asyncio.Queue()
        self.sent, self.transcripts = [], list(transcripts)
        self.q.put_nowait(json.dumps({"type": "connected"}))

    async def send(self, data):
        self.sent.append(data)
        if isinstance(data, str) and json.loads(data)["type"] == "update_settings":
            self.q.put_nowait(json.dumps({"type": "error", "message": "bias not supported"}))
        if isinstance(data, str) and json.loads(data)["type"] == "commit":
            self.q.put_nowait(json.dumps({"type": "speech_start"}))
            self.q.put_nowait(json.dumps({"type": "transcript", "text": self.transcripts.pop(0),
                                          "detected_language_code": "hi-IN", "latency": 210}))

    async def close(self):
        self.q.put_nowait(None)

    def __aiter__(self):
        return self

    async def __anext__(self):
        m = await self.q.get()
        if m is None:
            raise StopAsyncIteration
        return m


@pytest.fixture
def client(db, monkeypatch):
    fake = FakeSTT(["Ramesh ka total kitna"])

    async def stt_connect(key, mode, regional="", noisy=False):
        return fake

    async def tts_stream(key, text, lang):
        for _ in range(3):
            yield b"\x00\x01" * 100

    monkeypatch.setattr(gnani, "stt_connect", stt_connect)
    monkeypatch.setattr(gnani, "tts_stream", tts_stream)
    app = main.create_app(db)
    with TestClient(app) as c:
        c.fake = fake
        yield c


def recv_until(ws, kind):
    seen = []
    while True:
        m = ws.receive()
        if m.get("bytes") is not None:
            seen.append(("audio", len(m["bytes"])))
            continue
        j = json.loads(m["text"])
        seen.append(j)
        if j["type"] == kind:
            return seen


def test_ws_live_flow(client):
    with client.websocket_connect("/ws/voice") as ws:
        ws.send_text(json.dumps({"type": "start", "engine": "live", "lang": "auto"}))
        seen = recv_until(ws, "tts_end")
        assert seen[0]["key"] == "greeting" and "AI" in seen[0]["text"]
        assert ("audio", 200) in seen  # TTS chunks streamed as binary

        ws.send_text(json.dumps({"type": "mic_on"}))
        assert recv_until(ws, "warning")[-1]["key"] == "biasWarning"  # bias rejected -> warn, keep going
        ws.send_bytes(b"\x00" * 1500)
        ws.send_text(json.dumps({"type": "commit"}))
        seen = recv_until(ws, "reply")
        tr = next(m for m in seen if isinstance(m, dict) and m["type"] == "transcript")
        assert tr["stt_ms"] == 210
        assert "Gandhi Nagar 450" in seen[-1]["text"]
        frames = [f for f in client.fake.sent if isinstance(f, bytes)]
        assert frames and all(len(f) == FRAME for f in frames)


def test_ws_typed_text_same_flow(client):
    with client.websocket_connect("/ws/voice") as ws:
        ws.send_text(json.dumps({"type": "start", "engine": "browser", "lang": "auto"}))
        recv_until(ws, "reply")
        ws.send_text(json.dumps({"type": "text", "text": "Lakshmi ne 50 udhaar liya"}))
        r = recv_until(ws, "reply")[-1]
        assert r["state"] == "confirming"
        ws.send_text(json.dumps({"type": "tap", "action": "save"}))
        r = recv_until(ws, "reply")[-1]
        assert r["saved"] and "170" in r["text"]


def test_rest_endpoints_and_csv(client):
    cs = client.get("/api/customers").json()
    assert len(cs) == 3
    lak = next(c for c in cs if c["name"] == "Lakshmi")
    h = client.get(f"/api/customers/{lak['id']}").json()
    assert h["history"][0]["running"] == 120
    csv = client.get("/api/ledger.csv")
    assert csv.content.startswith("﻿".encode())
    client.put("/api/settings", json={"shop_name": "Sharma Store", "upi_vpa": "sharma@upi"})
    url = client.get(f"/api/customers/{lak['id']}/reminder?lang=en").json()["url"]
    assert url.startswith("https://wa.me/919000000003?text=") and "gentle%20reminder" in url
    assert "am%3D120" in url


def test_barge_in_stops_reply(db, monkeypatch):
    fake = FakeSTT(["Lakshmi ka baaki"])

    async def stt_connect(key, mode, regional="", noisy=False):
        return fake

    async def slow_tts(key, text, lang):
        for _ in range(100):
            yield b"\x00\x01" * 100
            await asyncio.sleep(0.05)

    monkeypatch.setattr(gnani, "stt_connect", stt_connect)
    monkeypatch.setattr(gnani, "tts_stream", slow_tts)
    with TestClient(main.create_app(db)) as c, c.websocket_connect("/ws/voice") as ws:
        ws.send_text(json.dumps({"type": "start", "engine": "live", "lang": "auto", "bargeIn": True}))
        recv_until(ws, "tts_start")  # greeting is now playing
        ws.send_text(json.dumps({"type": "mic_on"}))
        ws.send_text(json.dumps({"type": "commit"}))  # fake Gnani answers with speech_start
        seen = recv_until(ws, "speech_start")
        end = next(m for m in seen if isinstance(m, dict) and m["type"] == "tts_end")
        assert end["interrupted"] is True  # TTS socket closed before speech_start reached the browser
