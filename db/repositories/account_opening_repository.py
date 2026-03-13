import logging

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.account_opening_models import AccountForm, AccountFormPage
from schemas.account_opening_schemas import AccountFormCreate, AccountFormPageCreate

logger = logging.getLogger(__name__)


def create_account_form(
    db: Session,
    account_form: AccountFormCreate,
    created_by: str = "system",
):
    db_form = AccountForm(
        branch_code=account_form.branch_code,
        account_number=account_form.account_number,
        customer_name=account_form.customer_name,
        pan_number=account_form.pan_number,
        mobile_number=account_form.mobile_number,
        form_status=account_form.form_status,
        created_by=created_by,
    )

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
            detail="Failed to save account form due to duplicate entry.",
        )
    except Exception as exc:
        db.rollback()
        logger.exception("Unexpected error while saving account form")
        raise HTTPException(status_code=500, detail=f"Failed to save account form: {str(exc)}")


def create_account_form_page(
    db: Session,
    form_page: AccountFormPageCreate,
    created_by: str = "system",
):
    form_exists = db.query(AccountForm).filter(AccountForm.id == form_page.form_id).first()
    if not form_exists:
        logger.warning("Form ID %s does not exist.", form_page.form_id)
        raise HTTPException(status_code=404, detail="Account form not found.")

    existing_page = db.query(AccountFormPage).filter(
        AccountFormPage.form_id == form_page.form_id,
        AccountFormPage.page_number == form_page.page_number,
    ).first()

    if existing_page:
        logger.warning("Page %s for form %s already exists.", form_page.page_number, form_page.form_id)
        raise HTTPException(
            status_code=400,
            detail=f"Page {form_page.page_number} already exists for this form.",
        )

    db_page = AccountFormPage(
        form_id=form_page.form_id,
        page_number=form_page.page_number,
        page_data=form_page.page_data,
        created_by=created_by,
    )

    try:
        db.add(db_page)
        db.commit()
        db.refresh(db_page)
        logger.info("Page %s saved successfully for form %s.", form_page.page_number, form_page.form_id)
        return db_page
    except IntegrityError:
        db.rollback()
        logger.warning("Integrity error while saving form page")
        raise HTTPException(
            status_code=400,
            detail="Failed to save form page due to duplicate entry.",
        )
    except Exception as exc:
        db.rollback()
        logger.exception("Unexpected error while saving form page")
        raise HTTPException(status_code=500, detail=f"Failed to save form page: {str(exc)}")
