import base64
from functools import lru_cache
from typing import Optional, Union

import cv2
import numpy as np
from ultralytics import YOLO

@lru_cache(maxsize=1)
def get_face_model(model_path: str = "weights/yolov8n-face.pt") -> YOLO:
    """Load and cache the face detection model."""
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


def detect_first_face(
    image_base64: str,
    model_path: str = "weights/yolov8n-face.pt",
    padding_ratio: float = 0.25,
) -> Optional[np.ndarray]:
    """
    Detect and return the first face crop from an image.

    Returns:
        A cropped face as a NumPy array, or None if no face is found.
    """
    img = _decode_base64_image(image_base64)
    model = get_face_model(model_path)

    results = model.predict(source=img, verbose=False)

    for result in results:
        boxes = result.boxes
        if boxes is None or len(boxes) == 0:
            continue

        box = boxes[0]
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

        width = x2 - x1
        height = y2 - y1
        padding_x = int(width * padding_ratio)
        padding_y = int(height * padding_ratio)

        x1 = max(0, x1 - padding_x)
        y1 = max(0, y1 - padding_y)
        x2 = min(img.shape[1], x2 + padding_x)
        y2 = min(img.shape[0], y2 + padding_y)

        face = img[y1:y2, x1:x2]
        if face.size != 0:
            return face

    return None


def face_to_data_url(face: np.ndarray, image_format: str = "jpg") -> str:
    """Encode a face crop as a data URL for HTTP responses."""
    success, encoded = cv2.imencode(f".{image_format.lstrip('.')}", face)
    if not success:
        raise ValueError("Failed to encode face image")

    mime_type = "jpeg" if image_format.lower().lstrip(".") in {"jpg", "jpeg"} else image_format.lower().lstrip(".")
    base64_data = base64.b64encode(encoded.tobytes()).decode("utf-8")
    return f"data:image/{mime_type};base64,{base64_data}"
