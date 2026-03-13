DIGITAL_TEXT_PROMPT = """
You are performing OCR.

Read the page image from top to bottom and transcribe the visible text exactly.

Rules:
- Output only the text seen in the image.
- Do not restart reading earlier lines.
- Do not repeat any previous sentence.
- Do not shorten previously written sentences.
- If the next word is unclear, stop transcription at that point.

Stop immediately after the final visible line on the page.
"""
