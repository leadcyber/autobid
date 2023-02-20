from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from utils.answers import get_answer, is_correct_answer
from utils.logger import log_unknown_question

import selenium
from urllib.parse import urlparse
import time
import glvar
from utils.db import register_bid_qa

PLATFORM = "newrelic"

def autofill(field: WebElement, answer):
    if field.tag_name == "input":
        if len(answer) > 0:
            field.send_keys(answer[0])
            return answer[0]
    return None

def autofill_legend(container: WebElement, field_name: str, answer):
    elements = container.find_elements(By.CSS_SELECTOR, f"[aria-labelledby='{field_name}']")
    print(elements[0].get_attribute("type"))
    if len(elements) == 0:
        return None
    if elements[0].get_attribute("type") == "radio":
        radio_items = []
        for radio_element in elements:
            radio_id = radio_element.get_attribute("id")
            radio_label_element = container.find_element(By.CSS_SELECTOR, f"[for='{radio_id}']")
            radio_items.append((radio_label_element, radio_label_element.text))
        for ans in answer:
            for radio_item in radio_items:
                if is_correct_answer(radio_item[1], [ans]):
                    radio_item[0].click()
                    return radio_item[1]
    return None

def bid(driver: webdriver.Chrome, url: str, job_id: str):
    form_element = driver.find_element(By.TAG_NAME, "form")
    label_elements = form_element.find_elements(By.CSS_SELECTOR, "label")
    unknown_questions = []

    for label_element in label_elements:
        field_id = label_element.get_attribute("for")
        label_id = label_element.get_attribute("id")
        if field_id is None or label_id is None or label_id == "":
            continue
        label = label_element.text
        question = label.replace("*", "").replace("\n", "").strip()
        container = label_element.find_element(By.XPATH, "..")

        answer = get_answer(PLATFORM, question, job_id)
        if answer is None:
            log_unknown_question(PLATFORM, question, url, job_id)
            unknown_questions.append(question)
            continue
        
        print(question, " : ", answer)
        actual_answer = None
        if question == "Upload file":
            actual_answer = autofill(container.find_element(By.NAME, f"file_{field_id}"), answer)
        else:
            actual_answer = autofill(container.find_element(By.NAME, field_id), answer)
        register_bid_qa(job_id, PLATFORM, question, actual_answer)

    legend_elements = form_element.find_elements(By.TAG_NAME, "legend")
    for legend_element in legend_elements:
        label_id = legend_element.get_attribute("id")
        if label_id is None or label_id == "":
            continue
        label = legend_element.text
        question = label.replace("*", "").replace("\n", "").strip()
        if question == "":
            continue
        field_name = legend_element.get_attribute("id")
        container = legend_element.find_element(By.XPATH, "..")

        answer = get_answer(PLATFORM, question, job_id)
        if answer is None:
            log_unknown_question(PLATFORM, question, url, job_id)
            unknown_questions.append(question)
            continue
        
        print(question, " : ", answer)
        actual_answer = autofill_legend(container, field_name, answer)
        register_bid_qa(job_id, PLATFORM, question, actual_answer)
    
    if len(unknown_questions) > 0:
        raise Exception("Has unknown question: \n" + "\n".join(unknown_questions))
    form_element.submit()


def wait_for_apply(driver: webdriver.Chrome, original_url: str):
    while True:
        if glvar.terminate_url == original_url: return "rebid"
        try:
            if len(driver.window_handles) == 0:
                break
            
            parse_result = urlparse(driver.current_url)
            if parse_result.path.endswith("thanks"):
                break
        except selenium.common.exceptions.InvalidSessionIdException as e:
            break
        except:
            break
    time.sleep(1)
    return ""


def is_resumator(driver: webdriver.Chrome) -> bool:
    try:
        driver.find_element(By.CLASS_NAME, "job-form-fields")
        return True
    except:
        return False