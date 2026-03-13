from typing import Any


def normalize_content(content: Any) -> str:
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
