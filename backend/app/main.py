from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.session import Base, engine, get_db, SessionLocal
from app.database.seed import seed_demo_data
from app.api import auth, customers, transactions, voice, assistant, reports, sync, receipt

# Initialize database schema
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Voice AI for Bharat – Financial Record-Keeping for Informal Retail (Kirana Dukaan).",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    db = SessionLocal()
    try:
        seed_demo_data(db, reset=False)
    finally:
        db.close()

# Include API Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(customers.router, prefix=settings.API_V1_STR)
app.include_router(transactions.router, prefix=settings.API_V1_STR)
app.include_router(voice.router, prefix=settings.API_V1_STR)
app.include_router(assistant.router, prefix=settings.API_V1_STR)
app.include_router(reports.router, prefix=settings.API_V1_STR)
app.include_router(sync.router, prefix=settings.API_V1_STR)
app.include_router(receipt.router, prefix=settings.API_V1_STR)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app": settings.PROJECT_NAME,
        "tagline": settings.PROJECT_TAGLINE,
        "version": settings.VERSION,
        "encryption": "SQLCipher-compatible encrypted SQLite",
        "supported_languages": ["en", "hi", "kn", "te", "ta"]
    }

@app.post("/api/seed/reset")
def reset_seed_data(db: Session = Depends(get_db)):
    """Reset the demo database to the initial clean condition."""
    seed_demo_data(db, reset=True)
    return {"message": "Demo data successfully reset to initial clean state"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
