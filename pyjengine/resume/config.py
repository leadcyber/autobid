from config import WORKSPACE_PATH
import os

RESUME_TEMPLATE_PATH = f'{WORKSPACE_PATH}/resume'

SENTENCE_DB_CACHE_TTL = 1
TEMPLATE_CACHE_TTL = 180

RANK_RESERVATION_RATE = 0.5

TEMP_PATH = f'{WORKSPACE_PATH}/temp'

LIBREOFFICE_PATH = f'{os.getcwd()}/../bin/LibreOffice.app'