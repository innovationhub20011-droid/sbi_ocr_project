import logging
import time

from fastapi import FastAPI, UploadFile, File, Depends, Request
from sqlalchemy.orm import Session
from controllers.pan_controller import get_all_pan 
from controllers.aadhaar_controller import get_all_aadhaar
from db.database import engine, get_db
from models.document_model import Base
from controllers.pan_controller import extract_pan
from controllers.aadhaar_controller import extract_aadhaar
from controllers.passport_controller import extract_passport
from controllers.driving_controller import extract_driving_license
from controllers.voter_controller import extract_voter_id
from controllers.text_documents.handwritten_text_controller import (
    extract_handwritten_text,
    get_all_handwritten_text_ocr,
)
from controllers.text_documents.digital_text_controller import (
    extract_digital_text,
    get_all_digital_text_ocr,
)
from controllers.text_documents.miscellaneous_text_controller import (
    extract_misc_text,
    get_all_miscellaneous_text_ocr,
)
from controllers.account_opening_controller.page1_controller import extract_account_opening_page1
from controllers.account_opening_controller.page2_controller import extract_account_opening_page2

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    force=True,
)
logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger("uvicorn.error")

app = FastAPI(title="SBI OCR Vision API")


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

@app.post("/extract/pan")
async def pan_api(file: UploadFile = File(...)):
    logger.info("Request received on /extract/pan | file=%s", file.filename)
    return await extract_pan(file)

@app.post("/extract/aadhaar")
async def aadhaar_api(file: UploadFile = File(...)):
    logger.info("Request received on /extract/aadhaar | file=%s", file.filename)
    return await extract_aadhaar(file)

@app.post("/extract/passport")
async def passport_api(file: UploadFile = File(...)):
    logger.info("Request received on /extract/passport | file=%s", file.filename)
    return await extract_passport(file)

@app.post("/extract/driving-license")
async def driving_license_api(file: UploadFile = File(...)):
    logger.info("Request received on /extract/driving-license | file=%s", file.filename)
    return await extract_driving_license(file)

@app.post("/extract/voter-id")
async def voter_id_api(file: UploadFile = File(...)):
    logger.info("Request received on /extract/voter-id | file=%s", file.filename)
    return await extract_voter_id(file)

@app.post("/extract/text/handwritten_text")
async def handwritten_text_api(file: UploadFile = File(...)):
    logger.info("Request received on /extract/text/handwritten_text | file=%s", file.filename)
    return await extract_handwritten_text(file)


@app.post("/extract/text/digital_text")
async def digital_text_api(file: UploadFile = File(...)):
    logger.info("Request received on /extract/text/digital_text | file=%s", file.filename)
    return await extract_digital_text(file)


@app.post("/extract/text/miscellaneous_text")
async def misc_text_api(file: UploadFile = File(...)):
    logger.info("Request received on /extract/text/miscellaneous_text | file=%s", file.filename)
    return await extract_misc_text(file)

@app.post("/extract/account-opening/page1")
async def account_opening_page1_api(file: UploadFile = File(...), db: Session = Depends(get_db)):
    logger.info("Request received on /extract/account-opening/page1 | file=%s", file.filename)
    return await extract_account_opening_page1(file, db)

@app.post("/extract/account-opening/page2")
async def account_opening_page2_api(file: UploadFile = File(...)):
    logger.info("Request received on /extract/account-opening/page2 | file=%s", file.filename)
    return await extract_account_opening_page2(file)

@app.get("/retrieve/pan/all")
async def retrieve_all_pan():
    logger.info("Request received on /retrieve/pan/all")
    return get_all_pan()

@app.get("/retrieve/aadhaar/all")
async def retrieve_all_aadhaar():
    logger.info("Request received on /retrieve/aadhaar/all")
    return get_all_aadhaar()


@app.get("/retrieve/text/handwritten_text/all")
async def retrieve_all_handwritten_text():
    logger.info("Request received on /retrieve/text/handwritten_text/all")
    return get_all_handwritten_text_ocr()


@app.get("/retrieve/text/digital_text/all")
async def retrieve_all_digital_text():
    logger.info("Request received on /retrieve/text/digital_text/all")
    return get_all_digital_text_ocr()


@app.get("/retrieve/text/miscellaneous_text/all")
async def retrieve_all_miscellaneous_text():
    logger.info("Request received on /retrieve/text/miscellaneous_text/all")
    return get_all_miscellaneous_text_ocr()