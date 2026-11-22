"""The LLM brain: prompt -> Groq (1.5 s) -> Gemini (2 s) -> parsed result. Any failure returns None."""
import asyncio
import logging
import os
import time

from ..brain.parser import parse_brain_json
from ..brain.prompt import SYSTEM, build_user
from ..brain.types import BrainContext, BrainOutcome
from .llm_client import GeminiClient, GroqClient, LlmClient

log = logging.getLogger("bolkhata.brain")
TIMEOUTS = {"groq": 1.5, "gemini": 2.0}
DEFAULT_GROQ_MODEL = "openai/gpt-oss-120b"  # Groq's production 120B model; llama-3.3-70b is past its shutdown date
DEFAULT_GEMINI_MODEL = "gemini-3.5-flash-lite"  # stable, fast; recommended by Google for new projects


class LlmBrain:
    def __init__(self, clients: list[LlmClient]):
        self.clients = [c for c in clients if c.is_configured]

    async def interpret(self, transcript: str, ctx: BrainContext) -> BrainOutcome | None:
        user = build_user(transcript, ctx)
        for c in self.clients:
            t0 = time.perf_counter()
            try:
                raw = await asyncio.wait_for(c.complete_json(SYSTEM, user, TIMEOUTS.get(c.name, 2.0)),
                                             TIMEOUTS.get(c.name, 2.0))
            except Exception as e:  # noqa: BLE001 - timeout, 429, network: try the next provider
                log.info("brain %s failed: %s", c.name, type(e).__name__)
                continue
            result = parse_brain_json(raw)
            if result is not None:
                return BrainOutcome(result, c.name, round((time.perf_counter() - t0) * 1000))
            log.info("brain %s returned unusable JSON", c.name)
        return None


def build_brain():
    """None when LLM_ENABLED=false or no key is set: the app then runs on rules only, exactly as before."""
    if os.environ.get("LLM_ENABLED", "true").lower() == "false":
        return None
    brain = LlmBrain([
        GroqClient(os.environ.get("GROQ_API_KEY", ""), os.environ.get("GROQ_MODEL") or DEFAULT_GROQ_MODEL),
        GeminiClient(os.environ.get("GEMINI_API_KEY", ""), os.environ.get("GEMINI_MODEL") or DEFAULT_GEMINI_MODEL),
    ])
    return brain if brain.clients else None
