import logging
from functools import lru_cache
from io import BytesIO
from typing import Tuple, cast

import torch
from PIL import Image
from torchvision import models, transforms

logger = logging.getLogger(__name__)

MODEL_PATH = "weights/account_page_classifier.pth"
DEFAULT_CLASSES = [f"page_{i}" for i in range(1, 8)]
IMAGE_SIZE = (224, 224)
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def get_device() -> torch.device:
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


def build_model(num_classes: int) -> torch.nn.Module:
    model = models.mobilenet_v2(weights=None)
    model.classifier[1] = torch.nn.Linear(model.last_channel, num_classes)
    return model


@lru_cache(maxsize=1)
def get_account_page_classifier() -> tuple[torch.nn.Module, dict, torch.device]:
    device = get_device()
    logger.info("Loading account page classifier on device=%s", device)

    model = build_model(len(DEFAULT_CLASSES))
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
        return idx_to_class.get(pred_idx, DEFAULT_CLASSES[pred_idx] if 0 <= pred_idx < len(DEFAULT_CLASSES) else "Unknown")

    if 0 <= pred_idx < len(DEFAULT_CLASSES):
        return DEFAULT_CLASSES[pred_idx]

    return "Unknown"


def display_name_for_class(class_name: str) -> str:
    if class_name.startswith("page_"):
        suffix = class_name.split("_", 1)[1]
        if suffix.isdigit():
            return f"Page {suffix}"
    return class_name.replace("_", " ").title()


def classify_account_page_bytes(image_bytes: bytes) -> Tuple[str, float]:
    try:
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
    except Exception as exc:
        raise ValueError("Uploaded file is not a valid image") from exc

    image_tensor = cast(torch.Tensor, get_transform()(image))
    image_tensor = image_tensor.unsqueeze(0)

    model, class_to_idx, device = get_account_page_classifier()
    image_tensor = image_tensor.to(device)

    with torch.no_grad():
        outputs = model(image_tensor)
        probabilities = torch.softmax(outputs, dim=1)
        confidence, prediction = torch.max(probabilities, 1)

    pred_idx = int(prediction.item())
    label = _resolve_label(pred_idx, class_to_idx)
    return label, float(confidence.item())


def validate_account_page1(image_bytes: bytes) -> tuple[bool, str, float]:
    predicted_label, confidence = classify_account_page_bytes(image_bytes)
    logger.info("Account page classified as %s with confidence %.2f", predicted_label, confidence)
    return predicted_label == "page_1", predicted_label, confidence
