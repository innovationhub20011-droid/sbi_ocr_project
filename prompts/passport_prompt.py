PASSPORT_PROMPT = """
Extract all visible text from the image.

From the extracted text, fill the JSON structure below.
Return JSON only.
If a value is not visible, return empty string.

{
    "passport_number": "",
    "surname": "",
    "given_names": "",
    "nationality": "",
    "sex": "",
    "date_of_birth": "",
    "place_of_birth": "",
    "date_of_issue": "",
    "date_of_expiry": "",
    "place_of_issue": "",
    "father_name": "",
    "mother_name": "",
    "address": "",
    "pin_code": "",
    "file_number": ""
}
"""