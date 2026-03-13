from typing import Optional

from langchain_core.messages import HumanMessage

from config.ollama_settings import load_ollama_settings
from llm.client_factory import get_json_client, get_raw_client
from llm.content_utils import normalize_content
from llm.raw_output_logger import log_raw_output
from llm.response_parsers import parse_json_or_fallback
from utils.model_routing import get_model_for_endpoint


_settings = load_ollama_settings()


def call_vision_model(
    prompt: str,
    image_base64: str,
    empty_schema: Optional[dict] = None,
    api_endpoint: str = "N/A",
    file_name: str = "N/A",
) -> dict:
    """Generic vision caller that returns parsed dictionary output."""

    if empty_schema is None:
        empty_schema = {}

    try:
        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                },
            ]
        )

        model_name = get_model_for_endpoint(api_endpoint, _settings.default_model)
        response = get_json_client(model_name).invoke([message])

        raw_output = normalize_content(response.content)
        log_raw_output(raw_output, _settings.raw_output_log_path, api_endpoint=api_endpoint, file_name=file_name)
        return parse_json_or_fallback(raw_output, empty_schema)

    except Exception:
        return empty_schema


def call_vision_model_raw(
    prompt: str,
    image_base64: str,
    api_endpoint: str = "N/A",
    file_name: str = "N/A",
) -> str:
    """Vision caller for plain text OCR."""

    try:
        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                },
            ]
        )

        model_name = get_model_for_endpoint(api_endpoint, _settings.default_model)
        response = get_raw_client(model_name).invoke([message])

        raw_output = normalize_content(response.content)
        log_raw_output(raw_output, _settings.raw_output_log_path, api_endpoint=api_endpoint, file_name=file_name)
        return raw_output.strip()

    except Exception:
        return ""
