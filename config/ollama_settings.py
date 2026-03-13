import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class OllamaSettings:
    base_url: str
    model: str
    temperature: float
    num_predict: int


def load_ollama_settings() -> OllamaSettings:
    base_url = (os.getenv("OLLAMA_BASE_URL") or os.getenv("OLLAMA_HOST") or "").strip()
    if not base_url:
        raise ValueError("OLLAMA_BASE_URL (or OLLAMA_HOST) is required in .env")

    model = os.getenv("OLLAMA_MODEL", "").strip()
    if not model:
        raise ValueError("OLLAMA_MODEL is required in .env")

    return OllamaSettings(
        base_url=base_url,
        model=model,
        temperature=float(os.getenv("OLLAMA_TEMPERATURE", "0")),
        num_predict=int(os.getenv("OLLAMA_NUM_PREDICT", "2048")),
    )
