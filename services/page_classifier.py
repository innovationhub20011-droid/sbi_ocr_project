def classify_page(dummy_text: str):
    if "Loan Application" in dummy_text:
        return "loan_page1"
    elif "Employment" in dummy_text:
        return "loan_page2"
    else:
        return "unknown"