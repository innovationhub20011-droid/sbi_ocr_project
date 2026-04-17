import base64
import logging
from functools import lru_cache
from typing import Optional

import cv2
import numpy as np
from ultralytics import YOLO

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_signature_model(model_path: str = "weights/yolov8s-signature.pt") -> YOLO:
    """Load and cache the signature detection model."""
    return YOLO(model_path)


def _decode_base64_image(image_base64: str) -> np.ndarray:
    payload = image_base64.strip()
    if payload.startswith("data:image/") and "," in payload:
        payload = payload.split(",", 1)[1]

    image_bytes = base64.b64decode(payload)
    buffer = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(buffer, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("Image not loaded. Check the provided base64 input.")

    return img


def detect_first_signature(
    image_base64: str,
    model_path: str = "weights/yolov8s-signature.pt",
    padding_ratio: float = 0.1,
) -> Optional[np.ndarray]:
    """Detect and return the first signature crop from an image."""
    img = _decode_base64_image(image_base64)
    model = get_signature_model(model_path)
    height = img.shape[0]
    midpoint = height // 2
    bottom_half = img[midpoint:, :]
    bottom_half_gray = cv2.cvtColor(bottom_half, cv2.COLOR_BGR2GRAY)
    bottom_half_input = cv2.cvtColor(bottom_half_gray, cv2.COLOR_GRAY2BGR)
    results = model.predict(source=bottom_half_input, verbose=False, conf=0.05, imgsz=1280)

    for result in results:
        boxes = result.boxes
        if boxes is None or len(boxes) == 0:
            logger.info("No signature boxes detected for the provided image")
            continue

        best_idx = int(boxes.conf.argmax().item()) if hasattr(boxes, "conf") else 0
        box = boxes[best_idx]
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

        width = x2 - x1
        height = y2 - y1
        padding_x = int(width * padding_ratio)
        padding_y = int(height * padding_ratio)

        x1 = max(0, x1 - padding_x)
        y1 = max(0, y1 - padding_y)
        x2 = min(bottom_half.shape[1], x2 + padding_x)
        y2 = min(bottom_half.shape[0], y2 + padding_y)

        signature = bottom_half[y1:y2, x1:x2]
        if signature.size != 0:
            return signature

    logger.info("Signature detector returned no crop")
    return None


def signature_to_data_url(signature: np.ndarray, image_format: str = "jpg") -> str:
    """Encode a signature crop as a data URL for HTTP responses."""
    success, encoded = cv2.imencode(f".{image_format.lstrip('.')}", signature)
    if not success:
        raise ValueError("Failed to encode signature image")

    mime_type = "jpeg" if image_format.lower().lstrip(".") in {"jpg", "jpeg"} else image_format.lower().lstrip(".")
    base64_data = base64.b64encode(encoded.tobytes()).decode("utf-8")
    return f"data:image/{mime_type};base64,{base64_data}"
