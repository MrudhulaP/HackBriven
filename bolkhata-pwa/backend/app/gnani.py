"""Gnani (Vachana) clients. Endpoints, headers and fields from docs.gnani.ai only.
The API key never leaves the backend."""
import base64
import io
import json
import struct
import wave

import httpx
import websockets

STT_WS = "wss://api.vachana.ai/stt/v3/stream"
STT_REST = "https://api.vachana.ai/stt/v3"
TTS_WS = "wss://api.vachana.ai/api/v1/tts"
TTS_REST = "https://api.vachana.ai/api/v1/tts/inference"
FRAME = 1024  # bytes = 512 samples of 16-bit PCM
TTS_RATE = 22050
CODES = {"hi": "hi-IN", "en": "en-IN", "kn": "kn-IN", "te": "te-IN", "ta": "ta-IN"}


class GnaniError(Exception):
    pass


def stt_language(mode: str, regional: str = "") -> str:
    """A fixed language, or for Auto: Hindi + English + the shop's regional language (Prisma v3.0 takes up to 4),
    which stops Kannada/Tamil being heard as Telugu. No regional language set: Gnani's indic-auto."""
    if mode in CODES:
        return CODES[mode]
    return f"hi-IN,en-IN,{CODES[regional]}" if regional in ("kn", "te", "ta") else "indic-auto"


class FrameSplitter:
    """Re-chunks any byte stream into frames of exactly FRAME bytes."""

    def __init__(self):
        self.buf = bytearray()

    def feed(self, data: bytes) -> list[bytes]:
        self.buf += data
        n = len(self.buf) // FRAME * FRAME
        frames = [bytes(self.buf[i:i + FRAME]) for i in range(0, n, FRAME)]
        del self.buf[:n]
        return frames

    def flush(self) -> list[bytes]:
        """Pads the tail with silence so even the last frame is FRAME bytes."""
        if not self.buf:
            return []
        frame = bytes(self.buf) + b"\0" * (FRAME - len(self.buf))
        self.buf.clear()
        return [frame]


def fix_wav(data: bytes) -> bytes:
    """Gnani WAVs may carry 0xFFFFFFFF sizes; rewrite RIFF and data sizes from the real length."""
    if len(data) < 12 or data[:4] != b"RIFF" or data[8:12] != b"WAVE":
        return data
    b = bytearray(data)
    struct.pack_into("<I", b, 4, len(b) - 8)
    pos = 12
    while pos + 8 <= len(b):
        cid, size = b[pos:pos + 4], struct.unpack_from("<I", b, pos + 4)[0]
        if cid == b"data":
            struct.pack_into("<I", b, pos + 4, len(b) - pos - 8)
            break
        pos += 8 + size + (size & 1)
    return bytes(b)


def wav_pcm(data: bytes) -> tuple[int, bytes]:
    with wave.open(io.BytesIO(fix_wav(data))) as w:
        return w.getframerate(), w.readframes(w.getnframes())


def pcm_to_wav(pcm: bytes, rate: int = 16000) -> bytes:
    out = io.BytesIO()
    with wave.open(out, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm)
    return out.getvalue()


async def stt_connect(key: str, mode: str, regional: str = ""):
    return await websockets.connect(STT_WS, open_timeout=6, max_size=None, additional_headers={
        "x-api-key-id": key, "language_code": stt_language(mode, regional), "model": "prisma-v3.0",
        "x-sample-rate": "16000", "x-min-silence-ms": "400"})


async def stt_rest(key: str, wav: bytes, mode: str, regional: str = "") -> dict:
    async with httpx.AsyncClient(timeout=20) as c:
        r = await c.post(STT_REST, headers={"X-API-Key-ID": key},
                         data={"language_code": stt_language(mode, regional), "model": "prisma-v3.0"},
                         files={"audio_file": ("speech.wav", wav, "audio/wav")})
    body = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
    if r.status_code != 200 or body.get("success") is False:
        raise GnaniError(f"STT REST {r.status_code}: {str(body)[:200]}")
    return body


def _tts_request(text: str, lang: str, container: str) -> dict:
    return {"text": text, "model": "timbre-v3.0", "voice": "Shivani", "language": CODES.get(lang, "hi-IN"),
            "audio_config": {"container": container, "sample_rate": TTS_RATE, "num_channels": 1,
                             "sample_width": 2, "encoding": "linear_pcm"}}


async def tts_stream(key: str, text: str, lang: str):
    """Yields raw PCM16 chunks at TTS_RATE as they arrive. Closing the generator closes the socket (= cancel)."""
    async with websockets.connect(TTS_WS, open_timeout=6, max_size=None,
                                  additional_headers={"X-API-Key-ID": key}) as ws:
        await ws.send(json.dumps(_tts_request(text, lang, "raw")))
        async for raw in ws:
            m = json.loads(raw)
            if m.get("type") == "audio":
                chunk = (m.get("data") or {}).get("audio") or m.get("audio")
                if chunk:
                    yield base64.b64decode(chunk)
            elif m.get("type") == "complete":
                return
            elif m.get("type") == "error":
                raise GnaniError(m.get("message", "TTS error"))


async def tts_rest(key: str, text: str, lang: str) -> tuple[int, bytes]:
    async with httpx.AsyncClient(timeout=20) as c:
        r = await c.post(TTS_REST, headers={"X-API-Key-ID": key}, json=_tts_request(text, lang, "wav"))
    if r.status_code != 200:
        raise GnaniError(f"TTS REST {r.status_code}: {r.text[:200]}")
    return wav_pcm(r.content)
