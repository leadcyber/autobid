from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from utils.answers import get_answer, is_correct_answer, is_money_str, money_str2num, normalize_text, find_exact_question
from utils.logger import log_unknown_question
import time
import selenium
from urllib.parse import urlparse
import glvar
from driver import create_remote_driver
from config import config
from utils.db import register_bid_qa

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils import logger
from threading import Thread

PLATFORM = "linkedin"
linked_url_queue = []
invite_message = '''Hi **name**,

I hope you’re doing well! I’m interested in the role you posted: **job-title**. Based on my experience as Senior Software Engineer, I believe I could be a good fit.
I look forward to hearing from you.

Regards,
Michael'''


class LinkedInItem:
    step: str
    url: str
    window: str
    driver: webdriver.Chrome
    def __init__(self, step = "init", url = "", window = None, driver = None):
        self.step = step
        self.url = url
        self.window = window
        self.driver = driver

def autofill(driver: webdriver.Chrome, field: WebElement, input_element: WebElement, answer):
    class_list = field.get_attribute("class").split(" ")
    if field.tag_name == "fieldset":
        # checkboxes = field.find_elements(By.TAG_NAME, 'input')
        label_elements = field.find_elements(By.TAG_NAME, 'label')
        checkbox_values = [ label.text for label in label_elements ]
        for ans in answer:
            for (checkbox_index, checkbox_value) in enumerate(checkbox_values):
                if is_correct_answer(checkbox_value, [ans]):
                    label_elements[checkbox_index].click()
                    return checkbox_value
        return None
    if input_element.tag_name == "input":
        if input_element.get_attribute("value") != answer[0]:
            input_element.clear()
            input_element.send_keys(answer[0])
        try:
            if answer[0] == "Tucson, Arizona":
                time.sleep(1.5)
            typeahead_element = field.find_element(By.CSS_SELECTOR, "div[role='listbox']")
            while True:
                li_elements = typeahead_element.find_elements(By.CSS_SELECTOR, "div[role='option']")
                if len(li_elements) > 0:
                    input_element.send_keys(Keys.ARROW_DOWN)
                    time.sleep(1)
                    input_element.send_keys(Keys.ENTER)
                    break
                time.sleep(0.5)
        except: pass
        return answer[0]
    if input_element.tag_name == "textarea":
        textarea_element = input_element
        if textarea_element.get_attribute("value") != answer[0]:
            textarea_element.clear()
            textarea_element.send_keys(answer[0])
        return answer[0]
    if input_element.tag_name == "select":
        select_element = input_element
        initial_value = select_element.get_attribute("value")
        if initial_value != "" and initial_value != "Select an option":
            return initial_value
        options = field.find_elements(By.TAG_NAME, 'option')
        option_values = [ option.text.lower() for option in options ]
        for ans in answer:
            for (option_index, option_value) in enumerate(option_values):
                if is_correct_answer(option_value, [ans]):
                    options[option_index].click()
                    return option_value
        return None
    if "fb-radio-buttons" in class_list:
        radios = input_element
        label_elements = [ radio.find_element(By.XPATH, "following-sibling::*") for radio in radios ]
        radio_values = [ label.text for label in label_elements ]
        for ans in answer:
            for (radio_index, radio_value) in enumerate(radio_values):
                if is_correct_answer(radio_value, [ans]):
                    label_elements[radio_index].click()
                    return radio_value
        return None
    return None

def get_modal(driver: WebElement):
    while True:
        modal_elements = driver.find_elements(By.CLASS_NAME, "jobs-easy-apply-modal")
        if len(modal_elements) > 0:
            return modal_elements[0]
    
def wait_for_next_step(driver: WebElement):
    global previous_page
    while True:
        modal_element = get_modal(driver)
        try:
            header_element = modal_element.find_element(By.TAG_NAME, "h3")
            if header_element.text != previous_page:
                previous_page = header_element.text
                return modal_element
        except: pass

