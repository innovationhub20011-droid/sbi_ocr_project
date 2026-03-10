import base64
import logging

from fastapi import HTTPException

import pypdfium2 as pdfium

logger = logging.getLogger(__name__)

async def convert_image_to_base64(file):
    content = await file.read()
    return base64.b64encode(content).decode("utf-8")


async def convert_pdf_to_images(file):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded PDF is empty")

    try:
        pdf = pdfium.PdfDocument(content)
        images = []
        for index in range(len(pdf)):
            page = pdf[index]
            bitmap = page.render(scale=2)
            images.append(bitmap.to_pil())
        pdf.close()
        return images

    except Exception as exc:
        logger.exception("Failed to convert PDF to images with pypdfium2")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process PDF: {str(exc)}",
        )
