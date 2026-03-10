import logging
import json

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models import document_model
from models.account_opening_models import AccountForm, AccountFormPage
from schemas.document_schemas import (
    PanCreate,
    AadhaarCreate,
    PassportCreate,
    DrivingLicenseCreate,
    VoterIdCreate,
    TextDocumentOcrCreate,
)
from schemas.account_opening_schemas import AccountFormCreate, AccountFormPageCreate

logger = logging.getLogger(__name__)

PanCardDetails = document_model.PanCardDetails
AadhaarCardDetails = document_model.AadhaarCardDetails
PassportDetails = document_model.PassportDetails
DrivingLicenseDetails = document_model.DrivingLicenseDetails
VoterIdDetails = document_model.VoterIdDetails
HandwrittenTextOcrDetails = document_model.HandwrittenTextOcrDetails
DigitalTextOcrDetails = document_model.DigitalTextOcrDetails
MiscellaneousTextOcrDetails = document_model.MiscellaneousTextOcrDetails


# =====================================================
# 🔵 PAN SAVE SERVICE
# =====================================================
def create_pan(
    db: Session,
    pan: PanCreate,
    ocr_source: str = "vision_model",
    created_by: str = "system"
):

    # -----------------------------
    # 1️⃣ Pre-check for duplicate
    # -----------------------------
    existing = db.query(PanCardDetails).filter(
        PanCardDetails.pan_number == pan.pan_number
    ).first()

    if existing:
        logger.warning("PAN %s already exists in database.", pan.pan_number)
        raise HTTPException(
            status_code=400,
            detail="Data for this PAN card already exists in the database."
        )

    # -----------------------------
    # 2️⃣ Create DB Object
    # -----------------------------
    db_pan = PanCardDetails(
        pan_number=pan.pan_number,
        full_name=pan.full_name,
        father_name=pan.father_name,
        date_of_birth=pan.date_of_birth,
        pan_type=pan.derive_pan_type(),
        ocr_source=ocr_source,
        created_by=created_by,
    )

    # -----------------------------
    # 3️⃣ Save to DB
    # -----------------------------
    try:
        db.add(db_pan)
        db.commit()
        db.refresh(db_pan)

        logger.info("PAN %s saved successfully.", pan.pan_number)
        return db_pan

    except IntegrityError:
        db.rollback()
        logger.warning("Integrity error while saving PAN %s", pan.pan_number)
        raise HTTPException(
            status_code=400,
            detail="Data for this PAN card already exists in the database."
        )

    except Exception as exc:
        db.rollback()
        logger.exception("Unexpected error while saving PAN")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save PAN details: {str(exc)}"
        )


# =====================================================
# 🟢 AADHAAR SAVE SERVICE
# =====================================================
def create_aadhaar(
    db: Session,
    aadhaar: AadhaarCreate,
    ocr_source: str = "vision_model",
    created_by: str = "system"
):

    # -----------------------------
    # 1️⃣ Pre-check for duplicate
    # -----------------------------
    existing = db.query(AadhaarCardDetails).filter(
        AadhaarCardDetails.aadhaar_number == aadhaar.aadhaar_number
    ).first()

    if existing:
        logger.warning(
            "Aadhaar %s already exists in database.",
            aadhaar.aadhaar_number
        )
        raise HTTPException(
            status_code=400,
            detail="Data for this Aadhaar card already exists in the database."
        )

    # -----------------------------
    # 2️⃣ Create DB Object
    # -----------------------------
    db_aadhaar = AadhaarCardDetails(
        aadhaar_number=aadhaar.aadhaar_number,
        full_name=aadhaar.full_name,
        date_of_birth=aadhaar.date_of_birth,
        gender=aadhaar.gender,
        address=aadhaar.address,
        ocr_source=ocr_source,
        created_by=created_by,
    )

    # -----------------------------
    # 3️⃣ Save to DB
    # -----------------------------
    try:
        db.add(db_aadhaar)
        db.commit()
        db.refresh(db_aadhaar)

        logger.info(
            "Aadhaar %s saved successfully.",
            aadhaar.aadhaar_number
        )
        return db_aadhaar

    except IntegrityError:
        db.rollback()
        logger.warning(
            "Integrity error while saving Aadhaar %s",
            aadhaar.aadhaar_number
        )
        raise HTTPException(
            status_code=400,
            detail="Data for this Aadhaar card already exists in the database."
        )

    except Exception as exc:
        db.rollback()
        logger.exception("Unexpected error while saving Aadhaar")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save Aadhaar details: {str(exc)}"
        )