def try_next(modal_element: WebElement):
    button_element = None
    try:
        button_element = modal_element.find_element(By.CSS_SELECTOR, "footer [data-easy-apply-next-button]")
        button_element.click()
    except:
        button_elements = modal_element.find_elements(By.CSS_SELECTOR, "footer button")
        for btn_element in button_elements:
            button_element = btn_element
            if button_element.text == "Review":
                time.sleep(.5)
                button_element.click()
                break
            elif button_element.text.startswith("Submit"):
                time.sleep(.5)
                button_element.click()
                return True
    return False
def fill_resume(driver: webdriver.Chrome, modal_element: WebElement, url: str, job_id: str, is_log: bool):
    question = "Resume"
    answer = get_answer(PLATFORM, question, job_id)[0]
    if answer is None:
        if is_log is True:
            log_unknown_question(PLATFORM, question, url, job_id)
        return

    upload_element = None
    try:
        upload_element = modal_element.find_element(By.CSS_SELECTOR, ".js-jobs-document-upload__container input[type='file']")
    except:
        remove_buttons = modal_element.find_elements(By.CSS_SELECTOR, ".jobs-document-upload__remove-file button")
        if len(remove_buttons) > 0:
            remove_buttons[0].click()
            upload_element = modal_element.find_element(By.CSS_SELECTOR, ".js-jobs-document-upload__container input[type='file']")
        else:
            return
    upload_element.send_keys(answer)
    register_bid_qa(job_id, PLATFORM, question, answer)
    # resume_labels = resume_list_element.find_elements(By.CSS_SELECTOR, ".jobs-resume-picker__resume .jobs-resume-picker__resume-label")
    # resume_choose_buttons = resume_list_element.find_elements(By.CSS_SELECTOR, ".jobs-resume-picker__resume .jobs-resume-picker__resume-btn-container button[aria-label='Choose Resume']")
    # for (index, resume_label) in enumerate(resume_labels):
    #     if answer.endswith(resume_label.text):
    #         resume_choose_buttons[index].click()
    #         break
    # else:
    #     raise Exception("Cannot find resume in the " + answer)

def fill_form(driver: webdriver.Chrome, modal_element: WebElement, url: str, job_id: str, is_log: bool):
    unknown_questions = []
    label_elements = modal_element.find_elements(By.CSS_SELECTOR, ".fb-dash-form-element > div label, .fb-dash-form-element > fieldset legend")
    for label_element in label_elements:
        form_element = label_element.find_element(By.XPATH, "..")
        target_element = None
        if label_element.tag_name == "label":
            target_id = label_element.get_attribute("for")
            if target_id is None or target_id == "": continue
            target_elements = driver.find_elements(By.ID, target_id)
            if len(target_elements) == 0:
                continue
            target_element = target_elements[0]
        
        question = normalize_text(find_exact_question(label_element.text))
        if question == "":
            continue
        answer = get_answer(PLATFORM, question, job_id)
        if answer is None:
            if is_log is True:
                log_unknown_question(PLATFORM, question, url, job_id)
            unknown_questions.append(question)
            continue
        if type(answer) == list:
            for (index, ans) in enumerate(answer):
                if is_money_str(ans):
                    answer[index] = money_str2num(ans)

        print(question, " : ", answer)
        actual_answer = autofill(driver, form_element, target_element, answer)
        register_bid_qa(job_id, PLATFORM, question, actual_answer)

    resume_elements = modal_element.find_elements(By.XPATH, ".//h3[text()='Resume']")
    if len(resume_elements) > 0:
        fill_resume(driver, modal_element, url, job_id, is_log)

    if len(unknown_questions) > 0:
        raise Exception("Has unknown question: \n" + "\n".join(unknown_questions))

