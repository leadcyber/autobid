from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from utils.answers import get_answer, is_correct_answer, normalize_text, find_exact_question
from utils.logger import log_unknown_question
import time
import selenium
from urllib.parse import urlparse
import glvar
from utils.db import register_bid_qa

PLATFORM = "bamboohr"

def autofill(driver: WebElement, field: WebElement, answer):
    if field.tag_name == "input" or field.tag_name == "textarea":
        field.send_keys(answer[0])
        return answer[0]
    if field.tag_name == "select":
        preceding_sibling = field.find_elements(By.XPATH, "preceding-sibling::*")[-1]
        button_div = preceding_sibling.find_elements(By.XPATH, "./*")[0]
        button_div.click()
        data_menu_id = button_div.get_attribute("data-menu-id")
        time.sleep(1)
        data_menu_elements = driver.find_elements(By.CSS_SELECTOR, f"[data-menu-id='{data_menu_id}']")
        try:
            search_element = data_menu_elements[-1].find_element(By.CSS_SELECTOR, "input[aria-label='Search']")
            search_element.send_keys(answer[0])
            search_element.send_keys(Keys.ENTER)
            return answer[0]
        except:
            time.sleep(.5)
            option_elements = driver.find_elements(By.CSS_SELECTOR, f"div[data-helium-id={data_menu_id}] .fab-MenuOption")
            option_values = [ element.text for element in option_elements ]
            selected_option_values = []
            for ans in answer:
                for (index, option_value) in enumerate(option_values):
                    if is_correct_answer(option_value, [ans]):
                        option_elements[index].click()
                        selected_option_values.append(option_value)
            return selected_option_values
    return None

def autofill_legend(container: WebElement, field: str, answer):
    label_elements = container.find_elements(By.TAG_NAME, "label")
    if len(label_elements) == 0:
        return ""
    for ans in answer:
        for label_element in label_elements:
            if is_correct_answer(label_element.text, [ans]):
                label_element.click()
                return label_element.text
    return None


def goto_bid_slide(driver: webdriver.Chrome):
    retry = 5
    while retry >= 0:
        try:
            apply_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Apply for This Job')]")
            apply_buttons.extend(driver.find_elements(By.XPATH, "//button/span[contains(text(), 'Apply for This Job')]/.."))
            for apply_button in apply_buttons:
                try:
                    apply_button.click()
                    return
                except: pass
        except: pass
        retry = retry - 1
        time.sleep(1)

def bid(driver: webdriver.Chrome, url: str, job_id: str):
    goto_bid_slide(driver)

    form_element = driver.find_element(By.TAG_NAME, "form")
    label_elements = form_element.find_elements(By.CSS_SELECTOR, "label.fab-Label")
    unknown_questions = []

    submit_panel = driver.find_element(By.XPATH, "//span[contains(text(), 'Submit Application')]")
    submit_button = None
    while submit_panel.value_of_css_property("position") != "fixed":
        if submit_panel.tag_name == "button" and submit_button is None:
            submit_button = submit_panel
        submit_panel = submit_panel.find_element(By.XPATH, "..")
    driver.execute_script("arguments[0].setAttribute('style','display: none')",submit_panel)

    for label_element in label_elements:
        line_question = find_exact_question(label_element.text)
        if line_question is None:
            continue
        question = normalize_text(line_question)
        field_id = label_element.get_attribute("for")
        container = label_element.find_element(By.XPATH, "..")

        answer = get_answer(PLATFORM, question, job_id)
        if answer is None:
            log_unknown_question(PLATFORM, question, url, job_id)
            unknown_questions.append(question)
            continue
        
        print(question, " : ", answer)
        actual_answer = None
        if question == "resume":
            actual_answer = autofill(driver, container.find_element(By.CSS_SELECTOR, "[aria-label='file-input']"), answer)
        elif question == "cover letter":
            actual_answer = autofill(driver, container.find_element(By.CSS_SELECTOR, "[aria-label='file-input']"), answer)
        elif question == "date available":
            actual_answer = autofill(driver, container.find_element(By.CSS_SELECTOR, "[calendar-picker='date']"), answer)
        else:
            actual_answer = autofill(driver, container.find_element(By.NAME, field_id), answer)

        if actual_answer is None:
            log_unknown_question(PLATFORM, question, url, job_id)
            unknown_questions.append(question)
            continue
        register_bid_qa(job_id, PLATFORM, question, actual_answer)

    legend_elements = form_element.find_elements(By.TAG_NAME, "legend")
    for legend_element in legend_elements:
        line_question = find_exact_question(legend_element.text)
        if line_question is None:
            continue
        question = normalize_text(line_question)
        field_element = legend_element.find_elements(By.XPATH, "following-sibling::*")[0]
        container = legend_element.find_element(By.XPATH, "..")

        answer = get_answer(PLATFORM, question, job_id)
        if answer is None:
            log_unknown_question(PLATFORM, question, url, job_id)
            unknown_questions.append(question)
            continue
        
        print(question, " : ", answer)
        actual_answer = autofill_legend(container, field_element, answer)
        if actual_answer is None:
            log_unknown_question(PLATFORM, question, url, job_id)
            unknown_questions.append(question)
            continue
        register_bid_qa(job_id, PLATFORM, question, actual_answer)

    driver.execute_script("arguments[0].setAttribute('style','display: block')",submit_panel)
    
    if len(unknown_questions) > 0:
        raise Exception("Has unknown question: \n" + "\n".join(unknown_questions))
    time.sleep(2)
    submit_button.click()

def wait_for_apply(driver: webdriver.Chrome, original_url: str):
    while True:
        if glvar.terminate_url == original_url: return "rebid"
        try:
            if len(driver.window_handles) == 0:
                break
            
            parse_result = urlparse(driver.current_url)
            if parse_result.path.endswith("thanks"):
                break
            success_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Your application was submitted successfully')]")
            if len(success_elements) > 0 and success_elements[0].is_displayed():
                break
        except selenium.common.exceptions.InvalidSessionIdException as e:
            break
        except:
            break
    time.sleep(1)
    return ""