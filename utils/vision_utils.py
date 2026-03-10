from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from typing import Any
import os
import re
import json

from dotenv import load_dotenv


load_dotenv()


OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL") or os.getenv("OLLAMA_HOST")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2-vision:11b")
OLLAMA_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0"))
OLLAMA_NUM_PREDICT = int(os.getenv("OLLAMA_NUM_PREDICT", "2048"))

llm_config = {
    "model": OLLAMA_MODEL,
    "temperature": OLLAMA_TEMPERATURE,
    "num_predict": OLLAMA_NUM_PREDICT,
}

if OLLAMA_BASE_URL:
    llm_config["base_url"] = OLLAMA_BASE_URL


llm = ChatOllama(
    **llm_config
)

llm_json = ChatOllama(
    **llm_config,
    format="json"
)


def _normalize_content(content: Any) -> str:
    print('This is the data ..... ',content)
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        result = ""
        for part in content:
            if isinstance(part, str):
                result += part
            elif isinstance(part, dict) and "text" in part:
                result += part["text"]
        return result

    return ""


def _empty_like(schema: dict) -> dict:
    """Return a shallow empty copy for flat dict schemas."""
    return {k: "" for k in schema.keys()}


def _extract_from_labeled_text(raw_output: str, empty_schema: dict) -> dict:
    """
    Fallback parser for outputs like:
    **Full Name:** John Doe
    **Father's Name:** ...
    """
    # Only apply on flat JSON schemas.
    if not isinstance(empty_schema, dict) or any(isinstance(v, dict) for v in empty_schema.values()):
        return empty_schema

    parsed = _empty_like(empty_schema)

    for key in parsed.keys():
        label = key.replace("_", " ")
        pattern = rf"(?im)^\s*\**\s*{re.escape(label)}\s*\**\s*:\s*(.+?)\s*$"
        match = re.search(pattern, raw_output)
        if match:
            parsed[key] = match.group(1).strip()

    # PAN-specific fallback from free text if label mapping didn't work.
    if "pan_number" in parsed and not parsed["pan_number"]:
        pan_match = re.search(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", raw_output.upper())
        if pan_match:
            parsed["pan_number"] = pan_match.group(0)

    # Aadhaar fallback from free text if label mapping didn't work.
    if "aadhaar_number" in parsed and not parsed["aadhaar_number"]:
        aadhaar_match = re.search(r"\b(?:\d{4}\s?){3}\b", raw_output)
        if aadhaar_match:
            parsed["aadhaar_number"] = " ".join(aadhaar_match.group(0).split())

    if any(value for value in parsed.values()):
        return parsed

    return empty_schema


def call_vision_model(prompt: str, image_base64: str, empty_schema: dict) -> dict:
    """
    Generic Vision Caller
    Always returns dictionary (never raises)
    """

    try:
        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    },
                },
            ]
        )

        response = llm_json.invoke([message])

        raw_output = _normalize_content(response.content)

        print("===== RAW MODEL OUTPUT =====")
        print(raw_output)
        print("=============================")

        # Extract JSON block
        #json_match = re.search(r"\{.*?\}", raw_output, re.DOTALL)
        json_match = re.search(r"\{.*\}", raw_output, re.DOTALL)

        if not json_match:
            return _extract_from_labeled_text(raw_output, empty_schema)

        json_string = json_match.group(0)

        try:
            return json.loads(json_string)
        except json.JSONDecodeError:
            return _extract_from_labeled_text(raw_output, empty_schema)

    except Exception:
        return empty_schema
    
# this is method for raw text files.
def call_vision_model_raw(prompt: str, image_base64: str) -> str:
    """
    Vision caller for raw text OCR.
    Returns plain text.
    """

    try:
        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    },
                },
            ]
        )

        response = llm.invoke([message])

        raw_output = _normalize_content(response.content)

        print("===== RAW MODEL OUTPUT =====")
        print(raw_output)
        print("=============================")

        return raw_output.strip()

    except Exception as e:
        return ""