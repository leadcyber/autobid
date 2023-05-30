from autobid.env import WORKSPACE_PATH
import os

RESUME_TEMPLATE_PATH = f'{WORKSPACE_PATH}/resume'

SENTENCE_DB_CACHE_TTL = 1
TEMPLATE_CACHE_TTL = 180

TEMP_PATH = f'{WORKSPACE_PATH}/temp'

# LIBREOFFICE_PATH = f'{os.getcwd()}/../bin/LibreOffice.app'
LIBREOFFICE_PATH = '/Applications/LibreOffice.app'