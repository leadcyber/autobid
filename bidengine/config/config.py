
current_profile_id = 1

LOG_PATH = './log'
LOG_BID_PATH = f'{LOG_PATH}/bin'
LOG_RESUME_PATH = f'{LOG_PATH}/resume'


def set_current_profile(profile_id):
    global current_profile_id
    current_profile_id = profile_id