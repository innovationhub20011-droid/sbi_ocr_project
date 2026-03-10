from fastapi import FastAPI, UploadFile, File, Depends
from sqlalchemy.orm import Session
from controllers.pan_controller import get_all_pan 
from controllers.aadhar_controller import get_all_aadhaar
from db.database import engine, get_db
from models.document_model import Base
from controllers.pan_controller import extract_pan
from controllers.aadhar_controller import extract_aadhaar
from extractors.loan_extractor import extract_loan
from extractors.passport_extractor import extract_passport
from extractors.driving_extractor import extract_driving_license
from extractors.voter_extractor import extract_voter_id
from extractors.text_documents_extractor import (
    extract_handwritten_text,
    extract_digital_text,
    extract_misc_text,
    get_all_handwritten_text_ocr,
    get_all_digital_text_ocr,
    get_all_miscellaneous_text_ocr,
)
from controllers.account_opening_controller.page1_controller import extract_account_opening_page1
from controllers.account_opening_controller.page2_controller import extract_account_opening_page2

app = FastAPI(title="SBI OCR Vision API")

@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)

@app.post("/extract/pan")
async def pan_api(file: UploadFile = File(...)):
    print("Received PAN extraction request", file.filename)
    return await extract_pan(file)

@app.post("/extract/aadhaar")
async def aadhaar_api(file: UploadFile = File(...)):
    print("Received Aadhaar extraction request", file.filename)
    return await extract_aadhaar(file)

@app.post("/extract/loan")
async def loan_api(file: UploadFile = File(...)):
    print("Received Loan extraction request", file.filename)
    return await extract_loan(file)

@app.post("/extract/passport")
async def passport_api(file: UploadFile = File(...)):
    print("Received Passport extraction request", file.filename)
    return await extract_passport(file)

@app.post("/extract/driving-license")
async def driving_license_api(file: UploadFile = File(...)):
    print("Received Driving License extraction request", file.filename)
    return await extract_driving_license(file)

@app.post("/extract/voter-id")
async def voter_id_api(file: UploadFile = File(...)):
    return await extract_voter_id(file)

@app.post("/extract/text/handwritten_text")
async def handwritten_text_api(file: UploadFile = File(...)):
    return await extract_handwritten_text(file)


@app.post("/extract/text/digital_text")
async def digital_text_api(file: UploadFile = File(...)):
    return await extract_digital_text(file)


@app.post("/extract/text/miscellaneous_text")
async def misc_text_api(file: UploadFile = File(...)):
    return await extract_misc_text(file)

@app.post("/extract/account-opening/page1")
async def account_opening_page1_api(file: UploadFile = File(...), db: Session = Depends(get_db)):
    return await extract_account_opening_page1(file, db)

@app.post("/extract/account-opening/page2")
async def account_opening_page2_api(file: UploadFile = File(...)):
    return await extract_account_opening_page2(file)

@app.get("/retrieve/pan/all")
async def retrieve_all_pan():
    return get_all_pan()

@app.get("/retrieve/aadhaar/all")
async def retrieve_all_aadhaar():
   return get_all_aadhaar()


@app.get("/retrieve/text/handwritten_text/all")
async def retrieve_all_handwritten_text():
    return get_all_handwritten_text_ocr()


@app.get("/retrieve/text/digital_text/all")
async def retrieve_all_digital_text():
    return get_all_digital_text_ocr()


@app.get("/retrieve/text/miscellaneous_text/all")
async def retrieve_all_miscellaneous_text():
    return get_all_miscellaneous_text_ocr()