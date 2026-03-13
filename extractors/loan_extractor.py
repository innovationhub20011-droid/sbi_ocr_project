import base64
import logging

from services.file_service import convert_pdf_to_images
from llm.inference import call_vision_model
from services.page_classifier import classify_page
from prompts.loan_page1_prompt import LOAN_PAGE1_PROMPT
from prompts.loan_page2_prompt import LOAN_PAGE2_PROMPT

logger = logging.getLogger(__name__)


async def extract_loan(file):

    if not file.filename.lower().endswith(".pdf"):
        return {"error": "Only PDF allowed for loan forms"}

    images = await convert_pdf_to_images(file)
    total_pages = len(images)
    logger.info("Loan extraction started | file=%s | total_pages=%s", file.filename, total_pages)

    final_output = {}

    for index, img in enumerate(images):
        page_number = index + 1
        logger.info("Starting extraction for page %s/%s", page_number, total_pages)

        buffered = base64.b64encode(img.tobytes()).decode("utf-8")

        # Temporary classifier placeholder
        page_text = "Loan Application"

        page_type = classify_page(page_text)
        logger.info("Classified page %s as %s", page_number, page_type)

        if page_type == "loan_page1":
            response = call_vision_model(LOAN_PAGE1_PROMPT, buffered)
            final_output[f"page_{page_number}"] = response

        elif page_type == "loan_page2":
            response = call_vision_model(LOAN_PAGE2_PROMPT, buffered)
            final_output[f"page_{page_number}"] = response

        else:
            final_output[f"page_{page_number}"] = "Unknown page type"

        if page_number < total_pages:
            logger.info("Extraction completed for page %s, proceeding to page %s", page_number, page_number + 1)
        else:
            logger.info("Extraction completed for page %s, all pages processed", page_number)

    return final_output