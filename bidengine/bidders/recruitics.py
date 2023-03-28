from operator import truediv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.shadowroot import ShadowRoot
from selenium.webdriver.common.keys import Keys
from utils.answers import get_answer, is_correct_answer, normalize_text
from utils.logger import log_unknown_question
import time
import selenium
from urllib.parse import urlparse
import glvar
from utils.db import register_bid_qa

PLATFORM = "recruitics"
previous_page = ""

def autofill(field: WebElement, answer):
    if field.tag_name == "input" and (field.get_attribute("type") == "" or field.get_attribute("type") == "text" or field.get_attribute("type") == "email"):
        initial_value = field.get_attribute("value")
        if initial_value == "":
            field.send_keys(answer[0])
        return answer[0]
    if field.tag_name == "textarea":
        initial_value = field.get_attribute("value")
        if initial_value == "":
            field.send_keys(answer[0])
        return answer[0]
    if field.tag_name == "input" and field.get_attribute("type") == "checkbox":
        if True in answer:
            field.click()
            return True
        return False
    if field.tag_name == "select":
        options = []
        while True:
            options = field.find_elements(By.TAG_NAME, 'option')
            if len(options) > 0:
                break
        option_values = [ option.text.lower() for option in options ]
        for ans in answer:
            for (option_index, option_value) in enumerate(option_values):
                if is_correct_answer(option_value, [ans]):
                    options[option_index].click()
                    return option_value
    return None


def pre_step1(driver: webdriver.Chrome, url: str):
    apply_button = None
    while True:
        try:
            apply_button = driver.find_element(By.CSS_SELECTOR, "a[ph-tevent='apply_click']")
            apply_button.click()
            print("clicked")
            return True
        except: pass
        time.sleep(1)

def step_main(driver: webdriver.Chrome, url: str, job_id: str):
    form_element = None
    while True:
        try:
            form_element = driver.find_element(By.CLASS_NAME, "formData")
            break
        except: pass
    print("formData")
    
    unknown_questions = []

    try:
        question = "resume"
        answer = get_answer(PLATFORM, question, job_id)
        if answer is None:
            log_unknown_question(PLATFORM, question, url, job_id)
            unknown_questions.append(question)
        else:
            print(question, " : ", answer)
            resume_element = driver.find_element(By.CLASS_NAME, "dz-hidden-input")
            resume_element.send_keys(answer[0])
            register_bid_qa(job_id, PLATFORM, question, answer[0])
    except: pass
    print("resume")

    group_elements = form_element.find_elements(By.CLASS_NAME, "form-group")

    time.sleep(1)
    while True:
        overlay_element = driver.find_element(By.CLASS_NAME, "overlaybg")
        if not overlay_element.is_displayed():
            break
    print("overlay")

    for group_element in group_elements:
        class_list = group_element.get_attribute('class').split(" ")
        question = ""
        target_element = None
        if "border-form" in class_list:
            pass
            # checkbox_elements = group_element.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
            # for checkbox_element in checkbox_elements:
            #     checkbox_elements.click()
            # continue
        else:
            try:
                label_element = group_element.find_element(By.CSS_SELECTOR, "label[class='control-label']")
            except:
                sub_elements = group_element.find_elements(By.ID, "salaryType")
                if len(sub_elements) > 0:
                    question = "salary type"
                    yearly_checkbox = sub_elements[0].find_element(By.CSS_SELECTOR, "input[value='Yearly']")
                    yearly_checkbox.click()
                continue
            
            if "mobileNumber" in class_list:
                question = "Phone"
            elif "mobileType" in class_list:
                question = "MobileType"
            else:
                question = normalize_text(label_element.text)

            
            target_id = label_element.get_attribute("for")
            if target_id == "Email":
                target_id = "username"
            elif target_id == "Phone":
                target_id = "mobileNumber"
            
            target_element = group_element.find_element(By.NAME, target_id)

        if question == "":
            continue
        answer = get_answer(PLATFORM, question, job_id)
        if answer is None:
            log_unknown_question(PLATFORM, question, url, job_id)
            unknown_questions.append(question)
            continue

        print(question, " : ", answer)
        
        actual_answer = autofill(target_element, answer)
        register_bid_qa(job_id, PLATFORM, question, actual_answer)
    
    if len(unknown_questions) > 0:
        raise Exception("Has unknown question: \n" + "\n".join(unknown_questions))
    
    # submit_button = driver.find_element(By.ID, "submit")
    # retry = 5
    # while retry:
    #     try:
    #         submit_button.click()
    #         return
    #     except: pass
    #     retry = retry - 1
    #     time.sleep(1)
    # raise Exception("Cannot click submit button")

def bid(driver: webdriver.Chrome, url: str, job_id: str):
    parsed_url = urlparse(driver.current_url)
    if not parsed_url.path.startswith("/apply"):
        print("not apply")
        if not pre_step1(driver, url):
            print("step")
            return
        print("Passed pre_step1")

    step_main(driver, url, job_id)

def wait_for_apply(driver: webdriver.Chrome, original_url: str):
    while True:
        if glvar.terminate_url == original_url: return "rebid"
        try:
            if len(driver.window_handles) == 0:
                break
                
            parse_result = urlparse(driver.current_url)
            if parse_result.path.startswith("/application-submitted"):
                break

            apply_wrappers = driver.find_elements(By.TAG_NAME, "apply-button-wc")
            if len(apply_wrappers) > 0:
                shadow_root: ShadowRoot = driver.execute_script("return arguments[0].shadowRoot", apply_wrappers[0])
                submitted_elements = shadow_root.find_elements(By.CLASS_NAME, "application-submitted")
                if len(submitted_elements) > 0:
                    break
        except selenium.common.exceptions.InvalidSessionIdException as e:
            break
        time.sleep(1)
    time.sleep(1)
    return ""