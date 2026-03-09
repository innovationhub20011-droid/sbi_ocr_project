from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from typing import Any
import re
import json


llm = ChatOllama(
    model="llama3.2-vision:11b",
    temperature=0
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

        response = llm.invoke([message])

        raw_output = _normalize_content(response.content)

        print("===== RAW MODEL OUTPUT =====")
        print(raw_output)
        print("=============================")

        # Extract JSON block
        #json_match = re.search(r"\{.*?\}", raw_output, re.DOTALL)
        json_match = re.search(r"\{.*\}", raw_output, re.DOTALL)

        if not json_match:
            return empty_schema  # Model refused

        json_string = json_match.group(0)

        try:
            return json.loads(json_string)
        except json.JSONDecodeError:
            return empty_schema

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