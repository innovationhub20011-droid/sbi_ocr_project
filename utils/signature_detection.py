import base64
import logging
from functools import lru_cache
from typing import Optional

import cv2
import numpy as np
from ultralytics import YOLO

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_signature_model(model_path: str = "weights/detector_yolo_4cls.pt") -> YOLO:
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
    model_path: str = "weights/detector_yolo_4cls.pt",
) -> Optional[np.ndarray]:
    """Detect and return the first signature crop from an image."""
    img = _decode_base64_image(image_base64)
    model = get_signature_model(model_path)
    height = img.shape[0]
    midpoint = height // 2
    bottom_half = img[midpoint:, :]
    results = model.predict(source=bottom_half, verbose=False, conf=0.1)

    for result in results:
        boxes = result.boxes
        if boxes is None or len(boxes) == 0:
            logger.info("No signature boxes detected for the provided image")
            continue

        signature_boxes = []
        names = getattr(result, "names", None) or getattr(model, "names", {})

        for box in boxes:
            class_id = int(box.cls.item())
            if isinstance(names, dict):
                class_name = names.get(class_id, str(class_id))
            elif isinstance(names, (list, tuple)) and 0 <= class_id < len(names):
                class_name = names[class_id]
            else:
                class_name = str(class_id)
            if class_name.lower() == "signature":
                signature_boxes.append(box)

        if not signature_boxes:
            logger.info("No signature boxes detected for the provided image")
            continue

        best_box = max(signature_boxes, key=lambda b: float(b.conf.item()))
        x1, y1, x2, y2 = map(int, best_box.xyxy[0].tolist())
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(bottom_half.shape[1], x2)
        y2 = min(bottom_half.shape[0], y2)

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
