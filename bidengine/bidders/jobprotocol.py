from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from utils.answers import get_answer
from utils.logger import log_unknown_question
import time
import glvar
from utils.db import register_bid_qa

PLATFORM = "jobprotocol"

def autofill_first_page(field: WebElement, answer):
    if field.tag_name == "input":
        field.send_keys(answer[0])
        return answer[0]
    return None

def fill_first_page(driver: webdriver.Chrome, url: str, job_id: str):
    input_elements = driver.find_elements(By.TAG_NAME, "input")
    for input_element in input_elements:
        preceding_sibling = input_element.find_elements(By.XPATH, "preceding-sibling::*")[-1]
        question = preceding_sibling.get_attribute("innerText")
        
        question = question.strip()
        if len(question) == "":
            continue

        answer = get_answer(PLATFORM, question, job_id)
        if answer is None:
            log_unknown_question(PLATFORM, question, url, job_id)
            continue

        print(question, " : ", answer)
        actual_answer = autofill_first_page(input_element, answer)
        register_bid_qa(job_id, PLATFORM, question, actual_answer)
    
    time.sleep(2)
    button_elements = driver.find_elements(By.TAG_NAME, "button")
    for button_element in button_elements:
        if button_element.get_attribute("innerText") == "Submit":
            button_element.click()
            return


def autofill_second_page(field: WebElement, answer):
    if answer[0] is True:
        field.click()
        return True
    if len(answer) > 1:
        parent_element = field.find_element(By.XPATH, "..")
        description_element = parent_element.find_elements(By.XPATH, "following-sibling::*")[0]
        description_element.send_keys(answer[1])
        return answer[1]
    return False

def fill_second_page(driver: webdriver.Chrome, url: str, job_id: str):
    input_elements = driver.find_elements(By.TAG_NAME, "input")
    for input_element in input_elements:
        if input_element.get_attribute("type") != "checkbox":
            continue
        following_sibling = input_element.find_elements(By.XPATH, "following-sibling::*")[0]
        question = following_sibling.get_attribute("innerText")
        
        question = question.strip()
        if len(question) == "":
            continue

        answer = get_answer(PLATFORM, question, job_id)
        if answer is None:
            log_unknown_question(PLATFORM, question, url, job_id)
            continue

        print(question, " : ", answer)
        actual_answer = autofill_second_page(input_element, answer)
        register_bid_qa(job_id, PLATFORM, question, actual_answer)
    
    time.sleep(2)
    button_elements = driver.find_elements(By.TAG_NAME, "button")
    for button_element in button_elements:
        if button_element.get_attribute("innerText") == "Finish":
            button_element.click()
            return

def bid(driver: webdriver.Chrome, url: str, job_id: str):
    fill_first_page(driver, url, job_id)

    previous_count = 0
    while True:
        input_elements = driver.find_elements(By.TAG_NAME, "input")
        checkboxes = list(filter(lambda x: x.get_attribute("type") == "checkbox", input_elements))
        if len(checkboxes) == 0:
            time.sleep(1)
            continue
        if previous_count == len(checkboxes):
            break
        previous_count = len(checkboxes)
        time.sleep(3)

    fill_second_page(driver, url, job_id)

def wait_for_apply(driver: webdriver.Chrome, original_url: str):
    pass