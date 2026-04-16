from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from db.database import SessionLocal
from models.account_opening_models import AccountForm, AccountFormPage
from schemas.account_opening_schemas import AccountFormCreate


def _serialize_record(record) -> dict:
    return {key: value for key, value in record.__dict__.items() if not key.startswith("_")}


def _open_session():
    return SessionLocal()


def save_account_opening_page1(form_data: AccountFormCreate, page_number: int, page_data: str):
    db = _open_session()
    try:
        db_form = AccountForm(
            branch_code=form_data.branch_code,
            account_number=form_data.account_number,
            customer_name=form_data.customer_name,
            pan_number=form_data.pan_number,
            mobile_number=form_data.mobile_number,
            form_status=form_data.form_status,
            created_by=form_data.created_by,
        )
        db.add(db_form)
        db.flush()

        db_page = AccountFormPage(
            form_id=db_form.id,
            page_number=page_number,
            page_data=page_data,
            created_by=form_data.created_by,
        )
        db.add(db_page)
        db.commit()
        db.refresh(db_form)
        db.refresh(db_page)
        return {
            "status": "success",
            "form_id": db_form.id,
            "page_number": db_page.page_number,
            "record": {"form": _serialize_record(db_form), "page": _serialize_record(db_page)},
        }
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to save account opening form: {str(exc)}")
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save account opening form: {str(exc)}")
    finally:
        db.close()
