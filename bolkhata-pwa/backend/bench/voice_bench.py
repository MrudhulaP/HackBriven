"""Real-voice benchmark for English, Hindi and Hinglish (needs GNANI_API_KEY; LLM keys optional).

Each test sentence is spoken by Gnani TTS, transcribed by Gnani STT (Prisma v3.0, indic-auto) and handled by the
app (rules + LLM brain) on a throwaway database. Reports, per language:
  WER      word error rate of the transcript vs the written sentence (number formatting differences count as errors)
  meaning  the right intent AND the right values (name/amount/items/phone) — what actually matters for the ledger
  numbers  spoken amounts read correctly
  latency  STT processing time and the app's reply time
Synthetic voices only: real accents, speeds and shop noise are not covered.  Run:
  docker compose exec -w /app -e PYTHONPATH=/app:/app/tests/data backend python bench/voice_bench.py
"""
import array
import asyncio
import base64
import json
import os
import re
import sys
import time

import mongomock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tests", "data"))
from en_hi_cases import CASES  # noqa: E402
from run_probe import KEY  # noqa: E402

from app import gnani  # noqa: E402
from app.ai.llm_brain import build_brain  # noqa: E402
from app.dialogue import Conversation  # noqa: E402
from app.lang import edit_distance  # noqa: E402
from app.store import Crypto, Store  # noqa: E402

_DIG = str.maketrans("०१२३४५६७८९", "0123456789")


def words(s):
    s = s.translate(_DIG).lower().replace("₹", " ")
    s = re.sub(r"(\d)[,\s](?=\d)", r"\1", s)
    return re.sub(r"[^\w\sऀ-ॿ]", " ", s).split()


def to16k(pcm, rate):
    a = array.array("h", pcm)
    n = int(len(a) * 16000 / rate)
    out = array.array("h", bytes(2 * n))
    for i in range(n):
        p = i * rate / 16000
        j = int(p)
        f = p - j
        out[i] = int(a[j] * (1 - f) + a[min(j + 1, len(a) - 1)] * f)
    return out.tobytes()


async def main():
    key = os.environ["GNANI_API_KEY"]
    brain = build_brain()
    rows = []
    for text, lang, intent, exp in CASES:
        rate, pcm = await gnani.tts_rest(key, text, "en" if lang == "en" else "hi")
        t0 = time.perf_counter()
        r = await gnani.stt_rest(key, gnani.pcm_to_wav(to16k(pcm, rate)), "auto")
        stt_ms = round((r.get("processing_time") or (time.perf_counter() - t0)) * 1000)
        heard = r.get("transcript", "").strip()
        store = Store(mongomock.MongoClient().db, Crypto(base64.urlsafe_b64encode(b"k" * 32).decode()))
        store.seed_demo()
        t1 = time.perf_counter()
        rep, src, _ = await Conversation(store, "auto", "en").handle_smart(heard, r.get("detected_language_code"), brain=brain,
                                                                            spoken=False)
        reply_ms = round((time.perf_counter() - t1) * 1000)
        card = rep.get("card") or {}
        got = KEY.get(rep["key"], rep["key"])
        vals = all(re.sub(r"\D", "", str(card.get(k))) == v if k == "phone" else card.get(k) == v
                   for k, v in exp.items() if k in ("amount", "phone") and k in card)
        ref, hyp = words(text), words(heard)
        rows.append({"lang": lang, "text": text, "heard": heard, "wer": edit_distance(ref, hyp) / max(1, len(ref)),
                     "intent_ok": got == intent, "meaning_ok": got == intent and vals, "has_amount": "amount" in exp,
                     "amount_ok": card.get("amount") == exp.get("amount"), "stt_ms": stt_ms, "reply_ms": reply_ms,
                     "source": src, "reply": rep["text"]})
        await asyncio.sleep(0.3)
    for lang in ("en", "hi", "hinglish"):
        rs = [x for x in rows if x["lang"] == lang]
        am = [x for x in rs if x["has_amount"]]
        print(f"{lang:9} n={len(rs):2}  WER={sum(x['wer'] for x in rs) / len(rs):.1%}  "
              f"intent={sum(x['intent_ok'] for x in rs)}/{len(rs)}  meaning={sum(x['meaning_ok'] for x in rs)}/{len(rs)}  "
              f"amounts={sum(x['amount_ok'] for x in am)}/{len(am)}  "
              f"STT~{sorted(x['stt_ms'] for x in rs)[len(rs) // 2]} ms  reply~{sorted(x['reply_ms'] for x in rs)[len(rs) // 2]} ms  "
              f"LLM used {sum(x['source'] not in ('rules', 'junk') for x in rs)}x")
    for x in rows:
        if not x["meaning_ok"]:
            print(f"  MISS [{x['lang']}] said {x['text']!r}\n       heard {x['heard']!r} -> [{x['source']}] {x['reply'][:70]}")
    with open("/tmp/voice_bench.json", "w") as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    asyncio.run(main())
