import logging

from fastapi import APIRouter, File, UploadFile

from controllers.account_opening_controller.page1_controller import extract_account_opening_page1

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/extract/account-opening/page1")
async def account_opening_page1_api(file: UploadFile = File(...)):
    logger.info("Request received on /extract/account-opening/page1 | file=%s", file.filename)
    return await extract_account_opening_page1(file)
