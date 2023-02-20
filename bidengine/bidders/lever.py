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

PLATFORM = "lever"

def autofill(field: WebElement, answer):
    input_elements = list(filter(lambda x: x.get_attribute("type") != "hidden", field.find_elements(By.TAG_NAME, 'input')))
    if len(input_elements) > 0:
        input = input_elements[0]
        if input.get_attribute("type") == "radio":
            radio_elements = [ element for element in input_elements if element.get_attribute("type") == "radio" ]
            radio_values = [ element.get_attribute("value").lower() for element in radio_elements ]
            for ans in answer:
                for (radio_index, radio_value) in enumerate(radio_values):
                    if is_correct_answer(radio_value, [ans]):
                        radio_elements[radio_index].click()
                        return radio_value
        elif input.get_attribute("type") == "text" or input.get_attribute("type") == "email" or input.get_attribute("type") == "file":
            if type(answer) == bool:
                answer = [ "Yes" if answer is True else "No" ]
            input.clear()
            input.send_keys(answer[0])
            return answer[0]
        elif input.get_attribute("type") == "checkbox":
            checkbox_elements = [ element for element in input_elements if element.get_attribute("type") == "checkbox" ]
            if len(checkbox_elements) == 1:
                if answer[0] is True:
                    input.click()
                    return True
                return False
            elif len(checkbox_elements) > 1:
                checkbox_values = [ element.get_attribute("value").lower() for element in checkbox_elements ]
                for (checkbox_index, checkbox_value) in enumerate(checkbox_values):
                    if is_correct_answer(checkbox_value, answer):
                        checkbox_elements[checkbox_index].click()
                        return checkbox_value
                        
        return None
    
    select_elements = field.find_elements(By.TAG_NAME, 'select')
    if len(select_elements) > 0:
        select = select_elements[0]
        options = select.find_elements(By.TAG_NAME, 'option')
        option_values = [ option.text.lower() for option in options ]
        for ans in answer:
            for (option_index, option_value) in enumerate(option_values):
                if is_correct_answer(option_value, [ans]):
                    options[option_index].click()
                    return option_value
        return None

    textarea_elements = field.find_elements(By.TAG_NAME, 'textarea')
    if len(textarea_elements) > 0:
        textarea = textarea_elements[0]
        textarea.clear()
        textarea.send_keys(answer[0])
        return answer[0]
    return None


def bid(driver: webdriver.Chrome, url: str, job_id: str):
    form_element = driver.find_element(By.TAG_NAME, "form")
    question_elements = form_element.find_elements(By.CLASS_NAME, "application-question")
    unknown_questions = []

    driver.execute_script('document.getElementsByClassName("main-header")[0].setAttribute("style", "display: none")')

    question_index = 0
    while True:
        if question_index == len(question_elements):
            break
        element = question_elements[question_index]
        question_index = question_index + 1

        field = None
        try:
            field = element.find_element(By.CLASS_NAME, "application-field")
        except: continue
        try:
            label = element.find_element(By.CLASS_NAME, "application-label")
            question = label.text.replace("✱", "").replace("\n", "").strip()
        except:
            field = element.find_element(By.CLASS_NAME, "application-field")
            question = ""

            labels = field.find_elements(By.CLASS_NAME, "application-answer-alternative")
            if len(labels) > 0:
                question = labels[0].text.splitlines()[0]
            question = question.replace("✱", "").replace("\n", "").strip()

        if question == "":
            continue
        answer = get_answer(PLATFORM, question, job_id)
        if answer is None:
            log_unknown_question(PLATFORM, question, url, job_id)
            unknown_questions.append(question)
            continue

        print(question, " : ", answer)


        try:
            dismiss_element = driver.find_element(By.CLASS_NAME, "cc-dismiss")
            dismiss_element.click()
        except:
            pass

        actual_answer = autofill(field, answer)
        register_bid_qa(job_id, PLATFORM, question, actual_answer)

        current_question_elements = form_element.find_elements(By.CLASS_NAME, "application-question")
        for elm in question_elements:
            if elm in current_question_elements:
                current_question_elements.remove(elm)
        question_elements.extend(current_question_elements)

    additions = form_element.find_elements(By.CLASS_NAME, "application-additional")
    if len(additions) > 0:
        autofill(additions[0], get_answer(PLATFORM, "Cover letter", job_id))
            
    if len(unknown_questions) > 0:
        raise Exception("Has unknown question: \n" + "\n".join(unknown_questions))

    driver.execute_script('document.getElementsByClassName("main-header")[0].setAttribute("style", "display: block")')

    captchas = form_element.find_elements(By.CLASS_NAME, "h-captcha")
    if len(captchas) > 0:
        raise Exception("Human check required")
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
            if parse_result.path.endswith("lever-confirmation-page"):
                break
        except selenium.common.exceptions.InvalidSessionIdException as e:
            break
        except:
            break
    time.sleep(1)
    return ""