def create_passport(
    db: Session,
    passport: PassportCreate,
    ocr_source: str = "vision_model",
    created_by: str = "system"
):
    passport_number = (passport.passport_number or "").strip() or None

    if passport_number:
        existing = db.query(PassportDetails).filter(
            PassportDetails.passport_number == passport_number
        ).first()
        if existing:
            logger.warning("Passport %s already exists in database.", passport_number)
            raise HTTPException(status_code=400, detail="Data for this passport already exists in the database.")

    db_passport = PassportDetails(
        passport_number=passport_number,
        surname=passport.surname,
        given_names=passport.given_names,
        nationality=passport.nationality,
        sex=passport.sex,
        date_of_birth=passport.date_of_birth,
        place_of_birth=passport.place_of_birth,
        date_of_issue=passport.date_of_issue,
        date_of_expiry=passport.date_of_expiry,
        place_of_issue=passport.place_of_issue,
        father_name=passport.father_name,
        mother_name=passport.mother_name,
        address=passport.address,
        pin_code=passport.pin_code,
        file_number=passport.file_number,
        ocr_source=ocr_source,
        created_by=created_by,
    )

    try:
        db.add(db_passport)
        db.commit()
        db.refresh(db_passport)
        return db_passport
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Data for this passport already exists in the database.")
    except Exception as exc:
        db.rollback()
        logger.exception("Unexpected error while saving passport")
        raise HTTPException(status_code=500, detail=f"Failed to save passport details: {str(exc)}")


def create_driving_license(
    db: Session,
    driving_license: DrivingLicenseCreate,
    ocr_source: str = "vision_model",
    created_by: str = "system"
):
    dl_number = (driving_license.driving_licence_number or "").strip() or None

    if dl_number:
        existing = db.query(DrivingLicenseDetails).filter(
            DrivingLicenseDetails.driving_licence_number == dl_number
        ).first()
        if existing:
            logger.warning(
                "Driving License %s already exists in database.",
                dl_number,
            )
            raise HTTPException(status_code=400, detail="Data for this driving license already exists in the database.")

    db_dl = DrivingLicenseDetails(
        driving_licence_number=dl_number,
        name=driving_license.name,
        father_name=driving_license.father_name,
        date_of_birth=driving_license.date_of_birth,
        date_of_issue=driving_license.date_of_issue,
        valid_till_nt=driving_license.valid_till_nt,
        valid_till_tr=driving_license.valid_till_tr,
        address=driving_license.address,
        blood_group=driving_license.blood_group,
        class_of_vehicle=driving_license.class_of_vehicle,
        issuing_authority=driving_license.issuing_authority,
        ocr_source=ocr_source,
        created_by=created_by,
    )

    try:
        db.add(db_dl)
        db.commit()
        db.refresh(db_dl)
        return db_dl
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Data for this driving license already exists in the database.")
    except Exception as exc:
        db.rollback()
        logger.exception("Unexpected error while saving driving license")
        raise HTTPException(status_code=500, detail=f"Failed to save driving license details: {str(exc)}")


def create_voter_id(
    db: Session,
    voter_id: VoterIdCreate,
    ocr_source: str = "vision_model",
    created_by: str = "system"
):
    epic_number = (voter_id.epic_number or "").strip() or None

    if epic_number:
        existing = db.query(VoterIdDetails).filter(
            VoterIdDetails.epic_number == epic_number
        ).first()
        if existing:
            logger.warning("Voter EPIC %s already exists in database.", epic_number)
            raise HTTPException(status_code=400, detail="Data for this voter ID already exists in the database.")

    db_voter = VoterIdDetails(
        epic_number=epic_number,
        name=voter_id.name,
        father_name=voter_id.father_name,
        gender=voter_id.gender,
        date_of_birth=voter_id.date_of_birth,
        address=voter_id.address,
        electoral_registration_officer=voter_id.electoral_registration_officer,
        assembly_constituency=voter_id.assembly_constituency,
        download_date=voter_id.download_date,
        ocr_source=ocr_source,
        created_by=created_by,
    )

    try:
        db.add(db_voter)
        db.commit()
        db.refresh(db_voter)
        return db_voter
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Data for this voter ID already exists in the database.")
    except Exception as exc:
        db.rollback()
        logger.exception("Unexpected error while saving voter ID")
        raise HTTPException(status_code=500, detail=f"Failed to save voter ID details: {str(exc)}")
        


def _save_text_document_ocr(
    db: Session,
    ocr_data: TextDocumentOcrCreate,
    model_cls,
    document_type_label: str,
    created_by: str = "system"
):
    db_record = model_cls(
        document_type=document_type_label,
        file_name=ocr_data.file_name,
        ocr_result=json.dumps(ocr_data.ocr_result, ensure_ascii=True),
        total_pages=ocr_data.total_pages,
        ocr_source=ocr_data.ocr_source,
        created_by=created_by,
    )

    try:
        db.add(db_record)
        db.flush()
        return db_record

    except Exception as exc:
        logger.exception("Unexpected error while saving text document OCR")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save text document OCR: {str(exc)}"
        )


def create_handwritten_text_ocr(db: Session, ocr_data: TextDocumentOcrCreate, created_by: str = "system"):
    return _save_text_document_ocr(
        db,
        ocr_data,
        HandwrittenTextOcrDetails,
        "Handwritten Text Document",
        created_by,
    )


def create_digital_text_ocr(db: Session, ocr_data: TextDocumentOcrCreate, created_by: str = "system"):
    return _save_text_document_ocr(
        db,
        ocr_data,
        DigitalTextOcrDetails,
        "Digital Text Document",
        created_by,
    )


