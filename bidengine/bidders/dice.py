from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.shadowroot import ShadowRoot
from selenium.webdriver.common.keys import Keys
from utils.answers import get_answer, is_correct_answer
from utils.logger import log_unknown_question
import time
import selenium
from urllib.parse import urlparse
import glvar

PLATFORM = "dice"
previous_page = ""

def autofill(field: WebElement, driver: webdriver.Chrome, answer):
    if field.tag_name == "button" and field.get_attribute("aria-haspopup") == "listbox":
        popup_element = None
        for i in range(3):
            field.click()
            time.sleep(3)
            try:
                popup_element = driver.find_element(By.CLASS_NAME, "wd-popup")
                break
            except:
                time.sleep(1)
        listbox_element = popup_element.find_element(By.CSS_SELECTOR, "ul[role='listbox']")

        li_elements = listbox_element.find_elements(By.TAG_NAME, "li")
        for li_element in li_elements:
            if is_correct_answer(li_element.text, answer):
                li_element.click()
                return li_element.text
        body_element = driver.find_element(By.TAG_NAME, "body")
        body_element.send_keys(Keys.ESCAPE)
        return None
    if field.tag_name == "input" and (field.get_attribute("data-uxi-widget-type") == "selectinput" or field.get_attribute("data-uxi-widget-type") == "multiselect"):
        container = field.find_element(By.XPATH, "../..")
        container.click()
        field.send_keys(answer[0])
        time.sleep(1)
        field.send_keys(Keys.ENTER)

        while True:
            selected_elements = container.find_elements(By.CSS_SELECTOR, "div[data-automation-id='selectedItem']")
            print(selected_elements)
            if len(selected_elements) > 0:
                break
            try:
                popup_element = driver.find_element(By.CLASS_NAME, "wd-popup")
                search_label_element = popup_element.find_element(By.CSS_SELECTOR, "div[title='Search Results']")
                search_count_element = search_label_element.find_elements(By.XPATH, "following-sibling::*")[0]
                if int(search_count_element.text[1:-1]) > 1:
                    time.sleep(1)
                    search_wrapper = search_label_element.find_element(By.XPATH, "..")
                    search_list_element = search_wrapper.find_elements(By.XPATH, "following-sibling::*")[0]
                    print("A")
                    search_item_element = search_list_element.find_element(By.CSS_SELECTOR, "div[aria-posinset='1']")
                    print("B")
                    clickable_element = search_item_element.find_elements(By.XPATH, "*")[0]
                    print("C")
                    driver.execute_script("arguments[0].click()",clickable_element)
                    break
            except:
                pass
            time.sleep(1)
            
        # ul_element = container.find_element(By.CSS_SELECTOR, "ul[role='listbox']")
        # while len(ul_element.find_elements(By.XPATH, "./*"))
        #     time.sleep(1)
        time.sleep(1)
        field.send_keys(Keys.TAB)
        return answer[0]


    if (field.tag_name == "" or field.tag_name == "input") and (field.get_attribute("type") == "text" or field.get_attribute("type") == "email"):
        field.send_keys(answer[0])
        return answer[0]
    if field.tag_name == "textarea":
        field.send_keys(answer[0])
        return answer[0]
    if field.tag_name == "input" and field.get_attribute("type") == "checkbox":
        if (type(answer) == bool and answer is True) or answer is True:
            field.click()
            return True
        return False
    if field.tag_name == "div":
        if field.get_attribute("data-automation-id") == "dateInputWrapper":
            element = field.find_element(By.CSS_SELECTOR, "div[data-automation-id='dateSectionMonth-display']")
            element.click()
            time.sleep(.5)
            element.find_elements(By.XPATH, "following-sibling::*")[0].send_keys(answer.split("/")[0])
            time.sleep(.5)
            element = field.find_element(By.CSS_SELECTOR, "div[data-automation-id='dateSectionDay-display']")
            element.click()
            time.sleep(.5)
            element.find_elements(By.XPATH, "following-sibling::*")[0].send_keys(answer.split("/")[1])
            time.sleep(.5)
            element = field.find_element(By.CSS_SELECTOR, "div[data-automation-id='dateSectionYear-display']")
            element.click()
            time.sleep(.5)
            element.find_elements(By.XPATH, "following-sibling::*")[0].send_keys(answer.split("/")[2])
            time.sleep(.5)
        else:
            label_elements = field.find_elements(By.TAG_NAME, "label")
            for label_element in label_elements:
                target_id = label_element.get_attribute("for")
                if target_id is None or target_id == "":
                    continue
                print("LABEL-div", label_element.text)
                if is_correct_answer(label_element.text, answer):
                    try:
                        target = field.find_element(By.ID, target_id)
                        driver.execute_script("arguments[0].click()", target)
                        time.sleep(1)
                    except:
                        label_element.click()
                        time.sleep(1)
                    return label_element.text
            body_element = driver.find_element(By.TAG_NAME, "body")
            body_element.send_keys(Keys.ESCAPE)
            return None
    return None


