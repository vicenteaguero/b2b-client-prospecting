# client_prospecting/params.py

import os

ROOT_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))

ETC_DIR = os.path.join(ROOT_DIR, 'etc')
ASSETS_DIR = os.path.join(ROOT_DIR, 'assets')

ENV_PATH = os.path.join(ETC_DIR, '.env')

################################################################################

# Email

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

CREDENTIALS_PATH = os.path.join(ETC_DIR, 'credentials.json')
TOKEN_PATH = os.path.join(ETC_DIR, 'token.pkl')

################################################################################

# Prospecting

BUSINESS_INFO_PATH = os.path.join(ASSETS_DIR, 'business_info.md')
TEMPLATE_PATH = os.path.join(ASSETS_DIR, 'template.html')
BANNER_EMAIL_PATH = os.path.join(ASSETS_DIR, 'banner_email.jpg')
