import re

def extract_client_name(file_contents):
    # Implement your logic to extract the client name using regular expressions
    # For example:
    match = re.search(r"Name: (.+)", file_contents)
    if match:
        return match.group(1)
    else:
        return ""

def extract_ahcccs_id(file_contents):
    # Implement your logic to extract the AHCCCS ID using regular expressions
    # For example:
    match = re.search(r"AHCCCS ID: (.+)", file_contents)
    if match:
        return match.group(1)
    else:
        return ""

def extract_note_type(file_contents):
    # Implement your logic to extract the note type using regular expressions
    # For example:
    match = re.search(r"Service Code: (.+)", file_contents)
    if match:
        return match.group(1)
    else:
        return ""

def extract_date(file_contents):
    # Implement your logic to extract the date using regular expressions
    # For example:
    match = re.search(r"Date of Service: (.+)", file_contents)
    if match:
        return match.group(1)
    else:
        return ""
