import os
from typing import Optional

class Settings:
    PROJECT_NAME: str = "BolKhata"
    PROJECT_TAGLINE: str = "The Ledger You Talk To"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "bolkhata-secret-key-kirana-bharat-voice-ai-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./bolkhata.db")
    
    # AI & Speech Configuration
    DEFAULT_LANGUAGE: str = "hi"  # hi, kn, en
    SPEECH_PROVIDER: str = os.getenv("SPEECH_PROVIDER", "hybrid")
    BHASHINI_API_KEY: Optional[str] = os.getenv("BHASHINI_API_KEY", None)
    BHASHINI_USER_ID: Optional[str] = os.getenv("BHASHINI_USER_ID", None)
    BHASHINI_INFERENCE_PIPELINE_ENDPOINT: Optional[str] = os.getenv("BHASHINI_INFERENCE_PIPELINE_ENDPOINT", None)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", None)
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", None)
    
    # Default Currency
    DEFAULT_CURRENCY: str = "INR"

settings = Settings()