def pre_step1(driver: webdriver.Chrome, url: str):
    apply_button = None
    while True:
        apply_wrappers = driver.find_elements(By.TAG_NAME, "apply-button-wc")
        if len(apply_wrappers) == 0:
            continue
        shadow_root: ShadowRoot = driver.execute_script("return arguments[0].shadowRoot", apply_wrappers[0])
        submitted_elements = shadow_root.find_elements(By.CLASS_NAME, "application-submitted")
        if len(submitted_elements) > 0:
            return False
        
        apply_buttons = shadow_root.find_elements(By.CLASS_NAME, "btn")
        if len(apply_buttons) > 0:
            apply_button = apply_buttons[0]
            break
        
        time.sleep(1)

    apply_button.click()
    return True

def pre_step2(driver: webdriver.Chrome, url: str):
    apply_button = None
    while True:
        header_wrapper = driver.find_elements(By.ID, "header-wrap")
        if len(header_wrapper) == 0:
            continue

        apply_sec = header_wrapper[0].find_elements(By.CLASS_NAME, "applySec")
        if len(apply_sec) == 0:
            continue
        sec_element_wrapper = apply_sec[0].find_elements(By.XPATH, "*")[0]
        sec_element = sec_element_wrapper.find_element(By.TAG_NAME, "dhi-wc-apply-button")

        shadow_root: ShadowRoot = driver.execute_script("return arguments[0].shadowRoot", sec_element)
        # submitted_elements = shadow_root.find_elements(By.CLASS_NAME, "application-submitted")
        # if len(submitted_elements) > 0:
        #     return False
        
        try:
            apply_button_wrapper = shadow_root.find_element(By.ID, "ja-apply-button")
            apply_button = apply_button_wrapper.find_element(By.TAG_NAME, "a")
            break
        except: pass
        
        time.sleep(1)

    apply_button.click()
    return True

def wait_for_next_step(driver: webdriver.Chrome):
    global previous_page
    page_contents = []
    while True:
        parse_result = urlparse(driver.current_url)
        if parse_result.path.startswith("/application-submitted"):
            return None
        page_contents = driver.find_elements(By.TAG_NAME, "main")
        if len(page_contents) > 0:
            try:
                heading_element = page_contents[0].find_element(By.CLASS_NAME, "heading-wrapper")
                if heading_element.text != previous_page:
                    previous_page = heading_element.text
                    break
            except: pass
        time.sleep(1)
    time.sleep(1)
    return page_contents[0]

def step_main(driver: webdriver.Chrome, page_content: WebElement, url: str):
    navigation_button_panel = page_content.find_element(By.CLASS_NAME, "navigation-buttons")
    
    next_button_element = None
    print(navigation_button_panel)
    try:
        next_button_element = navigation_button_panel.find_element(By.CLASS_NAME, "btn-next")
    except: pass

    print(next_button_element.tag_name)
    next_button_element.click()

def bid(driver: webdriver.Chrome, url: str, job_id: str):
    parsed_url = urlparse(driver.current_url)
    if parsed_url.path.startswith("/job-detail"):
        if not pre_step1(driver, url):
            return
        print("Passed pre_step1")
    if parsed_url.path.startswith("/jobs/detail"):
        if not pre_step2(driver, url):
            return
        print("Passed pre_step2")

    global previous_page
    previous_page = ""

    while True:
        time.sleep(1)
        content_page = wait_for_next_step(driver)
        if content_page is None:
            break
        else:
            print("Passed", previous_page)
        try:
            step_main(driver, content_page, url)
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