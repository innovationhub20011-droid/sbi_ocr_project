LOAN_PAGE1_PROMPT = """
Extract Loan Application Page 1 details.

Return STRICT JSON:

{
    "applicant_name": "",
    "dob": "",
    "mobile_number": "",
    "pan_number": "",
    "aadhaar_number": ""
}

Return empty string if not found.
No explanation.
"""