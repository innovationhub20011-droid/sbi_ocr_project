HANDWRITTEN_TEXT_PROMPT = """
Perform OCR on the handwritten page.

Rules:
- Output plain text only.
- Do not output markdown.
- Do not output code blocks.
- If no readable handwritten text is detected, return an empty string.

Read the page from top to bottom and copy visible handwritten text exactly.

Stop after the last visible text.

Return only the transcription.
"""