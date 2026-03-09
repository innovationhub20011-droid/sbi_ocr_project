PAGE2_PROMPT = """
Extract structured data from SBI Account Opening Form – Page 2.

Rules:
- Extract only from labeled fields.
- Do not shift values across sections.
- For checkboxes, return only selected option text.
- If "Others" selected with handwritten value, return: "Others - <value>"
- If not selected or not visible, return empty string.
- Maintain exact spelling.
- Dates format: DDMMYYYY.
- Return valid JSON only. No explanations.

Return this JSON:

{
  "proof_of_identity": {
    "document_type": "",
    "equivalent_edocument": "",
    "document_number": "",
    "issued_by": "",
    "issue_date": "",
    "expiry_date": ""
  },
  "foreign_national_details": {
    "visa_details": "",
    "issued_by": "",
    "issue_date": "",
    "expiry_date": ""
  },
  "current_address": {
    "address_type": "",
    "address_line1": "",
    "address_line2": "",
    "city": "",
    "district": "",
    "state": "",
    "pin": "",
    "country": ""
  },
  "correspondence_address": {
    "address_type": "",
    "address_line1": "",
    "address_line2": "",
    "city": "",
    "district": "",
    "state": "",
    "pin": "",
    "country": ""
  },
  "additional_ovd_document": {
    "document_type": "",
    "document_number": "",
    "date": ""
  },
  "declaration": {
    "consent_for_aadhaar_auth": "",
    "place": "",
    "date": ""
  },
  "office_use": {
    "documents_received": "",
    "aadhaar_verification": "",
    "threshold_limit": "",
    "bis_organization_code": "",
    "customer_segment": "",
    "depositor_type": "",
    "risk_category": "",
    "permitted_to_open_cif": "",
    "official_name": "",
    "pf_number": "",
    "ss_number": "",
    "designation": "",
    "office_date": ""
  }
}
"""