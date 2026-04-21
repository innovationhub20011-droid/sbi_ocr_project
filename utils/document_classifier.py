import logging
from functools import lru_cache
from io import BytesIO
from typing import Tuple, cast

import torch
from PIL import Image
from torchvision import models, transforms

logger = logging.getLogger(__name__)

MODEL_PATH = "weights/document_classifier.pth"
DEFAULT_CLASSES = ["aadhaar", "other", "pan"]
CONFIDENCE_THRESHOLD = 0.8
IMAGE_SIZE = (224, 224)
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]
LABEL_ALIASES = {
    "aadhar": "aadhaar",
    "aadhaar": "aadhaar",
    "pan": "pan",
    "other": "other",
}


def get_device() -> torch.device:
    # Prefer accelerated backends when they are available, fall back to CPU.
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


@lru_cache(maxsize=1)
def get_transform() -> transforms.Compose:
    return transforms.Compose(
        [
            transforms.Resize(IMAGE_SIZE),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ]
    )


@lru_cache(maxsize=1)
def get_document_classifier() -> tuple[torch.nn.Module, dict, torch.device]:
    device = get_device()
    logger.info("Loading document classifier on device=%s", device)

    # Recreate the MobileNetV2 head used during training.
    model = models.mobilenet_v2(weights=None)
    model.classifier[1] = torch.nn.Linear(model.last_channel, 3)

    # Support both plain state_dict checkpoints and wrapped checkpoints.
    checkpoint = torch.load(MODEL_PATH, map_location=device)
    if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
        model.load_state_dict(checkpoint["model_state_dict"])
        class_to_idx = checkpoint.get("class_to_idx", {})
    else:
        model.load_state_dict(checkpoint)
        class_to_idx = {}

    model.to(device)
    model.eval()
    return model, class_to_idx, device


def _resolve_label(pred_idx: int, class_to_idx: dict) -> str:
    if class_to_idx:
        idx_to_class = {idx: cls for cls, idx in class_to_idx.items()}
        return idx_to_class.get(pred_idx, "Unknown")

    if 0 <= pred_idx < len(DEFAULT_CLASSES):
        return DEFAULT_CLASSES[pred_idx]

    return "Unknown"


def _normalize_label(label: str) -> str:
    return LABEL_ALIASES.get(label.strip().lower(), label.strip().lower())


def classify_document_bytes(image_bytes: bytes) -> Tuple[str, float]:
    try:
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
    except Exception as exc:
        raise ValueError("Uploaded file is not a valid image") from exc

    # The torchvision transform returns a tensor, but the type checker needs help here.
    image_tensor = cast(torch.Tensor, get_transform()(image))
    image_tensor = image_tensor.unsqueeze(0)

    model, class_to_idx, device = get_document_classifier()
    image_tensor = image_tensor.to(device)

    with torch.no_grad():
        outputs = model(image_tensor)
        probs = torch.softmax(outputs, dim=1)
        confidence, pred = torch.max(probs, 1)

    # Convert the predicted class index into a regular Python int for label lookup.
    pred_idx = int(pred.item())
    label = _normalize_label(_resolve_label(pred_idx, class_to_idx))
    return label, float(confidence.item())


def validate_document_type(
    image_bytes: bytes,
    expected_label: str,
    confidence_threshold: float = CONFIDENCE_THRESHOLD,
) -> tuple[bool, str, float]:
    predicted_label, confidence = classify_document_bytes(image_bytes)
    normalized_expected = _normalize_label(expected_label)
    logger.info("Document classified as %s with confidence %.2f", predicted_label, confidence)

    if confidence < confidence_threshold:
        return False, predicted_label, confidence

    if predicted_label != normalized_expected:
        return False, predicted_label, confidence
    return True, predicted_label, confidence
