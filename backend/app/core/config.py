import os
from pathlib import Path
from typing import Optional, List

# backend/data/, found from this file so it is the same whatever folder the server starts in.
# Docker mounts this whole folder, so SQLite's -wal/-shm side files are kept too.
_BACKEND_DIR = Path(__file__).resolve().parents[2]
_DATA_DIR = _BACKEND_DIR / "data"
_DATA_DIR.mkdir(exist_ok=True)
# One-time move of a database from the old location (backend/bolkhata.db), side files included.
if not (_DATA_DIR / "bolkhata.db").exists() and (_BACKEND_DIR / "bolkhata.db").is_file():
    for _suffix in ("", "-wal", "-shm"):
        _old = _BACKEND_DIR / f"bolkhata.db{_suffix}"
        if _old.exists():
            _old.rename(_DATA_DIR / _old.name)

class Settings:
    PROJECT_NAME: str = "BolKhata"
    PROJECT_TAGLINE: str = "The Ledger You Talk To"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api"
    
    # Security & On-Device Encryption
    SECRET_KEY: str = os.getenv("SECRET_KEY", "bolkhata-secret-key-kirana-bharat-voice-ai-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    DATABASE_ENCRYPTION_KEY: str = os.getenv("DATABASE_ENCRYPTION_KEY", "bolkhata-sqlcipher-secure-kirana-vault-2026")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{_DATA_DIR / 'bolkhata.db'}")
    USE_SQLCIPHER: bool = os.getenv("USE_SQLCIPHER", "false").lower() in ("true", "1", "yes")
    
    # AI & Speech Configuration
    DEFAULT_LANGUAGE: str = "hi"  # en, hi, kn, te, ta
    SUPPORTED_LANGUAGES: List[str] = ["en", "hi", "kn", "te", "ta"]
    SPEECH_PROVIDER: str = os.getenv("SPEECH_PROVIDER", "hybrid")  # gnani, bhashini, whisper, browser
    
    # Gnani AI Streaming STT & TTS
    GNANI_API_KEY: Optional[str] = os.getenv("GNANI_API_KEY", None)
    GNANI_TOKEN: Optional[str] = os.getenv("GNANI_TOKEN", None)
    GNANI_ASR_URL: str = os.getenv("GNANI_ASR_URL", "https://asr.gnani.ai/v1/stream")
    GNANI_TTS_URL: str = os.getenv("GNANI_TTS_URL", "https://tts.gnani.ai/v1/synthesize")
    
    # Bhashini & OpenAI fallback
    BHASHINI_API_KEY: Optional[str] = os.getenv("BHASHINI_API_KEY", None)
    BHASHINI_USER_ID: Optional[str] = os.getenv("BHASHINI_USER_ID", None)
    BHASHINI_INFERENCE_PIPELINE_ENDPOINT: Optional[str] = os.getenv("BHASHINI_INFERENCE_PIPELINE_ENDPOINT", None)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", None)
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", None)
    
    # Default Currency
    DEFAULT_CURRENCY: str = "INR"

settings = Settings()
