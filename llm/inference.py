import asyncio
import logging
from typing import Optional

from langchain_core.messages import HumanMessage

from config.ollama_settings import load_ollama_settings
from llm.client_factory import get_llm_client
from llm.content_utils import normalize_content
from llm.raw_output_logger import log_raw_output
from llm.response_parsers import parse_json_or_fallback


_settings = load_ollama_settings()
_RAW_OUTPUT_LOG_PATH = "data/raw_model_output.txt"
_logger = logging.getLogger("uvicorn.error")


def _build_vision_message(prompt: str, image_base64: str) -> HumanMessage:
    return HumanMessage(
        content=[
            {
                "type": "text",
                "text": prompt,
            },
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
            },
        ]
    )


def _invoke_vision_model(
    *,
    isjson: bool,
    prompt: str,
    image_base64: str,
    api_endpoint: str,
    file_name: str,
) -> str:
    model_name = _settings.model
    _logger.info("Calling vision model with model=%s endpoint=%s file=%s", model_name, api_endpoint, file_name)

    message = _build_vision_message(prompt, image_base64)
    response = get_llm_client(model_name, isjson=isjson).invoke([message])

    raw_output = normalize_content(response.content)
    log_raw_output(raw_output, _RAW_OUTPUT_LOG_PATH, api_endpoint=api_endpoint, file_name=file_name)
    return raw_output


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
        raw_output = _invoke_vision_model(
            isjson=True,
            prompt=prompt,
            image_base64=image_base64,
            api_endpoint=api_endpoint,
            file_name=file_name,
        )
        return parse_json_or_fallback(raw_output, empty_schema)

    except Exception as exc:
        _logger.exception(
            "Vision model call failed | endpoint=%s file=%s",
            api_endpoint,
            file_name,
        )
        raise RuntimeError("Vision model call failed") from exc


def call_vision_model_raw(
    prompt: str,
    image_base64: str,
    api_endpoint: str = "N/A",
    file_name: str = "N/A",
) -> str:
    """Vision caller for plain text OCR."""

    try:
        raw_output = _invoke_vision_model(
            isjson=False,
            prompt=prompt,
            image_base64=image_base64,
            api_endpoint=api_endpoint,
            file_name=file_name,
        )
        return raw_output.strip()

    except Exception as exc:
        _logger.exception(
            "Raw vision model call failed | endpoint=%s file=%s",
            api_endpoint,
            file_name,
        )
        raise RuntimeError("Raw vision model call failed") from exc


async def call_vision_model_async(
    prompt: str,
    image_base64: str,
    empty_schema: Optional[dict] = None,
    api_endpoint: str = "N/A",
    file_name: str = "N/A",
) -> dict:
    return await asyncio.to_thread(
        call_vision_model,
        prompt,
        image_base64,
        empty_schema,
        api_endpoint,
        file_name,
    )


async def call_vision_model_raw_async(
    prompt: str,
    image_base64: str,
    api_endpoint: str = "N/A",
    file_name: str = "N/A",
) -> str:
    return await asyncio.to_thread(
        call_vision_model_raw,
        prompt,
        image_base64,
        api_endpoint,
        file_name,
    )
