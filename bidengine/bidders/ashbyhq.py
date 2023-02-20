from distutils.command import check
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from utils.answers import get_answer, is_correct_answer
from utils.logger import log_unknown_question
import time
import selenium
from urllib.parse import urlparse
import glvar
from utils.db import register_bid_qa

PLATFORM = "ashbyhq"

def autofill(parent: WebElement, answer):
    input_elements = None
    input_elements = parent.find_elements(By.TAG_NAME, "input")
    if len(input_elements) == 1:
        input_element = input_elements[0]
        input_type = input_element.get_attribute("type")
        print(input_element, input_type)
        if input_type == "text" or input_type == "email" or input_type == "tel" or input_type == "":
            input_element.send_keys(answer[0])
            return answer[0]
        elif input_type == "file":
            input_element.send_keys(answer[0])
            while True:
                button_elements = parent.find_elements(By.TAG_NAME, "button")
                for button_element in button_elements:
                    if button_element.text == "Replace" and button_element.get_attribute("disabled") != "true":
                        return answer[0]
                time.sleep(1)
        elif input_type == "checkbox":
            check_buttons = parent.find_elements(By.TAG_NAME, "button")
            if len(check_buttons) > 0:
                button_texts = [ button_element.text for button_element in check_buttons ]
                for ans in answer:
                    for (index, button_text) in enumerate(button_texts):
                        if is_correct_answer(button_text, [ans]):
                            check_buttons[index].click()
                            return button_text
    elif len(input_elements) > 1:
        if input_elements[0].get_attribute("type") == "radio":
            input_datas = []
            for input_element in input_elements:
                input_id = input_element.get_attribute("id")
                label_elements = parent.find_elements(By.CSS_SELECTOR, f"label[for='{input_id}']")
                if len(label_elements) == 0: continue
                input_datas.append((label_elements[0].text, input_element))
            for ans in answer:
                for input_data in input_datas:
                    if is_correct_answer(input_data[0], [ans]):
                        input_data[1].click()
                        return input_data[0]
    return None

def bid(driver: webdriver.Chrome, url: str, job_id: str):
    form_element = None
    while True:
        form_elements = driver.find_elements(By.CSS_SELECTOR, "div[class^=\"_jobPostingForm_\"], div[class*=\" _jobPostingForm_\"]")
        if len(form_elements) > 0:
            form_element = form_elements[0]
            break
    unknown_questions = []

    label_elements = form_element.find_elements(By.TAG_NAME, "label")
    for label_element in label_elements:
        target_id = label_element.get_attribute("for")
        parent_field = label_element.find_element(By.XPATH, "..")
        if target_id is not None and target_id != "":
            target_elements = driver.find_elements(By.ID, target_id)
            if len(target_elements) > 0 and target_elements[0].get_attribute("type") == "radio":
                continue

        question = label_element.text.replace("*", "").strip()
        if question == "":
            continue
        answer = get_answer(PLATFORM, question, job_id)
        if answer is None:
            log_unknown_question(PLATFORM, question, url, job_id)
            unknown_questions.append(question)
            continue

        print(question, " : ", answer)

        actual_answer = autofill(parent_field, answer)
        register_bid_qa(job_id, PLATFORM, question, actual_answer)
            
    if len(unknown_questions) > 0:
        raise Exception("Has unknown question: \n" + "\n".join(unknown_questions))

    time.sleep(5)
    submit_buttons = driver.find_elements(By.CSS_SELECTOR, "button[class^=\"_submitButton\"], button[class*=\" _submitButton\"]")
    if len(submit_buttons) > 0:
        submit_buttons[0].click()

def wait_for_apply(driver: webdriver.Chrome, original_url: str):
    while True:
        if glvar.terminate_url == original_url: return "rebid"
        try:
            if len(driver.window_handles) == 0:
                break
            
            success_elements = driver.find_elements(By.XPATH, "//p[contains(text(), 'Thank you for your interest in')]")
            if len(success_elements) > 0:
                break
            success_elements = driver.find_elements(By.XPATH, "//p[contains(text(), 'Your application was successfully submitted')]")
            if len(success_elements) > 0:
                break
        except selenium.common.exceptions.InvalidSessionIdException as e:
            break
        time.sleep(1)
    time.sleep(1)
    return ""