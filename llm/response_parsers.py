import json
import re


def _empty_like(schema: dict) -> dict:
    """Return a shallow empty copy for flat dict schemas."""
    return {k: "" for k in schema.keys()}


def _normalized_key(key: str) -> str:
    return re.sub(r"[^a-z0-9]", "", key.lower())


def _alias_groups() -> dict[str, set[str]]:
    return {
        "full_name": {"fullname", "name", "cardholdername", "holdername"},
        "father_name": {"fathername", "fathersname", "fathers_name", "parentname"},
        "date_of_birth": {"dateofbirth", "dob", "birthdate", "yearofbirth", "yob"},
        "aadhaar_number": {"aadhaarnumber", "aadharnumber", "uid", "uidnumber"},
        "pan_number": {"pannumber", "pan"},
        "driving_licence_number": {
            "drivinglicencenumber",
            "drivinglicensenumber",
            "licencenumber",
            "licensenumber",
            "dlnumber",
        },
    }


def _normalize_json_to_schema(parsed_json: dict, empty_schema: dict) -> dict:
    """Map model keys to expected schema keys so minor key variations are tolerated."""
    if not isinstance(parsed_json, dict) or not isinstance(empty_schema, dict):
        return empty_schema

    normalized_source = {
        _normalized_key(k): v for k, v in parsed_json.items() if isinstance(k, str)
    }

    aliases = _alias_groups()
    output = _empty_like(empty_schema)

    for expected_key in output.keys():
        expected_norm = _normalized_key(expected_key)
        candidate_norms = {expected_norm}
        candidate_norms.update(_normalized_key(a) for a in aliases.get(expected_key, set()))

        for candidate in candidate_norms:
            if candidate in normalized_source:
                value = normalized_source[candidate]
                output[expected_key] = value.strip() if isinstance(value, str) else value
                break

    return output


def _extract_date_of_birth_fallback(raw_output: str) -> str:
    """Best-effort DOB extraction from OCR text for Aadhaar-like outputs."""
    patterns = [
        # Date formats after DOB labels.
        r"(?im)(?:date\s*of\s*birth|dob)\s*[:\-]?\s*(\d{2}[/-]\d{2}[/-]\d{2,4})",
        # Year-of-birth label (common on some Aadhaar layouts).
        r"(?im)(?:year\s*of\s*birth|yob)\s*[:\-]?\s*(\d{4})",
        # Generic full-date fallback if explicit labels are missing.
        r"\b(\d{2}[/-]\d{2}[/-]\d{4})\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, raw_output)
        if match:
            return match.group(1).strip()

    return ""


def extract_from_labeled_text(raw_output: str, empty_schema: dict) -> dict:
    """
    Fallback parser for outputs like:
    **Full Name:** John Doe
    **Father's Name:** ...
    """
    if not isinstance(empty_schema, dict) or any(isinstance(v, dict) for v in empty_schema.values()):
        return empty_schema

    parsed = _empty_like(empty_schema)

    for key in parsed.keys():
        label = key.replace("_", " ")
        pattern = rf"(?im)^\s*\**\s*{re.escape(label)}\s*\**\s*:\s*(.+?)\s*$"
        match = re.search(pattern, raw_output)
        if match:
            parsed[key] = match.group(1).strip()

    if "pan_number" in parsed and not parsed["pan_number"]:
        pan_match = re.search(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", raw_output.upper())
        if pan_match:
            parsed["pan_number"] = pan_match.group(0)

    if "aadhaar_number" in parsed and not parsed["aadhaar_number"]:
        aadhaar_match = re.search(r"\b(?:\d{4}\s?){3}\b", raw_output)
        if aadhaar_match:
            parsed["aadhaar_number"] = " ".join(aadhaar_match.group(0).split())

    if any(value for value in parsed.values()):
        return parsed

    return empty_schema


def parse_json_or_fallback(raw_output: str, empty_schema: dict) -> dict:
    json_match = re.search(r"\{.*\}", raw_output, re.DOTALL)
    if not json_match:
        return extract_from_labeled_text(raw_output, empty_schema)

    json_string = json_match.group(0)
    try:
        parsed_json = json.loads(json_string)
        normalized = _normalize_json_to_schema(parsed_json, empty_schema)

        if "date_of_birth" in normalized and not str(normalized.get("date_of_birth", "")).strip():
            normalized["date_of_birth"] = _extract_date_of_birth_fallback(raw_output)

        # If JSON is present but effectively empty, try labeled-text fallback.
        if not any(str(v).strip() for v in normalized.values()):
            return extract_from_labeled_text(raw_output, empty_schema)

        return normalized
    except json.JSONDecodeError:
        parsed = extract_from_labeled_text(raw_output, empty_schema)
        if "date_of_birth" in parsed and not str(parsed.get("date_of_birth", "")).strip():
            parsed["date_of_birth"] = _extract_date_of_birth_fallback(raw_output)
        return parsed
