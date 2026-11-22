"""LLM providers. Request/response shapes checked against console.groq.com/docs and ai.google.dev (Nov 2026).
Keys come from the backend environment only; they are never logged or sent to the browser."""
import httpx


class LlmError(Exception):
    pass


class LlmClient:
    name = "llm"

    def __init__(self, key: str, model: str, client: httpx.AsyncClient | None = None):
        self.key, self.model = key, model
        self.http = client or httpx.AsyncClient()

    @property
    def is_configured(self) -> bool:
        return bool(self.key and self.model)

    async def complete_json(self, system: str, user: str, timeout: float) -> str:
        raise NotImplementedError


class GroqClient(LlmClient):
    """OpenAI-compatible chat completions with JSON mode."""
    name = "groq"
    URL = "https://api.groq.com/openai/v1/chat/completions"

    async def complete_json(self, system, user, timeout):
        body = {"model": self.model, "temperature": 0, "max_completion_tokens": 400,
                "response_format": {"type": "json_object"},
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
        if self.model.startswith("openai/gpt-oss"):
            body.update(reasoning_effort="low", include_reasoning=False)  # reasoning costs latency
        r = await self.http.post(self.URL, json=body, timeout=timeout,
                                 headers={"Authorization": f"Bearer {self.key}"})
        if r.status_code != 200:
            raise LlmError(f"groq HTTP {r.status_code}")  # 429 = rate limited -> caller falls back
        try:
            return r.json()["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError, ValueError) as e:
            raise LlmError("groq: unexpected response shape") from e


class GeminiClient(LlmClient):
    """generateContent with JSON output. The system prompt goes in the user turn to keep the request minimal."""
    name = "gemini"

    async def complete_json(self, system, user, timeout):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        body = {"contents": [{"role": "user", "parts": [{"text": system + "\n\nInput:\n" + user}]}],
                "generationConfig": {"temperature": 0, "maxOutputTokens": 400, "responseMimeType": "application/json"}}
        r = await self.http.post(url, json=body, timeout=timeout, headers={"x-goog-api-key": self.key})
        if r.status_code != 200:
            raise LlmError(f"gemini HTTP {r.status_code}")
        try:
            parts = r.json()["candidates"][0]["content"]["parts"]
            return "".join(p.get("text", "") for p in parts if not p.get("thought"))
        except (KeyError, IndexError, TypeError, ValueError) as e:
            raise LlmError("gemini: unexpected response shape") from e
