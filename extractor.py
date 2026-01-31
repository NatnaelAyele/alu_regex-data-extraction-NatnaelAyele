import re
import json
import urllib.parse
import unicodedata


# Input and output file names
INPUT_FILE = "sample_input.txt"
OUTPUT_FILE = "sample_output.json"


# Reads all text from the given input file and returns it as a single string.
def read_input(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def is_safe_url(raw_line: str) -> bool:
    """
    Checks whether a given URL is safe and valid.
    """
    
    # Normalize unicode characters so that hidden or tricky characters are converted into a standard form
    normalized = unicodedata.normalize('NFKC', raw_line)
    decoded = urllib.parse.unquote(normalized).lower()

    # Reject URLs that contain quotes, which are often used in injections
    if '"' in decoded or "'" in decoded:
        return False

    # List of dangerous keywords and patterns commonly used in attacks
    danger_flags = [
        '<script', '<img', 'onerror', 'onload', 'alert(', 
        'javascript:', 'vbscript:', 'data:',             
        'or 1=1', "' or '", "admin'", "'--", "union select", 
        'drop table', 'drop ', 'delete from',            
        '../', '..\\'                                    
    ]

    for flag in danger_flags:
        if flag in decoded:
            return False

    url_candidate = raw_line.split()[0]
    

    # URLs with too many slashes like "http:///" are invalid
    if ":///" in url_candidate:
        return False

    try:
        # Parse the URL into components (scheme, domain, path, etc.)
        parsed = urllib.parse.urlparse(url_candidate)
        domain = parsed.netloc

        if parsed.scheme not in ['http', 'https']:
            return False
        
        # URL must have a domain name
        if not domain:
            return False
        
         # Domain should contain a dot (except for localhost)
        if '.' not in domain and domain != 'localhost':
            return False

        if domain.endswith('.'):
            return False
        # Double dots in domains are rejected
        if '..' in domain:
            return False
        
        domain.encode('ascii')
        
    except (UnicodeEncodeError, AttributeError, Exception):
        return False
    
    # If all checks pass, the URL is considered safe
    return True

def extract_urls(text: str) -> list:
    """
    Scans the input text line by line and extracts URLs found in it.
    Each URL is cleaned and checked using the safety validation function (is_safe_url()).
    """

    safe_urls = []

    # Split the input text into individual lines
    lines = text.splitlines()

    for line in lines:
        line = line.strip()

        # Skip empty lines
        if not line: 
            continue

         # Look for a URL starting with http:// or https://
        match = re.search(r'https?://.+', line)
        if match:
            full_segment = match.group(0)
            
            url_candidate = full_segment.split()[0]

            if not url_candidate:
                continue

            # Remove trailing punctuation like "." or ","
            last_char = url_candidate[-1]
            if last_char in ['.', ',']:
                url_candidate = url_candidate[:-1]
            
             # If the URL ends with an invalid character, skip it
            elif not last_char.isalnum() and last_char != '/':
                continue

            # Check if the URL passes all safety rules
            if is_safe_url(url_candidate):
                safe_urls.append(url_candidate)
                
    return safe_urls

def extract_emails(text: str) -> list:
    """
    Extracts email addresses from a block of text using a regex pattern and returns them.
    """

    # Regex pattern to match valid email addresses
    pattern = r'\b[a-zA-Z0-9._%+-]+(?<!\.)@(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b'
    found = re.findall(pattern, text)

    # Filter out emails that contain double dots (..) and return
    return [email for email in found if ".." not in email]


def mask_email(email: str) -> str:
    """
    Masks the username part of an email address to protect privacy.
    Only the first and last characters are kept visible.
    used to display or store emails in a safer, less sensitive form.
    """

    try:
        user, domain = email.split('@')
        
        # If the username is very short, only keep the first character and mask the rest
        if len(user) <= 2:
            masked_user = user[0] + "***"
        else:

            # For longer usernames, keep the first and last character and hide everything in between
            masked_user = f"{user[0]}*****{user[-1]}"
            
        return f"{masked_user}@{domain}"
    
    except ValueError:
        return email




def extract_hashtags(text: str) -> list:
    """
    Extracts hashtags from a block of text using a regex pattern and returns them.
    """

    pattern = r'(#[0-9_]*[A-Za-z][A-Za-z0-9_]*)[.,]?(?=\s|$)'
    return re.findall(pattern, text)

def extract_credit_cards(text: str) -> list:
    """
    Extracts credit card numbers from a block of text using a regex pattern and returns them.
    """

    # Regex pattern to match valid credit card numbers
    pattern = r'\b(?:\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4})\b'
    matches = re.findall(pattern, text)

    masked_cards = []

    # hide the first twelve digits and keep the last four digits only
    for card in matches:
        last_four = card[-4:]
        masked_cards.append("**** **** **** " + last_four)

    return masked_cards

def extract_currency(text: str) -> list:
    """
    Extracts currency type data from a block of text using a regex pattern and returns them.
    """
    pattern = r'(?<!#)\$\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?\b'
    return re.findall(pattern, text)




def write_output(file_path: str, data: dict) -> None:
    """
    Writes the extracted results into a JSON file.
    in a structured and readable format.
    """

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
def main():

    """
    Acts as the main entry point of the program.
    It reads the input file, extracts the matching data types,
    saves the output to a JSON file, and prints the result.
    """

    # Read raw text from the input file
    raw_text = read_input(INPUT_FILE)
    raw_emails = extract_emails(raw_text)

    # Extract valid 'emails', 'urls', 'credit card numbers', 'currency_amounts', 'hashtags' and store them in a dictionary
    results = {
        "emails": [mask_email(email) for email in raw_emails],
        "urls": extract_urls(raw_text),
        "credit_cards": extract_credit_cards(raw_text),
        "currency_amounts": extract_currency(raw_text),
        "hashtags": extract_hashtags(raw_text)
    }

    # Write results to the output JSON file
    write_output(OUTPUT_FILE, results)

    # prints the result in the terminal
    print(json.dumps(results, indent=4))


if __name__ == "__main__":
    main()