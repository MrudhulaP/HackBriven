from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# SQLite / SQLCipher configuration requires check_same_thread=False
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

# On-device Encrypted SQLite / SQLCipher Pragma Integration
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    if settings.DATABASE_URL.startswith("sqlite"):
        # Apply SQLCipher encryption key pragma if configured
        if settings.DATABASE_ENCRYPTION_KEY:
            try:
                cursor.execute(f"PRAGMA key = '{settings.DATABASE_ENCRYPTION_KEY}';")
            except Exception:
                pass
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