def create_miscellaneous_text_ocr(db: Session, ocr_data: TextDocumentOcrCreate, created_by: str = "system"):
    return _save_text_document_ocr(
        db,
        ocr_data,
        MiscellaneousTextOcrDetails,
        "Miscellaneous Text Documents",
        created_by,
    )


def _serialize_ocr_records(records):
    serialized = []
    for record in records:
        item = {
            "id": record.id,
            "document_type": record.document_type,
            "file_name": record.file_name,
            "ocr_result": json.loads(record.ocr_result) if record.ocr_result else {},
            "total_pages": record.total_pages,
            "ocr_source": record.ocr_source,
            "is_verified": record.is_verified,
            "verified_by": record.verified_by,
            "verified_date": record.verified_date,
            "created_by": record.created_by,
            "created_date": record.created_date,
            "updated_by": record.updated_by,
            "updated_date": record.updated_date,
        }
        serialized.append(item)
    return serialized


def retrieve_all_handwritten_text_ocr(db: Session):
    records = db.query(HandwrittenTextOcrDetails).order_by(HandwrittenTextOcrDetails.id.desc()).all()
    return _serialize_ocr_records(records)


def retrieve_all_digital_text_ocr(db: Session):
    records = db.query(DigitalTextOcrDetails).order_by(DigitalTextOcrDetails.id.desc()).all()
    return _serialize_ocr_records(records)


def retrieve_all_miscellaneous_text_ocr(db: Session):
    records = db.query(MiscellaneousTextOcrDetails).order_by(MiscellaneousTextOcrDetails.id.desc()).all()
    return _serialize_ocr_records(records)


# =====================================================
# 🟡 ACCOUNT FORM SAVE SERVICE
# =====================================================
def create_account_form(
    db: Session,
    account_form: AccountFormCreate,
    created_by: str = "system"
):
    """
    Create a new account opening form entry.
    Returns the created form with its UUID.
    """
    # -----------------------------
    # 1️⃣ Create DB Object
    # -----------------------------
    db_form = AccountForm(
        branch_code=account_form.branch_code,
        account_number=account_form.account_number,
        customer_name=account_form.customer_name,
        pan_number=account_form.pan_number,
        mobile_number=account_form.mobile_number,
        form_status=account_form.form_status,
        created_by=created_by,
    )

    # -----------------------------
    # 3️⃣ Save to DB
    # -----------------------------
    try:
        db.add(db_form)
        db.commit()
        db.refresh(db_form)

        logger.info("Account form saved successfully with ID %s.", db_form.id)
        return db_form

    except IntegrityError:
        db.rollback()
        logger.warning("Integrity error while saving account form")
        raise HTTPException(
            status_code=400,
            detail="Failed to save account form due to duplicate entry."
        )

    except Exception as exc:
        db.rollback()
        logger.exception("Unexpected error while saving account form")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save account form: {str(exc)}"
        )


# =====================================================
# 🟡 ACCOUNT FORM PAGE SAVE SERVICE
# =====================================================
def create_account_form_page(
    db: Session,
    form_page: AccountFormPageCreate,
    created_by: str = "system"
):
    """
    Create a new account form page entry.
    Checks that the form_id exists and page_number is unique for that form.
    """
    # -----------------------------
    # 1️⃣ Check if form exists
    # -----------------------------
    form_exists = db.query(AccountForm).filter(
        AccountForm.id == form_page.form_id
    ).first()

    if not form_exists:
        logger.warning("Form ID %s does not exist.", form_page.form_id)
        raise HTTPException(
            status_code=404,
            detail="Account form not found."
        )

    # -----------------------------
    # 2️⃣ Pre-check for duplicate page_number
    # -----------------------------
    existing_page = db.query(AccountFormPage).filter(
        AccountFormPage.form_id == form_page.form_id,
        AccountFormPage.page_number == form_page.page_number
    ).first()

    if existing_page:
        logger.warning(
            "Page %s for form %s already exists.",
            form_page.page_number, form_page.form_id
        )
        raise HTTPException(
            status_code=400,
            detail=f"Page {form_page.page_number} already exists for this form."
        )

    # -----------------------------
    # 3️⃣ Create DB Object
    # -----------------------------
    db_page = AccountFormPage(
        form_id=form_page.form_id,
        page_number=form_page.page_number,
        page_data=form_page.page_data,
        created_by=created_by,
    )

    # -----------------------------
    # 4️⃣ Save to DB
    # -----------------------------
    try:
        db.add(db_page)
        db.commit()
        db.refresh(db_page)

        logger.info(
            "Page %s saved successfully for form %s.",
            form_page.page_number, form_page.form_id
        )
        return db_page

    except IntegrityError:
        db.rollback()
        logger.warning("Integrity error while saving form page")
        raise HTTPException(
            status_code=400,
            detail="Failed to save form page due to duplicate entry."
        )

    except Exception as exc:
        db.rollback()
        logger.exception("Unexpected error while saving form page")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save form page: {str(exc)}"
        )