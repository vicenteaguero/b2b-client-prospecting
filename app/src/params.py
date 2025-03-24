# app/src/params.py

import os

APP_NAME = 'app'

# Root Folders
DATA_FOLDER = 'data'
ASSETS_FOLDER = 'assets'

# App Folders
PAGES_FOLDER = 'sites'

# App Logo
LOGO_FILE = 'logo.png'

# About Info
README_ABOUT = 'ABOUT.md'
GITHUB_URL = 'https://github.com/vicenteaguero/b2b-client-prospecting'
REPORT_URL_MAIL = 'mailto:vicenteaguero@uc.cl'

################################################################################

# Paths
BASE_PATH = os.path.join(os.path.dirname(__file__), '..', '..')
DATA_PATH = os.path.join(BASE_PATH, DATA_FOLDER)
ASSETS_PATH = os.path.join(BASE_PATH, ASSETS_FOLDER)

# App Path
APP_PATH = os.path.join(BASE_PATH, APP_NAME)

# Paths
PATHS = {
    'logo': os.path.join(ASSETS_PATH, LOGO_FILE),
    'readme_about': os.path.join(APP_PATH, README_ABOUT),
    'pages': {
        os.path.splitext(x)[0]: os.path.join(APP_PATH, PAGES_FOLDER, x)
        for x in os.listdir(os.path.join(APP_PATH, PAGES_FOLDER))
    }
}

################################################################################

# About Text
with open(PATHS['readme_about']) as f:
    ABOUT_TEXT = f.read()
