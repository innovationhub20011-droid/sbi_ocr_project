import base64
from pdf2image import convert_from_bytes

async def convert_image_to_base64(file):
    content = await file.read()
    return base64.b64encode(content).decode("utf-8")

async def convert_pdf_to_images(file):
    content = await file.read()
    images = convert_from_bytes(content)
    return images