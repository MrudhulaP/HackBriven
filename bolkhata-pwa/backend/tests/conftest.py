import base64
import os

os.environ["BOLKHATA_NO_APP"] = "1"
os.environ.setdefault("ENCRYPTION_KEY", base64.urlsafe_b64encode(b"k" * 32).decode())
os.environ["GNANI_API_KEY"] = "test-key"  # Gnani is always mocked; the real API is never called in tests
os.environ["LLM_ENABLED"] = "false"  # LLM providers are mocked too; tests never call Groq or Gemini
for _k in ("GROQ_API_KEY", "GEMINI_API_KEY"):
    os.environ.pop(_k, None)

import mongomock  # noqa: E402
import pytest  # noqa: E402

from app.store import Crypto, Store  # noqa: E402


@pytest.fixture
def db():
    return mongomock.MongoClient().db


@pytest.fixture
def store(db):
    s = Store(db, Crypto(os.environ["ENCRYPTION_KEY"]))
    s.seed_demo()
    return s
