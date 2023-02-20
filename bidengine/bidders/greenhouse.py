import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from utils.answers import get_answer, normalize_text, is_correct_answer
from utils.logger import log_unknown_question
import time
from urllib.parse import urlparse
import glvar
from utils.db import register_bid_qa

PLATFORM = "greenhouse"

def autofill(driver: webdriver.Chrome, field: WebElement, label: WebElement, answer):
    if answer == "":
        return
    select2s = field.find_elements(By.CLASS_NAME, "select2-container")
    if len(select2s) > 0:
        select2 = select2s[0]
        select2_id = select2.get_attribute("id")
        select_id = select2_id.replace("s2id_", "")
        select_element = driver.find_element(By.ID, select_id)
        if select_element.tag_name == "select":
            options = select_element.find_elements(By.TAG_NAME, "option")
            option_texts = [ option.get_attribute("innerText") for option in options ]
            for ans in answer:
                for (index, option_text) in enumerate(option_texts):
                    if is_correct_answer(option_text, [ans]):
                        select2_value = options[index].get_attribute("value")
                        print(ans, select2_value)
                        driver.execute_script(f'$("#{select2_id}").select2("val", "{select2_value}")')
                        return option_text
        elif select_element.tag_name == "input":
            driver.execute_script(f'$("#{select2_id}").select2("open")')
            active_element = driver.execute_script("return document.activeElement")
            active_element.send_keys(answer[0])
            while len(driver.find_elements(By.CLASS_NAME, "select2-searching")) > 0:
                time.sleep(1)
            active_element.send_keys(Keys.ENTER)
            return answer[0]
        return None

    select_elements = field.find_elements(By.TAG_NAME, 'select')
    if len(select_elements) > 0:
        option_elements = select_elements[0].find_elements(By.TAG_NAME, "option")
        option_values = [ element.text for element in option_elements ]
        for ans in answer:
            for (option_index, option_value) in enumerate(option_values):
                if is_correct_answer(option_value, [ans]):
                    option_elements[option_index].click()
                    return option_value
        return None
    
    upload_elements = field.find_elements(By.CLASS_NAME, "attach-or-paste")
    if len(upload_elements) > 0:
        data_field = upload_elements[0].get_attribute("data-field")
        s3_upload_forms = driver.find_elements(By.CLASS_NAME, "s3-upload-form")
        for s3_upload_form in s3_upload_forms:
            if s3_upload_form.get_attribute('data-presigned-form') == data_field:
                file_element = s3_upload_form.find_element(By.NAME, "file")
                file_element.send_keys(answer[0])
                return answer[0]
        return None

    auto_completes = field.find_elements(By.TAG_NAME, 'auto-complete')
    if len(auto_completes) > 0:
        auto_complete = auto_completes[0]
        input = auto_complete.find_element(By.TAG_NAME, 'input')
        input.send_keys(answer[0])

        ul = auto_complete.find_element(By.TAG_NAME, "ul")
        while ul.get_attribute('hidden') == "true":
            time.sleep(1)

        input.send_keys(Keys.ARROW_DOWN)
        input.send_keys(Keys.ENTER)
        return answer[0]

    input_elements = field.find_elements(By.TAG_NAME, 'input')
    if len(input_elements) > 0:
        checkbox_elements = field.find_elements(By.CSS_SELECTOR, 'input[type="checkbox"]')
        if len(checkbox_elements) > 0:
            checkbox_values = [ element.find_element(By.XPATH, "..").text for element in checkbox_elements ]
            checked = [False] * len(checkbox_values)
            selected_values = []
            for ans in answer:
                for (index, checkbox_value) in enumerate(checkbox_values):
                    if checked[index]:
                        continue
                    if is_correct_answer(checkbox_value, [ans]):
                        checkbox_elements[index].click()
                        checked[index] = True
                        selected_values.append(checkbox_value)
            return selected_values
        else:
            for input in input_elements:
                if input.get_attribute("type") == "text":
                    input.send_keys(answer[0])
                    return answer[0]
        return None

    textarea_elements = field.find_elements(By.TAG_NAME, 'textarea')
    if len(textarea_elements) > 0:
        textarea_elements[0].send_keys(answer[0])
        return answer[0]
    return None


def bid(driver: webdriver.Chrome, url: str, job_id: str):
    form_element = driver.find_element(By.TAG_NAME, "form")
    field_elements = form_element.find_elements(By.CLASS_NAME, "field")
    unknown_questions = []

    for element in field_elements:
        label = element
        lines = label.get_attribute("innerText").splitlines()
        if len(lines) == 0:
            continue

        question = lines[0].replace("*", "").strip()
        if question == "":
            continue
        answer = get_answer(PLATFORM, question, job_id)
        if answer is None:
            log_unknown_question(PLATFORM, question, url, job_id)
            unknown_questions.append(question)
            continue

        print(question, " : ", answer)
        actual_answer = autofill(driver, element, label, answer)
        register_bid_qa(job_id, PLATFORM, question, actual_answer)

    if len(unknown_questions) > 0:
        raise Exception("Has unknown question: \n" + "\n".join(unknown_questions))
    
    submit_button = driver.find_element(By.ID, "submit_app")
    while submit_button.get_attribute("value") != "Submit Application":
        time.sleep(1)
    time.sleep(1)
    submit_button.click()

def wait_for_apply(driver: webdriver.Chrome, original_url: str):
    while True:
        if glvar.terminate_url == original_url: return "rebid"
        try:
            if len(driver.window_handles) == 0:
                break
            
            parse_result = urlparse(driver.current_url)
            if parse_result.path.endswith("confirmation"):
                break
        except selenium.common.exceptions.InvalidSessionIdException as e:
            break
    time.sleep(1)
    return ""

def get_inner_greenhouse(driver: WebElement):
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    if len(iframes) > 0:
        urls = [ iframe.get_attribute("src") for iframe in iframes ]
        for url in urls:
            parse_result = urlparse(url)
            if parse_result.netloc.endswith("greenhouse.io"):
                return url
            return None
    return None