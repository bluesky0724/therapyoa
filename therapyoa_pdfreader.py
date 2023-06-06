import re
from pdfminer.high_level import extract_text

def extract_client_info(assessment_file_path):
    extracted_info = {'Name': '', 'DOB': ''}
    text = extract_text(assessment_file_path)

    # Search for the fields in the extracted text using regular expressions
    name_match = re.search(r'Name:\s*(.*)', text)
    dob_match = re.search(r'DOB:\s*(.*)', text)

    if name_match:
        extracted_info['Name'] = name_match.group(1).strip()

    if dob_match:
        extracted_info['DOB'] = dob_match.group(1).strip()

    return extracted_info