import json
import re


def _empty_like(schema: dict) -> dict:
    """Return an empty copy for a flat dict schema."""
    return {key: "" for key in schema.keys()}


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

def parse_json_or_fallback(raw_output: str, empty_schema: dict) -> dict:
    json_match = re.search(r"\{.*\}", raw_output, re.DOTALL)
    if not json_match:
        return empty_schema

    json_string = json_match.group(0)

    try:
        parsed_json = json.loads(json_string)

        if not empty_schema:
            return parsed_json

        normalized = _normalize_json_to_schema(parsed_json, empty_schema)
        if any(str(value).strip() for value in normalized.values() if value is not None):
            return normalized

        return empty_schema

    except json.JSONDecodeError:
        return empty_schema
