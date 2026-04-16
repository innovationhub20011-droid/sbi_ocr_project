import logging

from fastapi import APIRouter, File, UploadFile

from controllers.text_documents.digital_text_controller import (
    extract_digital_text,
    get_all_digital_text_ocr,
)
from controllers.text_documents.handwritten_text_controller import (
    extract_handwritten_text,
    get_all_handwritten_text_ocr,
)
from controllers.text_documents.miscellaneous_text_controller import (
    extract_misc_text,
    get_all_miscellaneous_text_ocr,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/extract/text/handwritten_text")
async def handwritten_text_api(file: UploadFile = File(...)):
    logger.info("Request received on /extract/text/handwritten_text | file=%s", file.filename)
    return await extract_handwritten_text(file)


@router.post("/extract/text/digital_text")
async def digital_text_api(file: UploadFile = File(...)):
    logger.info("Request received on /extract/text/digital_text | file=%s", file.filename)
    return await extract_digital_text(file)


@router.post("/extract/text/miscellaneous_text")
async def misc_text_api(file: UploadFile = File(...)):
    logger.info("Request received on /extract/text/miscellaneous_text | file=%s", file.filename)
    return await extract_misc_text(file)


@router.get("/retrieve/text/handwritten_text/all")
async def retrieve_all_handwritten_text():
    logger.info("Request received on /retrieve/text/handwritten_text/all")
    return get_all_handwritten_text_ocr()


@router.get("/retrieve/text/digital_text/all")
async def retrieve_all_digital_text():
    logger.info("Request received on /retrieve/text/digital_text/all")
    return get_all_digital_text_ocr()


@router.get("/retrieve/text/miscellaneous_text/all")
async def retrieve_all_miscellaneous_text():
    logger.info("Request received on /retrieve/text/miscellaneous_text/all")
    return get_all_miscellaneous_text_ocr()
