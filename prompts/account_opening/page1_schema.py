PAGE1_PROMPT = """
Extract structured data from SBI Account Opening Form – Page 1.

Rules:
- Extract only from labeled fields.
- Do not shift values between fields.
- For checkboxes, return only the selected option text.
- If "Others" is selected and a value is written, return: "Others - <value>"
- If nothing is selected or field not visible, return empty string.
- Date format: DDMMYYYY.
- Return valid JSON only. No explanations.

Return this JSON:

{
  "top_section": {
    "branch_name": "",
    "branch_code": "",
    "date": "",
    "customer_id": "",
    "account_number": "",
    "account_type": "",
    "ckyc_number": "",
    "pf_number": ""
  },
  "personal_section": {
    "first_name": "",
    "middle_name": "",
    "last_name": "",
    "dob": "",
    "gender": "",
    "marital_status": "",
    "parent_or_spouse_name": "",
    "guardian_name": "",
    "relationship_with_guardian": "",
    "nationality": "",
    "citizenship": "",
    "occupation_type": "",
    "employee_id": "",
    "place_of_posting": "",
    "organization_name": "",
    "nature_of_business": "",
    "designation": "",
    "annual_income": "",
    "net_worth": "",
    "source_of_funds": "",
    "religion": "",
    "category": "",
    "person_with_disability": "",
    "education": "",
    "politically_exposed": "",
    "pan_number": ""
  },
  "contact_section": {
    "mobile_number": "",
    "email": "",
    "std_tel_off": "",
    "tel_res": ""
  }
}
"""