def apply(driver: webdriver.Chrome, url: str, job_id: str):
    apply_button = None
    print("Q")
    while True:
        apply_button_wrappers = driver.find_elements(By.CLASS_NAME, "jobs-apply-button--top-card")
        print("P")
        if len(apply_button_wrappers) > 0:
            try:
                apply_button = apply_button_wrappers[0].find_element(By.TAG_NAME, "button")
            except:
                time.sleep(1)
                continue
            print("T")
            break
        else:
            already_elements = driver.find_elements(By.CSS_SELECTOR, ".jobs-s-apply .artdeco-inline-feedback--success")
            print("X")
            already_elements.extend(driver.find_elements(By.CSS_SELECTOR, ".jobs-unified-top-card .jobs-details-top-card__apply-error"))
            print("Y")
            already_elements.extend(driver.find_elements(By.CSS_SELECTOR, ".post-apply-timeline .post-apply-timeline__entity"))
            print("Z")
            if len(already_elements) > 0:
                return
        time.sleep(.5)

    try:
        driver.execute_script("document.getElementById('msg-overlay').setAttribute('style', 'display: none')")
    except: pass

    while True:
        try:
            apply_button_wrappers = driver.find_elements(By.CLASS_NAME, "jobs-apply-button--top-card")
            apply_button = apply_button_wrappers[0].find_element(By.TAG_NAME, "button")
            apply_button.click()
        except:
            time.sleep(.5)
            continue
        time.sleep(.5)
        modal_elements = driver.find_elements(By.CLASS_NAME, "jobs-easy-apply-modal")
        if len(modal_elements) > 0:
            break

    global previous_page
    previous_page = ""

    while True:
        print("passed4")
        modal_element = wait_for_next_step(driver)
        print("passed5")
        print("On page:", previous_page)
        modal_element = get_modal(driver)
        print("passed6")
        is_log = True
        while True:
            try:
                if previous_page == "Resume":
                    fill_resume(driver, modal_element, url, job_id, is_log)
                else:
                    fill_form(driver, modal_element, url, job_id, is_log)
                break
            except Exception as e:
                if str(e).startswith("Has unknown question"):
                    print(e)
                    time.sleep(10)
                    is_log = False
                elif str(e).startswith("Cannot find resume"):
                    print(e)
                    break
                else:
                    # raise e
                    time.sleep(3)
                    continue
        if try_next(modal_element): break

    while True:
        done_elements = driver.find_elements(By.CSS_SELECTOR, "div[aria-labelledby='post-apply-modal'] .artdeco-modal__actionbar button")
        done_elements.extend(driver.find_elements(By.CSS_SELECTOR, "div[aria-labelledby='post-apply-modal'] .artdeco-modal__dismiss"))
        done_elements.extend(driver.find_elements(By.CSS_SELECTOR, "div[aria-labelledby='post-apply-loading-modal__title'] .artdeco-modal__actionbar button"))
        done_elements.extend(driver.find_elements(By.CSS_SELECTOR, "div[aria-labelledby='post-apply-loading-modal__title'] button[aria-label='Dismiss']"))
        if len(done_elements) > 0:
            try:
                done_elements[0].click()
                break
            except: pass
        time.sleep(.5)

def wait_for_apply(driver: webdriver.Chrome, original_url: str):
    while True:
        if glvar.terminate_url == original_url: return "rebid"
        try:
            if len(driver.window_handles) == 0:
                break
            
            parse_result = urlparse(driver.current_url)
            if parse_result.path.startswith("/jobs/view/"):
                already_elements = driver.find_elements(By.CSS_SELECTOR, ".jobs-s-apply .artdeco-inline-feedback--success")
                already_elements.extend(driver.find_elements(By.CSS_SELECTOR, ".jobs-unified-top-card .jobs-details-top-card__apply-error"))
                already_elements.extend(driver.find_elements(By.CSS_SELECTOR, ".post-apply-timeline .post-apply-timeline__entity"))
                if len(already_elements) > 0:
                    break
            else:
                break
        except selenium.common.exceptions.InvalidSessionIdException as e:
            break
        except:
            break
    time.sleep(.5)
    return ""

