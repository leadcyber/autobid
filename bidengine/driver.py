from copyreg import constructor
import numbers
from xmlrpc.client import boolean
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from config import config
import requests
from ast import literal_eval

incogniton_profile_id = '59d3328c-078b-48c3-b343-065a56d5e236'

class ProfileState:
    def __init__(self, group: str = "", state: int = 0) -> None:
        self.group = group
        self.state = state

def _create_remote_driver():
    try:
        stop_url = 'http://127.0.0.1:35000/profile/stop/'+incogniton_profile_id
        resp = requests.get(stop_url)
        print(resp)
    except:
        print("Failed to stop")
        
    incogniton_url = 'http://127.0.0.1:35000/automation/launch/python/'+incogniton_profile_id
    resp = requests.get(incogniton_url)
    incomingJson = resp.json()
    if incomingJson["status"] == "error":
        raise Exception("Cannot connect")
    return webdriver.Remote(
                command_executor = incomingJson['url'],
                desired_capabilities = literal_eval(incomingJson['dataDict']) )

remote_driver = None
profile_usage = [0] * 4
profile_state = [
{
    "linkedin_0": ProfileState(group="linkedin", state=0),
    "linkedin_1": ProfileState(group="linkedin", state=0),
    "linkedin_2": ProfileState(group="linkedin", state=0),
    "linkedin_3": ProfileState(group="linkedin", state=0),
    "linkedin_4": ProfileState(group="linkedin", state=0),
    "linkedin_5": ProfileState(group="linkedin", state=0),
    "linkedin_6": ProfileState(group="linkedin", state=0),
    "linkedin_7": ProfileState(group="linkedin", state=0),
    "linkedin_8": ProfileState(group="linkedin", state=0),
    "indeed_0": ProfileState(group="indeed", state=0),
    "0": ProfileState(group="", state=0),
    "1": ProfileState(group="", state=0),
    "2": ProfileState(group="", state=0),
    "3": ProfileState(group="", state=0),
    "4": ProfileState(group="", state=0),
}
]

def create_remote_driver() -> webdriver.Chrome:
    global remote_driver
    try:
        _ = remote_driver.current_url
    except:
        try:
            remote_driver.quit()
        except: pass
        remote_driver = _create_remote_driver()
    return remote_driver

def get_free_profile(group_name):
    current_profile_state = profile_state[config.current_profile_id - 1]
    for name in current_profile_state:
        if current_profile_state[name].group == group_name and current_profile_state[name].state == 0:
            return name
    raise Exception("No free profile")
def set_profile_state(profile_name: str, state: int):
    current_profile_state = profile_state[config.current_profile_id - 1]
    current_profile_state[profile_name].state = state
def is_profile_free(profile_name: str):
    current_profile_state = profile_state[config.current_profile_id - 1]
    return current_profile_state[profile_name].state == 0

def should_block_image(parse_result):
    if parse_result.netloc.endswith("lever.co"):
        return False
    return True

def create_direct_driver(profile_name: str, block_image: bool = True) -> webdriver.Chrome:
    chrome_options = Options()
    if block_image is True:
        chrome_options.add_extension('../bin/Block image 1.1.0.0.crx')
    chrome_options.add_argument('--disable-features=OptimizationGuideModelDownloading,OptimizationHintsFetching,OptimizationTargetPrediction,OptimizationHints')
    chrome_options.add_argument('user-data-dir=profiles/profile_' + str(config.current_profile_id) + "/" + profile_name)

    return webdriver.Chrome(executable_path="../bin/chromedriver", chrome_options=chrome_options)