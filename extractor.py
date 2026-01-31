import re
import json
import urllib.parse
import unicodedata

INPUT_FILE = "sample_input.txt"
OUTPUT_FILE = "sample_output.json"

def read_input(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def is_safe_url(raw_line: str) -> bool:
    normalized = unicodedata.normalize('NFKC', raw_line)
    decoded = urllib.parse.unquote(normalized).lower()

    # 1. Reject if it contains quotes (Fixes "http://example".com)
    if '"' in decoded or "'" in decoded:
        return False

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
    
    if ":///" in url_candidate:
        return False

    try:
        parsed = urllib.parse.urlparse(url_candidate)
        domain = parsed.netloc

        if parsed.scheme not in ['http', 'https']:
            return False

        if not domain:
            return False
        
        if '.' not in domain and domain != 'localhost':
            return False

        if domain.endswith('.'):
            return False
        
        if '..' in domain:
            return False
        
        domain.encode('ascii')
        
    except (UnicodeEncodeError, AttributeError, Exception):
        return False

    return True

def extract_urls(text: str) -> list:
    safe_urls = []
    lines = text.splitlines()

    for line in lines:
        line = line.strip()
        if not line: 
            continue
        match = re.search(r'https?://.+', line)
        if match:
            full_segment = match.group(0)
            
            url_candidate = full_segment.split()[0]

            if not url_candidate:
                continue

            last_char = url_candidate[-1]
            if last_char in ['.', ',']:
                url_candidate = url_candidate[:-1]
            
            elif not last_char.isalnum() and last_char != '/':
                continue
            if is_safe_url(url_candidate):
                safe_urls.append(url_candidate)
                
    return safe_urls

def extract_emails(text: str) -> list:
    pattern = r'\b[a-zA-Z0-9._%+-]+(?<!\.)@(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b'
    found = re.findall(pattern, text)
    return [email for email in found if ".." not in email]


def mask_email(email: str) -> str:
    try:
        user, domain = email.split('@')
        
        if len(user) <= 2:
            masked_user = user[0] + "***"
        else:
            masked_user = f"{user[0]}*****{user[-1]}"
            
        return f"{masked_user}@{domain}"
    except ValueError:
        return email




def extract_hashtags(text: str) -> list:
    pattern = r'(#[0-9_]*[A-Za-z][A-Za-z0-9_]*)[.,]?(?=\s|$)'
    return re.findall(pattern, text)

def extract_credit_cards(text: str) -> list:
    pattern = r'\b(?:\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4})\b'
    matches = re.findall(pattern, text)

    masked_cards = []
    for card in matches:
        last_four = card[-4:]
        masked_cards.append("**** **** **** " + last_four)

    return masked_cards

def extract_currency(text: str) -> list:
    pattern = r'(?<!#)\$\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?\b'
    return re.findall(pattern, text)




def write_output(file_path: str, data: dict) -> None:

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
def main():
    raw_text = read_input(INPUT_FILE)
    raw_emails = extract_emails(raw_text)
    results = {
        "emails": [mask_email(email) for email in raw_emails],
        "urls": extract_urls(raw_text),
        "credit_cards": extract_credit_cards(raw_text),
        "currency_amounts": extract_currency(raw_text),
        "hashtags": extract_hashtags(raw_text)
    }

    write_output(OUTPUT_FILE, results)


    print(json.dumps(results, indent=4))


if __name__ == "__main__":
    main()