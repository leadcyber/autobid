from operator import truediv
from xmlrpc.client import Boolean
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from utils.answers import get_answer, is_correct_answer
from utils.logger import log_unknown_question
import time
import selenium
from urllib.parse import urlparse
import glvar

PLATFORM = "icims"
previous_page = ""

def autofill(field: WebElement, driver: webdriver.Chrome, answer):
    if (field.tag_name == "" or field.tag_name == "input") and \
        (field.get_attribute("type") == "text" or field.get_attribute("type") == "email"\
             or field.get_attribute("type") == "file"\
                 ):
        field.clear()
        field.send_keys(answer[0])
        return True
    if field.tag_name == "textarea":
        field.clear()
        field.send_keys(answer[0])
        return True
    if field.tag_name == "input" and field.get_attribute("type") == "checkbox":
        if (type(answer) == list and True in answer) or answer is True:
            field.click()
        return True

def step_jd(driver: webdriver.Chrome, url: str):
    while True:
        apply_buttons = driver.find_elements(By.CSS_SELECTOR, "a[title='Apply for this job online']")
        if len(apply_buttons) > 0:
            try:
                apply_buttons[0].click()
                return True
            except:
                pass
        time.sleep(1)

def step_login(driver: webdriver.Chrome, url: str, job_id: str):
    unknown_questions = []
    form_element = None
    while True:
        form_elements = driver.find_elements(By.ID, "enterEmailForm")
        if len(form_elements) > 0:
            form_element = form_elements[0]
            break
        time.sleep(1)

    email_element = form_element.find_element(By.ID, "email")

    question = "Login"
    answer = get_answer(PLATFORM, question)
    if answer is None:
        log_unknown_question(PLATFORM, question, url, job_id)
        unknown_questions.append(question)
    else:
        email_element.send_keys(answer)

    try:
        accept_checkbox = driver.find_element(By.ID, "accept_privacy")
        accept_checkbox.click()
    except:
        pass

    try:
        accept_checkbox = driver.find_element(By.ID, "accept_gdpr")
        accept_checkbox.click()
    except:
        pass
        
    if len(unknown_questions) > 0:
        raise Exception("Has unknown question: \n" + "\n".join(unknown_questions))
    
    submit_button = form_element.find_element(By.ID, "enterEmailSubmitButton")
    submit_button.click()

def wait_for_next_step(driver: webdriver.Chrome):
    global previous_page
    page_contents = []
    while True:
        page_contents = driver.find_elements(By.CLASS_NAME, "iCIMS_CenteredPageContent")
        if len(page_contents) > 0:
            try:
                h2_element = page_contents[0].find_element(By.TAG_NAME, "h2")
                if h2_element.text != previous_page:
                    previous_page = h2_element.text
                    break
            except: pass
        time.sleep(1)
    time.sleep(1)
    return page_contents[0]

def step_main(driver: webdriver.Chrome, page_content: WebElement, url: str, job_id: str):
    h2_elements = page_content.find_elements(By.TAG_NAME, "h2")
    for h2_element in h2_elements:
        subtitle = h2_element.text
        if subtitle == "Candidate Profile": continue
        
        content_element = h2_element.find_element(By.XPATH, "..")
        if subtitle == "Work Experience":
            fill_work_history(driver, content_element, url)
        else:
            fill_normal_section(driver, content_element, url, job_id)
    next_button = driver.find_element(By.ID, "cp_form_submit_i")
    next_button.click()

def fill_work_history(driver: webdriver.Chrome, page_content: WebElement, url: str):
    unknown_questions = []
    fieldset_elements = page_content.find_elements(By.TAG_NAME, "fieldset")
    for (index, fieldset_element) in enumerate(fieldset_elements):
        pass

    if len(unknown_questions) > 0:
        raise Exception("Has unknown question: \n" + "\n".join(unknown_questions))

def fill_normal_section(driver: webdriver.Chrome, page_content: WebElement, url: str, job_id: str):
    unknown_questions = []
    label_elements = page_content.find_elements(By.TAG_NAME, "label")
    label_index = 0
    while True:
        if label_index == len(label_elements):
            break
        label_element = label_elements[label_index]
        label_index = label_index + 1
        try:
            target_id = label_element.get_attribute("for")
        except: continue
        if target_id is None or target_id == "":
            continue
        else:
            try:
                target_element = page_content.find_element(By.ID, target_id)
            except: continue
        
        question = label_element.text
        if question == "": continue
        if question == "My Computer (Opens new window)": continue
        if target_id == "resume_skip_checkbox": continue

        if target_id.endswith(".PhoneType"):
            question = "Phone Type"
        if target_id.endswith(".PhoneNumber"):
            question = "Phone Number"
        answer = get_answer(PLATFORM, question, job_id)
        if answer is None:
            log_unknown_question(PLATFORM, question, url, job_id)
            unknown_questions.append(question)
            continue

        print(question, " : ", answer)

        autofill(target_element, driver, answer)

        current_label_elements = page_content.find_elements(By.TAG_NAME, "label")
        for elm in label_elements:
            if elm in current_label_elements:
                current_label_elements.remove(elm)
        label_elements.extend(current_label_elements)

    if len(unknown_questions) > 0:
        raise Exception("Has unknown question: \n" + "\n".join(unknown_questions))
    

def bid(driver: webdriver.Chrome, url: str, job_id: str):
    while True:
        iframe_elements = driver.find_elements(By.ID, "icims_content_iframe")
        if len(iframe_elements) > 0:
            iframe_element = iframe_elements[0]
            break
        time.sleep(1)
    
    driver.switch_to.frame(iframe_element)

    parsed_url = urlparse(driver.current_url)
    if parsed_url.path.endswith("/job"):
        step_jd(driver, url)
        print("Passed JD step")

        while True:
            parsed_url = urlparse(driver.current_url)
            if parsed_url.path.endswith("/login"):
                break

    parsed_url = urlparse(driver.current_url)
    if parsed_url.path.endswith("/login"):
        step_login(driver, url, job_id)
        print("Passed login step")

    global previous_page
    previous_page = ""

    while True:
        content_page = wait_for_next_step(driver)
        print("Passed", previous_page)
        try:
            step_main(driver, content_page, url, job_id)
        except Exception as e:
            print("")
            print(e)
            print("")

def wait_for_apply(driver: webdriver.Chrome, original_url: str):
    while True:
        if glvar.terminate_url == original_url: return "rebid"
        try:
            if len(driver.window_handles) == 0:
                break

            success_elements = driver.find_elements(By.CSS_SELECTOR, "div[data-automation-id='congratulationsPopup']")
            if len(success_elements) > 0:
                break
            # success_elements = driver.find_elements(By.CLASS_NAME, "wd-icon-check-circle")
            # if len(success_elements) > 0:
            #     break
        except selenium.common.exceptions.InvalidSessionIdException as e:
            break
        time.sleep(1)
    time.sleep(1)
    return ""