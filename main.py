import logging
import time

from fastapi import FastAPI, Request
from db.database import engine
from models.document_model import Base
from routers.account_opening_router import router as account_opening_router
from routers.ovd_router import router as ovd_router
from routers.text_documents_router import router as text_documents_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    force=True,
)
logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger("uvicorn.error")

app = FastAPI(title="SBI OCR Vision API")
app.include_router(ovd_router)
app.include_router(account_opening_router)
app.include_router(text_documents_router)


@app.middleware("http")
async def log_http_requests(request: Request, call_next):
    started_at = time.perf_counter()
    logger.info("HTTP request started | method=%s path=%s", request.method, request.url.path)
    try:
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - started_at) * 1000
        logger.info(
            "HTTP request completed | method=%s path=%s status=%s duration_ms=%.2f",
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
        )
        return response
    except Exception:
        elapsed_ms = (time.perf_counter() - started_at) * 1000
        logger.exception(
            "HTTP request failed | method=%s path=%s duration_ms=%.2f",
            request.method,
            request.url.path,
            elapsed_ms,
        )
        raise

@app.on_event("startup")
async def startup_event():
    logger.info("Logger smoke check: application startup initialized")
    Base.metadata.create_all(bind=engine)
