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

PLATFORM = "jobvite"

def autofill(field: WebElement, driver: webdriver.Chrome, answer):
    field_type = field.tag_name
    if field_type == "fieldset":
        input_type = field.get_attribute("ng-switch-when")
        if input_type == "checkbox":
            if answer is True:
                field.click()
                return True
            else: return False
        if input_type == "radio":
            radios = field.find_elements(By.TAG_NAME, "input")
            radio_values = [ radio.find_element(By.XPATH, "..").text.lower() for radio in radios ]
            print(radio_values)
            for ans in answer:
                for (radio_index, radio_value) in enumerate(radio_values):
                    if is_correct_answer(radio_value, [ans]):
                        driver.execute_script("arguments[0].click()",radios[radio_index])
                        return radio_value
        return None
    elif field_type == "input":
        input_type = field.get_attribute("type")
        if input_type == "checkbox":
            if answer is True:
                field.click()
                return True
            else:
                return False
        else:
            field.send_keys(answer[0])
            return answer[0]
    elif field_type == "select":
        options = field.find_elements(By.TAG_NAME, 'option')
        option_values = [ option.text.lower() for option in options ]
        for ans in answer:
            for (option_index, option_value) in enumerate(option_values):
                if is_correct_answer(option_value, [ans]):
                    options[option_index].click()
                    return option_value
        return None
    return None

def bid(driver: webdriver.Chrome, url: str, job_id: str):

    form_element = None
    while True:
        form_elements = driver.find_elements(By.CSS_SELECTOR, "form[name$='applyForm']")
        if len(form_elements) > 0:
            form_element = form_elements[0]
            break
        time.sleep(1)
    unknown_questions = []

    label_elements = form_element.find_elements(By.TAG_NAME, "label")
    for label_element in label_elements:
        target_id = label_element.get_attribute("for")
        if target_id is None or target_id == "":
            continue
        field = form_element.find_element(By.ID, target_id)

        if field.get_attribute("type") == "radio":
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

        actual_answer = autofill(field, driver, answer)
        register_bid_qa(job_id, PLATFORM, question, actual_answer)

    resume_elements = form_element.find_elements(By.CSS_SELECTOR, "button[attachment-label='Resume']")
    if len(resume_elements) > 0:
        resume_elements[0].click()
        upload_elements = driver.find_elements(By.CSS_SELECTOR, "div[ng-show='visible.fileUpload']")
        for upload_element in upload_elements:
            parent = upload_element.find_element(By.XPATH, "..")
            parent_class = parent.get_attribute("class")
            if parent_class.find("ng-hide") < 0:
                question = "Resume/CV"
                answer = get_answer(PLATFORM, question, job_id)
                if answer is None:
                    log_unknown_question(PLATFORM, question, url, job_id)
                    unknown_questions.append(question)
                    continue
                actual_answer = autofill(upload_element.find_element(By.TAG_NAME, "input"), driver, answer)
                register_bid_qa(job_id, PLATFORM, question, actual_answer)
                break

    time.sleep(1)
    resume_loading = form_element.find_element(By.CSS_SELECTOR, "span[ng-show='resumeLoading']")
    while True:
        if resume_loading.get_attribute("class").find("ng-hide") >= 0:
            break
        time.sleep(1)
            
    if len(unknown_questions) > 0:
        raise Exception("Has unknown question: \n" + "\n".join(unknown_questions))

    form_element.find_element(By.CSS_SELECTOR, "button[aria-label='Next']").click()
    time.sleep(1)

    label_elements = form_element.find_elements(By.TAG_NAME, "label")
    for label_element in label_elements:
        target_id = label_element.get_attribute("for")
        if target_id is None or target_id == "":
            continue
        field = form_element.find_element(By.ID, target_id)

        if field.get_attribute("type") == "radio":
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

        actual_answer = autofill(field, driver, answer)
        register_bid_qa(job_id, PLATFORM, question, actual_answer)

    legend_elements = form_element.find_elements(By.TAG_NAME, "legend")
    for legend_element in legend_elements:
        fieldset_element = legend_element.find_element(By.XPATH, "..")

        question = legend_element.text.replace("*", "").strip()
        if question == "":
            continue
        answer = get_answer(PLATFORM, question, job_id)
        if answer is None:
            log_unknown_question(PLATFORM, question, url, job_id)
            unknown_questions.append(question)
            continue

        print(question, " : ", answer)

        actual_answer = autofill(fieldset_element, driver, answer)
        register_bid_qa(job_id, PLATFORM, question, actual_answer)
    
    if len(unknown_questions) > 0:
        raise Exception("Has unknown question: \n" + "\n".join(unknown_questions))
    
    form_element.find_element(By.CSS_SELECTOR, "button[aria-label='Send Application']").click()

def wait_for_apply(driver: webdriver.Chrome, original_url: str):
    while True:
        if glvar.terminate_url == original_url: return "rebid"
        try:
            if len(driver.window_handles) == 0:
                break
            
            parse_result = urlparse(driver.current_url)
            if parse_result.path.endswith("applyConfirmation"):
                break
        except selenium.common.exceptions.InvalidSessionIdException as e:
            break
        except:
            break
    time.sleep(1)
    return ""