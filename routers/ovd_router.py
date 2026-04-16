import logging

from fastapi import APIRouter, File, Query, UploadFile

from controllers.aadhaar_controller import extract_aadhaar, get_all_aadhaar
from controllers.driving_controller import extract_driving_license
from controllers.pan_controller import extract_pan, get_all_pan
from controllers.passport_controller import extract_passport
from controllers.voter_controller import extract_voter_id

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/extract/pan")
async def pan_api(file: UploadFile = File(...), photo: bool = Query(False)):
    logger.info("Request received on /extract/pan | file=%s", file.filename)
    return await extract_pan(file, photo=photo)


@router.post("/extract/aadhaar")
async def aadhaar_api(file: UploadFile = File(...), photo: bool = Query(False)):
    logger.info("Request received on /extract/aadhaar | file=%s", file.filename)
    return await extract_aadhaar(file, photo=photo)


@router.post("/extract/passport")
async def passport_api(file: UploadFile = File(...)):
    logger.info("Request received on /extract/passport | file=%s", file.filename)
    return await extract_passport(file)


@router.post("/extract/driving-license")
async def driving_license_api(file: UploadFile = File(...)):
    logger.info("Request received on /extract/driving-license | file=%s", file.filename)
    return await extract_driving_license(file)


@router.post("/extract/voter-id")
async def voter_id_api(file: UploadFile = File(...)):
    logger.info("Request received on /extract/voter-id | file=%s", file.filename)
    return await extract_voter_id(file)


@router.get("/retrieve/pan/all")
async def retrieve_all_pan():
    logger.info("Request received on /retrieve/pan/all")
    return get_all_pan()


@router.get("/retrieve/aadhaar/all")
async def retrieve_all_aadhaar():
    logger.info("Request received on /retrieve/aadhaar/all")
    return get_all_aadhaar()
