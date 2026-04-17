PAGE1_PROMPT = """
Extract structured data from SBI Account Opening Form Page 1.

Rules:
- Extract only from labeled fields.
- Do not shift values between fields.
- For checkboxes, return only the selected option text i.e in the right side of checkbox.
- If "Others" is selected and a value is written, return: "Others - <value>"
- If nothing is selected or field not visible, return empty string.
- Date format: DD-MM-YYYY.
- Skip middle name if not present.
- Return STRICT JSON only. No explanations.
- Do not include markdown, bullets, section headers, or labels like "Extracted Data".
- Do not wrap output in code fences.
- Output must start with "{" and end with "}".
- Use only double quotes for JSON keys and string values.

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