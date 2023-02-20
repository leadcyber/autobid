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

PLATFORM = "resumator"

def autofill(field: WebElement, answer):
    if field.tag_name == "input" or field.tag_name == "textarea":
        field.send_keys(answer[0])
        return answer[0]
    elif field.tag_name == "select":
        options = field.find_elements(By.TAG_NAME, 'option')
        option_values = [ option.text.lower() for option in options ]
        for ans in answer:
            for (option_index, option_value) in enumerate(option_values):
                if is_correct_answer(option_value, [ans]):
                    options[option_index].click()
                    return option_value
        return None
    


def bid(driver: webdriver.Chrome, url: str, job_id: str):
    form_element = driver.find_element(By.CLASS_NAME, "job-form-fields")
    label_elements = form_element.find_elements(By.TAG_NAME, "label")
    unknown_questions = []

    for label_element in label_elements:
        label_text = label_element.text
        input_id = label_element.get_attribute("for")

        if input_id is None or input_id == "":
            continue

        question = label_text.replace("*", "").strip()
        if question == "Address":
            street = get_answer(PLATFORM, "Street Address")
            register_bid_qa(job_id, PLATFORM, question, street)
            if street is None:
                log_unknown_question(PLATFORM, question, url, job_id)
                unknown_questions.append(question)
            else:
                print("Street Address", " : ", street)
                actual_answer = autofill(form_element.find_element(By.ID, input_id), street)

            city = get_answer(PLATFORM, "City")
            if city is None:
                log_unknown_question(PLATFORM, question, url, job_id)
                unknown_questions.append(question)
            else:
                print("City", " : ", city)
                autofill(form_element.find_element(By.ID, "resumator-city-value"), city)

            state = get_answer(PLATFORM, "State")
            if state is None:
                log_unknown_question(PLATFORM, question, url, job_id)
                unknown_questions.append(question)
            else:
                print("State", " : ", state)
                autofill(form_element.find_element(By.ID, "resumator-state-value"), state)

            postal = get_answer(PLATFORM, "Postal Code")
            if postal is None:
                log_unknown_question(PLATFORM, question, url, job_id)
                unknown_questions.append(question)
            else:
                print("Postal Code", " : ", postal)
                autofill(form_element.find_element(By.ID, "resumator-postal-value"), postal)

        else:
            target_element = form_element.find_element(By.ID, input_id)
            if target_element is None:
                continue
            if target_element.tag_name == "input" and target_element.get_attribute("type") == "checkbox":
                continue
            answer = get_answer(PLATFORM, question, job_id)
            if answer is None:
                log_unknown_question(PLATFORM, question, url, job_id)
                unknown_questions.append(question)
                continue
            print(question, " : ", answer)
            if question == "Resume":
                form_element.find_element(By.ID, "resumator-choose-upload").click()
            actual_answer = autofill(target_element, answer)
            register_bid_qa(job_id, PLATFORM, question, actual_answer)
        
    if len(unknown_questions) > 0:
        raise Exception("Has unknown question: \n" + "\n".join(unknown_questions))

    submit_button = driver.find_element(By.ID, 'resumator-submit-resume')
    submit_button.click()


def wait_for_apply(driver: webdriver.Chrome, original_url: str):
    while True:
        if glvar.terminate_url == original_url: return "rebid"
        try:
            if len(driver.window_handles) == 0:
                break
            
            success_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Your application has been received.')]")
            if len(success_elements) > 0:
                break
        except selenium.common.exceptions.InvalidSessionIdException as e:
            break
        time.sleep(1)
    time.sleep(1)
    return ""


def is_resumator(driver: webdriver.Chrome) -> bool:
    try:
        driver.find_element(By.CLASS_NAME, "job-form-fields")
        return True
    except:
        return False