def send_message(driver: webdriver.Chrome, url: str, request_connect: bool):
    message_button = None
    try:
        message_button = driver.find_element(By.CLASS_NAME, "message-anywhere-button")
    except Exception as e:
        return
    
    try:
        driver.execute_script("document.getElementById('msg-overlay').setAttribute('style', 'display: none')")
    except: pass

    href = message_button.get_attribute("href")
    if "/messaging/thread/new" in href:
        message_button.click()
        driver.execute_script("document.getElementById('msg-overlay').setAttribute('style', '')")
        
        msg_overlay = driver.find_element(By.ID, "msg-overlay")
        new_message_forms = msg_overlay.find_elements(By.XPATH, "//h2[text()='New message']")
        if len(new_message_forms) == 0:
            return
        footer_element = new_message_forms[0].find_element(By.XPATH, "../../../../following-sibling::*//footer")
        send_button_elements = footer_element.find_elements(By.XPATH, "//button[text()='Send']")
        if len(send_button_elements) > 0:
            send_button_elements[0].click()
        time.sleep(2)
    else:
        if request_connect is False:
            return
        hirer_element = driver.find_element(By.CSS_SELECTOR, ".hirer-card__container .hirer-card__hirer-information .app-aware-link")
        hirer_name = hirer_element.text
        job_title_element = driver.find_element(By.CSS_SELECTOR, ".job-view-layout .jobs-unified-top-card .jobs-unified-top-card__job-title")
        job_title = job_title_element.text
        driver.get(hirer_element.get_attribute("href"))

        try:
            while True:
                overlays = driver.find_elements(By.ID, "msg-overlay")
                if len(overlays) > 0:
                    break
            driver.execute_script("document.getElementById('msg-overlay').setAttribute('style', 'display: none')")
        except: pass
        time.sleep(3)

        try:
            connect_button = driver.find_element(By.CSS_SELECTOR, ".pv-top-card .pv-top-card-v2-ctas > .pvs-profile-actions .pvs-profiltion_elemene-actions__action button li-icon[type='connect']")
            connect_button.click()
        except:
            actions_element = driver.find_element(By.CSS_SELECTOR, ".pv-top-card .pv-top-card-v2-ctas > .pvs-profile-actions")
            try:
                connect_icon = actions_element.find_element(By.CSS_SELECTOR, ".pvs-profile-actions__action button li-icon[type='connect']")
                li_button_element = connect_icon.find_element(By.XPATH, "..")
                driver.execute_script("arguments[0].click()", li_button_element)
            except:
                more_element = actions_element.find_element(By.CSS_SELECTOR, ":scope > div:last-child")
                button_element = more_element.find_element(By.TAG_NAME, "button")
                driver.execute_script("arguments[0].click()", button_element)

                try:
                    connect_icon = actions_element.find_element(By.CSS_SELECTOR, ".pvs-overflow-actions-dropdown__content li div li-icon[type='connect']")
                    li_button_element = connect_icon.find_element(By.XPATH, "..")
                    driver.execute_script("arguments[0].click()", li_button_element)
                except:
                    return

        try:
            send_invite_element = driver.find_element(By.CSS_SELECTOR, "div.send-invite")
            try:
                send_invite_element.find_element(By.CSS_SELECTOR, "button[aria-label='Other']").click()
                send_invite_element.find_element(By.CSS_SELECTOR, ".artdeco-modal__actionbar button[aria-label='Connect']").click()
            except: pass

            send_invite_element.find_element(By.CSS_SELECTOR, ".artdeco-modal__actionbar button[aria-label='Add a note']").click()
            invite_message_element = send_invite_element.find_element(By.ID, "custom-message")
            invite_message_element.send_keys(invite_message.replace("**name**", hirer_name.split(" ")[0]).replace("**job-title**", job_title))
            send_invite_element.find_element(By.CSS_SELECTOR, ".artdeco-modal__actionbar button[aria-label='Send now']").click()                
        except:
            time.sleep(1)
            return

def bid(driver: webdriver.Chrome, url: str, job_id: str, request_connect: bool):
    apply(driver, url, job_id)
    send_message(driver, url, request_connect)