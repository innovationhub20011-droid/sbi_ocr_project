import os
import logging
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent

data_dir = BASE_DIR / "data"
data_dir.mkdir(parents=True, exist_ok=True)

DATABASE_URL = os.getenv(
    "OCR_DB_PATH",
    f"sqlite:///{(data_dir / 'ocr_records.db').resolve()}"
)

logger.info("Using DB: %s", DATABASE_URL)

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}  # Important for FastAPI + SQLite
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
