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
            
            if is_safe_url(full_segment):

                safe_urls.append(full_segment.split()[0])
                
    return safe_urls



def write_output(file_path: str, data: dict) -> None:

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
def main():
    raw_text = read_input(INPUT_FILE)

    results = {
        "urls": extract_urls(raw_text)
    }

    write_output(OUTPUT_FILE, results)


    print(json.dumps(results, indent=4))


if __name__ == "__main__":
    main()