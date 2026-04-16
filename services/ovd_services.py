from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from db.database import SessionLocal
from models.document_model import (
    AadhaarCardDetails,
    DrivingLicenseDetails,
    PanCardDetails,
    PassportDetails,
    VoterIdDetails,
)
from schemas.document_schemas import (
    AadhaarCreate,
    DrivingLicenseCreate,
    PanCreate,
    PassportCreate,
    VoterIdCreate,
)


def _serialize_record(record) -> dict:
    return {key: value for key, value in record.__dict__.items() if not key.startswith("_")}


def _open_session():
    return SessionLocal()


def _save_with_duplicate_warning(db, instance, duplicate_query, duplicate_message: str):
    existing = duplicate_query()
    if existing:
        return {
            "record": existing,
            "saved": False,
            "warning": duplicate_message,
        }

    try:
        db.add(instance)
        db.commit()
        db.refresh(instance)
        return {"record": instance, "saved": True, "warning": None}
    except IntegrityError:
        db.rollback()
        existing = duplicate_query()
        return {
            "record": existing,
            "saved": False,
            "warning": duplicate_message,
        }
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save details: {str(exc)}")


def _extract_pan_value(field):
    if isinstance(field, dict):
        value = field.get("value", "")
        return value if value is not None else ""
    return field if field is not None else ""


def save_pan_details(data: dict):
    pan = PanCreate(
        pan_number=_extract_pan_value(data.get("pan_number")),
        full_name=_extract_pan_value(data.get("full_name")),
        father_name=_extract_pan_value(data.get("father_name")),
        date_of_birth=_extract_pan_value(data.get("date_of_birth")),
    )

    db = _open_session()
    try:
        db_pan = PanCardDetails(
            pan_number=pan.pan_number,
            full_name=pan.full_name,
            father_name=pan.father_name,
            date_of_birth=pan.date_of_birth,
            pan_type=pan.derive_pan_type(),
            ocr_source="vision_model",
            created_by="system",
        )

        return _save_with_duplicate_warning(
            db=db,
            instance=db_pan,
            duplicate_query=lambda: db.query(PanCardDetails).filter(
                PanCardDetails.pan_number == pan.pan_number
            ).first(),
            duplicate_message="Data for this PAN card already exists in the database.",
        )
    finally:
        db.close()


def save_aadhaar_details(data: dict):
    aadhaar = AadhaarCreate(**data)

    db = _open_session()
    try:
        db_aadhaar = AadhaarCardDetails(
            aadhaar_number=aadhaar.aadhaar_number,
            full_name=aadhaar.full_name,
            date_of_birth=aadhaar.date_of_birth,
            gender=aadhaar.gender,
            address=aadhaar.address,
            ocr_source="vision_model",
            created_by="system",
        )

        return _save_with_duplicate_warning(
            db=db,
            instance=db_aadhaar,
            duplicate_query=lambda: db.query(AadhaarCardDetails).filter(
                AadhaarCardDetails.aadhaar_number == aadhaar.aadhaar_number
            ).first(),
            duplicate_message="Data for this Aadhaar card already exists in the database.",
        )
    finally:
        db.close()


def save_passport_details(data: dict):
    passport = PassportCreate(**data)
    passport_number = (passport.passport_number or "").strip() or None

    db = _open_session()
    try:
        if passport_number:
            existing = db.query(PassportDetails).filter(
                PassportDetails.passport_number == passport_number
            ).first()
            if existing:
                return {
                    "record": existing,
                    "saved": False,
                    "warning": "Data for this passport already exists in the database.",
                }

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
            ocr_source="vision_model",
            created_by="system",
        )

        return _save_with_duplicate_warning(
            db=db,
            instance=db_passport,
            duplicate_query=lambda: db.query(PassportDetails).filter(
                PassportDetails.passport_number == passport_number
            ).first() if passport_number else None,
            duplicate_message="Data for this passport already exists in the database.",
        )
    finally:
        db.close()


def save_driving_license_details(data: dict):
    driving_license = DrivingLicenseCreate(**data)
    dl_number = (driving_license.driving_licence_number or "").strip() or None

    db = _open_session()
    try:
        if dl_number:
            existing = db.query(DrivingLicenseDetails).filter(
                DrivingLicenseDetails.driving_licence_number == dl_number
            ).first()
            if existing:
                return {
                    "record": existing,
                    "saved": False,
                    "warning": "Data for this driving license already exists in the database.",
                }

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
            ocr_source="vision_model",
            created_by="system",
        )

        return _save_with_duplicate_warning(
            db=db,
            instance=db_dl,
            duplicate_query=lambda: db.query(DrivingLicenseDetails).filter(
                DrivingLicenseDetails.driving_licence_number == dl_number
            ).first() if dl_number else None,
            duplicate_message="Data for this driving license already exists in the database.",
        )
    finally:
        db.close()


def save_voter_id_details(data: dict):
    voter_id = VoterIdCreate(**data)
    epic_number = (voter_id.epic_number or "").strip() or None

    db = _open_session()
    try:
        if epic_number:
            existing = db.query(VoterIdDetails).filter(
                VoterIdDetails.epic_number == epic_number
            ).first()
            if existing:
                return {
                    "record": existing,
                    "saved": False,
                    "warning": "Data for this voter ID already exists in the database.",
                }

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
            ocr_source="vision_model",
            created_by="system",
        )

        return _save_with_duplicate_warning(
            db=db,
            instance=db_voter,
            duplicate_query=lambda: db.query(VoterIdDetails).filter(
                VoterIdDetails.epic_number == epic_number
            ).first() if epic_number else None,
            duplicate_message="Data for this voter ID already exists in the database.",
        )
    finally:
        db.close()


def retrieve_pan_details() -> list[dict]:
    db = _open_session()
    try:
        records = db.query(PanCardDetails).all()
        return [_serialize_record(record) for record in records]
    finally:
        db.close()


def retrieve_aadhaar_details() -> list[dict]:
    db = _open_session()
    try:
        records = db.query(AadhaarCardDetails).all()
        return [_serialize_record(record) for record in records]
    finally:
        db.close()
