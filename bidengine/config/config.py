
current_profile_id = 1

WORKSPACE_PATH = '/Volumes/Data/local_db'
DEFAULT_RESUME_PATH = '/Volumes/Work/resume/pure_frontend/Resume-Michael-Chilelli.pdf'
DEFAULT_COVER_LETTER_PATH = '/Volumes/Work/resume/pure_frontend/MC-cover-letter.pdf'

LOG_PATH = './log'
LOG_BID_PATH = f'{LOG_PATH}/bin'
LOG_RESUME_PATH = f'{LOG_PATH}/resume'
SERVICE_URL = "http://localhost:7000"
PY_SERVICE_URL = "http://localhost:7001"
DASHBOARD_URL = "http://localhost:6991"
BIDDER_PORT = 6990

def set_current_profile(profile_id):
    global current_profile_id
    current_profile_id = profile_id