import base64
from services.file_service import convert_pdf_to_images
from utils.vision_utils import call_vision_model
from services.page_classifier import classify_page
from prompts.loan_page1_prompt import LOAN_PAGE1_PROMPT
from prompts.loan_page2_prompt import LOAN_PAGE2_PROMPT

#added test comment.
async def extract_loan(file):

    if not file.filename.lower().endswith(".pdf"):
        return {"error": "Only PDF allowed for loan forms"}

    images = await convert_pdf_to_images(file)

    final_output = {}

    for index, img in enumerate(images):

        buffered = base64.b64encode(img.tobytes()).decode("utf-8")

        # Temporary classifier placeholder
        page_text = "Loan Application"

        page_type = classify_page(page_text)

        if page_type == "loan_page1":
            response = call_vision_model(LOAN_PAGE1_PROMPT, buffered)
            final_output[f"page_{index+1}"] = response

        elif page_type == "loan_page2":
            response = call_vision_model(LOAN_PAGE2_PROMPT, buffered)
            final_output[f"page_{index+1}"] = response

        else:
            final_output[f"page_{index+1}"] = "Unknown page type"

    return final_output