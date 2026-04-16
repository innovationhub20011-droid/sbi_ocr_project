import base64
from io import BytesIO

from PIL import Image


def pil_image_to_base64(image: Image.Image) -> str:
    buffer = BytesIO()
    image.convert("RGB").save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def clean_ocr_text(raw_text: str) -> str:
    """Collapse model repetition loops while preserving normal paragraph flow."""
    if not raw_text:
        return ""

    cleaned_lines = []
    prev_non_empty = None
    consecutive_repeat_count = 0
    repetitive_short_line_streak = 0
    repeated_dot_streak = 0
    saw_blank = False

    for line in raw_text.splitlines():
        current = line.strip()

        if not current:
            saw_blank = True
            continue

        normalized = current.lower()

        if normalized in {"...", ". . ."}:
            repeated_dot_streak += 1
            if repeated_dot_streak >= 2:
                break
        else:
            repeated_dot_streak = 0

        if normalized == prev_non_empty:
            consecutive_repeat_count += 1
        else:
            consecutive_repeat_count = 0

        if consecutive_repeat_count > 0:
            continue

        token_count = len(current.split())
        if token_count <= 2 and len(current) <= 6:
            repetitive_short_line_streak += 1
        else:
            repetitive_short_line_streak = 0

        if repetitive_short_line_streak >= 8:
            break

        if saw_blank and cleaned_lines:
            cleaned_lines.append("")

        cleaned_lines.append(current)
        prev_non_empty = normalized
        saw_blank = False

    return "\n".join(cleaned_lines).strip()
