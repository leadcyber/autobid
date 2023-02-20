from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from utils.answers import get_answer
from utils.logger import log_unknown_question
import time
import selenium
from urllib.parse import urlparse
import glvar
from utils.db import register_bid_qa

PLATFORM = "dover"

def autofill(field: WebElement, answer):
    if field.tag_name == "input":
        input_type = field.get_attribute("type")
        if input_type == "text" or input_type == "" or input_type == "textarea" or input_type == "file" or input_type == "email" or input_type == "tel":
            field.send_keys(answer[0])
            return answer[0]
    return None


def bid(driver: webdriver.Chrome, url: str, job_id: str):
    form_element = None
    while True:
        form_elements = driver.find_elements(By.TAG_NAME, "form")
        if len(form_elements) > 0:
            form_element = form_elements[0]
            break
        time.sleep(1)
    time.sleep(1)

    unknown_questions = []

    lable_elements = form_element.find_elements(By.TAG_NAME, "label")
    for label_element in lable_elements:
        label = label_element.text
        question = label.replace("*", "").replace("\n", "").strip()
        if question == "":
            continue
        answer = get_answer(PLATFORM, question, job_id)
        if answer is None:
            log_unknown_question(PLATFORM, question, url, job_id)
            unknown_questions.append(question)
            continue

        pair_container = label_element.find_element(By.XPATH, "..")
        try:
            input_element = pair_container.find_element(By.TAG_NAME, "input")
            actual_answer = autofill(input_element, answer)
            register_bid_qa(job_id, PLATFORM, question, actual_answer)
        except: pass

    if len(unknown_questions) > 0:
        raise Exception("Has unknown question: " + "\n".join(unknown_questions))

    submit_button = form_element.find_element(By.CSS_SELECTOR, "button[type='submit']")
    submit_button.click()

def wait_for_apply(driver: webdriver.Chrome, original_url: str):
    while True:
        if glvar.terminate_url == original_url: return "rebid"
        try:
            if len(driver.window_handles) == 0:
                break
            
            success_elements = driver.find_elements(By.XPATH, "//div[contains(text(), 'Thanks for applying!')]")
            if len(success_elements) > 0:
                break
        except selenium.common.exceptions.InvalidSessionIdException as e:
            break
        time.sleep(1)
    time.sleep(1)
    return ""