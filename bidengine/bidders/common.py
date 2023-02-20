import selenium
from selenium import webdriver
import time
import glvar

def wait_window_close(driver: webdriver.Chrome, original_url: str):
    while True:
        if glvar.terminate_url == original_url: return "rebid"
        try:
            if len(driver.window_handles) == 0: break
        except selenium.common.exceptions.InvalidSessionIdException as e:
            break
        time.sleep(1)
    return ""