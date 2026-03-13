import logging
from typing import Optional

from langchain_core.messages import HumanMessage

from config.ollama_settings import load_ollama_settings
from llm.client_factory import get_json_client, get_raw_client
from llm.content_utils import normalize_content
from llm.raw_output_logger import log_raw_output
from llm.response_parsers import parse_json_or_fallback
from utils.model_routing import get_model_for_endpoint


_settings = load_ollama_settings()
_RAW_OUTPUT_LOG_PATH = "data/raw_model_output.txt"
_logger = logging.getLogger("uvicorn.error")


def _build_prompt_with_model_info(prompt: str, model_name: str, api_endpoint: str) -> str:
    """Attach model metadata to the message content sent to Ollama."""
    return f"[MODEL={model_name}] [ENDPOINT={api_endpoint}]\n{prompt}"


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
        model_name = get_model_for_endpoint(api_endpoint, _settings.model)
        _logger.info("Calling call_vision_model with model=%s endpoint=%s file=%s", model_name, api_endpoint, file_name)

        message = HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": _build_prompt_with_model_info(prompt, model_name, api_endpoint),
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                },
            ]
        )

        response = get_json_client(model_name).invoke([message])

        raw_output = normalize_content(response.content)
        log_raw_output(raw_output, _RAW_OUTPUT_LOG_PATH, api_endpoint=api_endpoint, file_name=file_name)
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
        model_name = get_model_for_endpoint(api_endpoint, _settings.model)
        _logger.info("Calling call_vision_model_raw with model=%s endpoint=%s file=%s", model_name, api_endpoint, file_name)

        message = HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": _build_prompt_with_model_info(prompt, model_name, api_endpoint),
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                },
            ]
        )

        response = get_raw_client(model_name).invoke([message])

        raw_output = normalize_content(response.content)
        log_raw_output(raw_output, _RAW_OUTPUT_LOG_PATH, api_endpoint=api_endpoint, file_name=file_name)
        return raw_output.strip()

    except Exception:
        return ""
