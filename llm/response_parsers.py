import json
import re


def _empty_like(schema: dict) -> dict:
    """Return a shallow empty copy for flat dict schemas."""
    empty = {}
    for key, value in schema.items():
        empty[key] = _empty_like(value) if isinstance(value, dict) else ""
    return empty


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


def _is_meaningful_value(value) -> bool:
    if isinstance(value, dict):
        return any(_is_meaningful_value(inner) for inner in value.values())
    if isinstance(value, str):
        return bool(value.strip())
    return value not in (None, "", [], {})


def _normalize_json_to_schema(parsed_json: dict, empty_schema: dict) -> dict:
    """Map model keys to expected schema keys so minor key variations are tolerated."""
    if not isinstance(parsed_json, dict) or not isinstance(empty_schema, dict):
        return empty_schema

    if not empty_schema:
        return parsed_json

    normalized_source = {
        _normalized_key(k): v for k, v in parsed_json.items() if isinstance(k, str)
    }

    aliases = _alias_groups()
    output = _empty_like(empty_schema)

    for expected_key in output.keys():
        template = empty_schema.get(expected_key)

        if isinstance(template, dict):
            candidate = parsed_json.get(expected_key)
            if isinstance(candidate, dict):
                output[expected_key] = _normalize_json_to_schema(candidate, template)
            continue

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
    if not isinstance(empty_schema, dict):
        return empty_schema

    parsed = {}

    for key, template in empty_schema.items():
        if isinstance(template, dict):
            parsed[key] = extract_from_labeled_text(raw_output, template)
            continue

        label = key.replace("_", " ")
        pattern = rf"(?im)^\s*\**\s*{re.escape(label)}\s*\**\s*:\s*(.+?)\s*$"
        match = re.search(pattern, raw_output)
        parsed[key] = match.group(1).strip() if match else ""

    return parsed

def parse_json_or_fallback(raw_output: str, empty_schema: dict) -> dict:
    json_match = re.search(r"\{.*\}", raw_output, re.DOTALL)
    if not json_match:
        return extract_from_labeled_text(raw_output, empty_schema)

    json_string = json_match.group(0)

    try:
        parsed_json = json.loads(json_string)

        normalized = _normalize_json_to_schema(parsed_json, empty_schema)
        if _is_meaningful_value(normalized):
            return normalized

        return extract_from_labeled_text(raw_output, empty_schema)

    except json.JSONDecodeError:
        parsed = extract_from_labeled_text(raw_output, empty_schema)

        if isinstance(parsed, dict) and "date_of_birth" in parsed and not str(parsed.get("date_of_birth", "")).strip():
            parsed["date_of_birth"] = _extract_date_of_birth_fallback(raw_output)

        return parsed
