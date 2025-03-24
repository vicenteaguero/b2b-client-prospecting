#  client_prospectin/utils.py

from dotenv import load_dotenv

import base64
import re

from client_prospecting.params import ENV_PATH

def load_env():
    load_dotenv(ENV_PATH)

def extract_plain_text(payload):
    if payload.get('mimeType') == 'text/plain' and 'data' in payload['body']:
        return base64.urlsafe_b64decode(payload['body']['data']).decode()
    if 'parts' in payload:
        for part in payload['parts']:
            result = extract_plain_text(part)
            if result:
                return result
    return ''

def extract_mail(sender):
    match = re.match(r'(.*)<(.+)>', sender)
    if match:
        name, email = match.groups()
        return name.strip(), email.strip()
    else:
        return '', sender.strip()

def clean_subject(subject):
    cleaned = re.sub(r'^(Re:\s*)+', '', subject, flags=re.IGNORECASE)
    return f'Re: {cleaned.strip()}'
