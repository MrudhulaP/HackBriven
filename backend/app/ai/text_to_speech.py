import base64
from typing import Optional, Dict, Any
from app.core.config import settings

class TextToSpeechService:
    LANG_BCP47_MAP = {
        "hi": "hi-IN",
        "kn": "kn-IN",
        "te": "te-IN",
        "ta": "ta-IN",
        "en": "en-IN"
    }

    @classmethod
    async def synthesize_speech(
        cls,
        text: str,
        language: str = "hi"
    ) -> Dict[str, Any]:
        """
        Multilingual Text-To-Speech Synthesis Service:
        - Integrates with Gnani Streaming TTS when credentials present.
        - Provides BCP-47 directives for browser SpeechSynthesis.
        """
        bcp47 = cls.LANG_BCP47_MAP.get(language, "hi-IN")

        # 1. Gnani Indic Streaming TTS Provider
        if settings.GNANI_API_KEY or settings.GNANI_TOKEN:
            try:
                import httpx
                headers = {
                    "Authorization": f"Bearer {settings.GNANI_API_KEY or settings.GNANI_TOKEN}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "text": text,
                    "language": bcp47,
                    "audio_format": "mp3",
                    "gender": "female"
                }
                async with httpx.AsyncClient(timeout=8.0) as client:
                    resp = await client.post(settings.GNANI_TTS_URL, json=payload, headers=headers)
                    if resp.status_code == 200:
                        audio_b64 = base64.b64encode(resp.content).decode("utf-8")
                        return {
                            "text": text,
                            "language": language,
                            "bcp47": bcp47,
                            "provider": "gnani_streaming_tts",
                            "audio_base64": f"data:audio/mp3;base64,{audio_b64}",
                            "audio_url": None
                        }
            except Exception:
                pass

        # 2. Browser SpeechSynthesis Directive Fallback
        return {
            "text": text,
            "language": language,
            "bcp47": bcp47,
            "provider": "browser_speech_synthesis",
            "audio_base64": None,
            "audio_url": None
        }
