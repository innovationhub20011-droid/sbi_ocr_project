import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class OllamaSettings:
    base_url: str | None
    default_model: str
    temperature: float
    num_predict: int
    raw_num_predict: int
    repeat_penalty: float
    repeat_last_n: int
    raw_output_log_path: str


def load_ollama_settings() -> OllamaSettings:
    base_url = os.getenv("OLLAMA_BASE_URL") or os.getenv("OLLAMA_HOST")
    default_model = os.getenv("OLLAMA_MODEL", "").strip()
    if not default_model:
        raise ValueError("OLLAMA_MODEL is required in .env")

    return OllamaSettings(
        base_url=base_url,
        default_model=default_model,
        temperature=float(os.getenv("OLLAMA_TEMPERATURE", "0")),
        num_predict=int(os.getenv("OLLAMA_NUM_PREDICT", "2048")),
        raw_num_predict=int(os.getenv("OLLAMA_RAW_NUM_PREDICT", "1200")),
        repeat_penalty=float(os.getenv("OLLAMA_REPEAT_PENALTY", "1.15")),
        repeat_last_n=int(os.getenv("OLLAMA_REPEAT_LAST_N", "128")),
        raw_output_log_path=os.getenv("RAW_OUTPUT_LOG_PATH", "data/raw_model_output.txt"),
    )
