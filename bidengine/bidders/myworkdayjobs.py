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
from utils.db import register_bid_qa

PLATFORM = "myworkdayjobs"
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
        li_texts = [li_element.text for li_element in li_elements]
        for ans in answer:
            for (index, li_text) in enumerate(li_texts):
                if is_correct_answer(li_text, [ans]):
                    li_elements[index].click()
                    return li_text
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
        field.clear()
        field.send_keys(answer[0])
        return answer[0]
    if field.tag_name == "textarea":
        field.clear()
        field.send_keys(answer[0])
        return answer[0]
    if field.tag_name == "input" and field.get_attribute("type") == "checkbox":
        if True in answer:
            field.click()
            return True
        return False
    if field.tag_name == "div":
        if field.get_attribute("data-automation-id") == "dateInputWrapper":
            answer = answer[0]
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
            element.click()
        else:
            label_elements = field.find_elements(By.TAG_NAME, "label")
            label_items = []
            for label_element in label_elements:
                target_id = label_element.get_attribute("for")
                if target_id is None or target_id == "":
                    continue
                print("LABEL-div", label_element.text)
                label_items.append((label_element.text, target_id, label_element))
            for ans in answer:
                for label_item in label_items:
                    if is_correct_answer(label_item[0], [ans]):
                        try:
                            target = field.find_element(By.ID, label_item[1])
                            driver.execute_script("arguments[0].click()", target)
                            time.sleep(1)
                        except:
                            label_item[2].click()
                            time.sleep(1)
                        return label_item[0]
            body_element = driver.find_element(By.TAG_NAME, "body")
            body_element.send_keys(Keys.ESCAPE)
            return None
    return None
    


def step_signin(driver: webdriver.Chrome, url: str, job_id: str):
    unknown_questions = []
    while True:
        signin_buttons = driver.find_elements(By.CSS_SELECTOR, "div[aria-label='Sign In']")
        if len(signin_buttons) > 0:
            break
        time.sleep(1)
    answer = get_answer(PLATFORM, "Email Address")
    if answer is None:
        log_unknown_question(PLATFORM, "Email Address", url, job_id)
        unknown_questions.append("Email Address")
    email_element = driver.find_element(By.CSS_SELECTOR, "input[data-automation-id='email']")
    email_element.send_keys(answer)

    answer = get_answer(PLATFORM, "Password")
    if answer is None:
        log_unknown_question(PLATFORM, "Password", url, job_id)
        unknown_questions.append("Password")
    password_element = driver.find_element(By.CSS_SELECTOR, "input[data-automation-id='password']")
    password_element.send_keys(answer)

    time.sleep(2)

    retry = 5
    while retry > 0:
        signin_buttons = driver.find_elements(By.CSS_SELECTOR, "div[aria-label='Sign In']")
        if len(signin_buttons) > 0:
            try:
                print("sign in clicked")
                signin_buttons[0].click()
            except:
                return True
            retry = retry - 1
            time.sleep(10)
            continue
        return True
    return False

def step1(driver: webdriver.Chrome, url: str):
    while True:
        apply_buttons = driver.find_elements(By.XPATH, "//a[text()='Apply']")
        if len(apply_buttons) > 0:
            break
        time.sleep(1)

    retry = 5
    while retry > 0:
        apply_buttons = driver.find_elements(By.XPATH, "//a[text()='Apply']")
        if len(apply_buttons) > 0:
            try:
                apply_buttons[0].click()
            except:
                return True
            retry = retry - 1
            time.sleep(10)
            continue
        return True
    return False

def step2(driver: webdriver.Chrome, url: str):
    while True:
        apply_buttons = driver.find_elements(By.XPATH, "//a[text()='Apply Manually']")
        if len(apply_buttons) > 0:
            break
        time.sleep(1)
    retry = 5
    while retry > 0:
        apply_buttons = driver.find_elements(By.XPATH, "//a[text()='Apply Manually']")
        if len(apply_buttons) > 0:
            try:
                apply_buttons[0].click()
            except:
                return True
            retry = retry - 1
            time.sleep(10)
            continue
        return True
    return False

def step3(driver: webdriver.Chrome, url: str):
    while True:
        create_buttons = driver.find_elements(By.XPATH, "//button[text()='Create Account']")
        if len(create_buttons) > 0:
            break
        time.sleep(1)
    retry = 5
    while retry > 0:
        create_buttons = driver.find_elements(By.XPATH, "//button[text()='Create Account']")
        if len(create_buttons) > 0:
            try:
                create_buttons[0].click()
            except:
                return True
            retry = retry - 1
            time.sleep(10)
            continue
        return True
    return False

def step4(driver: webdriver.Chrome, url: str, job_id: str):
    unknown_questions = []
    while True:
        create_buttons = driver.find_elements(By.CSS_SELECTOR, "div[aria-label='Create Account']")
        if len(create_buttons) > 0:
            break
        time.sleep(1)
        
    answer = get_answer(PLATFORM, "Email Address")
    if answer is None:
        log_unknown_question(PLATFORM, "Email Address", url, job_id)
        unknown_questions.append("Email Address")
    email_element = driver.find_element(By.CSS_SELECTOR, "input[data-automation-id='email']")
    email_element.send_keys(answer)

    answer = get_answer(PLATFORM, "Password")
    if answer is None:
        log_unknown_question(PLATFORM, "Password", url, job_id)
        unknown_questions.append("Password")
    password_element = driver.find_element(By.CSS_SELECTOR, "input[data-automation-id='password']")
    password_element.send_keys(answer)
    verify_password_element = driver.find_element(By.CSS_SELECTOR, "input[data-automation-id='verifyPassword']")
    verify_password_element.send_keys(answer)

    try:
        agree_element = driver.find_element(By.CSS_SELECTOR, "input[data-automation-id='createAccountCheckbox']")
        agree_element.click()
        time.sleep(1)
    except: pass

    retry = 5
    while retry > 0:
        create_buttons = driver.find_elements(By.CSS_SELECTOR, "div[aria-label='Create Account']")
        if len(create_buttons) > 0:
            try:
                create_buttons[0].click()
                time.sleep(2)
                error_messages = driver.find_elements(By.CSS_SELECTOR, "div[data-automation-id='errorMessage']")
                if len(error_messages) > 0:
                    signin_link = driver.find_element(By.CSS_SELECTOR, "button[data-automation-id='signInLink']")
                    signin_link.click()
                    return step_signin(driver, url, job_id)
            except:
                return True
            retry = retry - 1
            time.sleep(10)
            continue
        break

    return True

def wait_for_next_step(driver: webdriver.Chrome):
    global previous_page
    page_contents = []
    while True:
        page_contents = driver.find_elements(By.CSS_SELECTOR, "div[id='mainContent']")
        if len(page_contents) > 0:
            veil_elements = driver.find_elements(By.CSS_SELECTOR, "div[data-automation-id='veil']")
            if len(veil_elements) == 0:
                try:
                    h2_element = page_contents[0].find_element(By.TAG_NAME, "h2")
                    if h2_element.text != previous_page:
                        previous_page = h2_element.text
                        break
                except: pass
        time.sleep(1)
    time.sleep(1)
    return page_contents[0]

def step_submit(driver: webdriver.Chrome, page_content: WebElement, url: str):
    submit_button = driver.find_element(By.CSS_SELECTOR, "button[data-automation-id='bottom-navigation-next-button']")
    submit_button.click()

def step_main(driver: webdriver.Chrome, page_content: WebElement, url: str, job_id: str):

    driver.execute_script('document.querySelector("div[data-automation-id=\'footerContainer\'] + div").setAttribute("style", "display: none")')
    driver.execute_script('document.querySelector("header").setAttribute("style", "display: none")')
    
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
            if (target_element.tag_name == "input" and target_element.get_attribute("type") == "radio") or \
                target_element.tag_name == "span" or \
                (target_element.tag_name == "input" and target_element.get_attribute("type") == "checkbox" and not target_id.startswith("input-")):
                continue
        
        question = label_element.text.replace("*", "").strip()
        if question == "": continue
        answer = get_answer(PLATFORM, question, job_id)
        if answer is None:
            log_unknown_question(PLATFORM, question, url, job_id)
            unknown_questions.append(question)
            continue

        print(question, " : ", answer)

        if (target_element.tag_name == "input" and target_element.get_attribute("value") == answer) or \
            (target_element.tag_name == "textarea" and target_element.text == answer):
            if len(answer) > 0:
                # Already filled the form
                driver.execute_script('document.querySelector("div[data-automation-id=\'footerContainer\'] + div").setAttribute("style", "display: block")')
                driver.execute_script('document.querySelector("header").setAttribute("style", "display: block")')
                next_button = driver.find_element(By.CSS_SELECTOR, "button[data-automation-id='bottom-navigation-next-button']")
                next_button.click()
                return
        actual_answer = autofill(target_element, driver, answer)
        register_bid_qa(job_id, PLATFORM, question, actual_answer)

        current_label_elements = page_content.find_elements(By.TAG_NAME, "label")
        for elm in label_elements:
            if elm in current_label_elements:
                current_label_elements.remove(elm)
        label_elements.extend(current_label_elements)

    try:
        today_wrapper = page_content.find_element(By.CSS_SELECTOR, "div[data-automation-id='formField-todaysDate']")
        date_element = today_wrapper.find_element(By.CSS_SELECTOR, "div[data-automation-id='dateInputWrapper']")
        answer = get_answer(PLATFORM, "today")
        actual_answer = autofill(date_element, driver, answer)
        register_bid_qa(job_id, PLATFORM, "today", actual_answer)
    except:
        pass
    
    legend_elements = page_content.find_elements(By.TAG_NAME, "legend")
    for legend_element in legend_elements:
        target_id = legend_element.get_attribute("for")
        if target_id is None or target_id == "":
            continue
        target_element = page_content.find_element(By.ID, target_id)

        question = legend_element.text.replace("*", "").strip()
        if question == "": continue
        answer = get_answer(PLATFORM, question, job_id)
        if answer is None:
            log_unknown_question(PLATFORM, question, url, job_id)
            unknown_questions.append(question)
            continue

        print(question, " : ", answer)

        actual_answer = autofill(target_element, driver, answer)
        register_bid_qa(job_id, PLATFORM, question, actual_answer)

    driver.execute_script('document.querySelector("div[data-automation-id=\'footerContainer\'] + div").setAttribute("style", "display: block")')
    driver.execute_script('document.querySelector("header").setAttribute("style", "display: block")')

    if len(unknown_questions) > 0:
        raise Exception("Has unknown question: \n" + "\n".join(unknown_questions))
    
    next_button = driver.find_element(By.CSS_SELECTOR, "button[data-automation-id='bottom-navigation-next-button']")
    next_button.click()

def step_experience(driver: webdriver.Chrome, page_content: WebElement, url: str, job_id):
    unknown_questions = []

    # Check if this field is already filled out
    try:
        work_container = page_content.find_element(By.CSS_SELECTOR, f"div[data-automation-id='workExperience-1']")
        field = work_container.find_element(By.CSS_SELECTOR, "[data-automation-id='jobTitle']")
        if len(field.get_attribute("value")) > 0:
            next_button = driver.find_element(By.CSS_SELECTOR, "button[data-automation-id='bottom-navigation-next-button']")
            next_button.click()
            return
    except:
        pass

    driver.execute_script('document.querySelector("header").setAttribute("style", "display: none")')
    driver.execute_script('document.querySelector("div[data-automation-id=\'footerContainer\'] + div").setAttribute("style", "display: none")')

    try:
        button_add_experience = page_content.find_element(By.CSS_SELECTOR, "button[aria-label='Add Work Experience']")
        button_add_experience.click()
        time.sleep(2)
    except:
        pass

    has_experience = True
    has_education = True
    try:
        button_add_experience = page_content.find_element(By.CSS_SELECTOR, "button[aria-label='Add Another Work Experience']")
        button_add_experience.click()
        time.sleep(2)
        button_add_experience = page_content.find_element(By.CSS_SELECTOR, "button[aria-label='Add Another Work Experience']")
        button_add_experience.click()
        time.sleep(2)
        button_add_experience = page_content.find_element(By.CSS_SELECTOR, "button[aria-label='Add Another Work Experience']")
        button_add_experience.click()
        time.sleep(2)
    except:
        has_experience = False

    try:
        button_add_experience = page_content.find_element(By.CSS_SELECTOR, "button[aria-label='Add Education']")
        button_add_experience.click()
        time.sleep(2)
    except:
        try:
            page_content.find_element(By.CSS_SELECTOR, "div[data-automation-id='educationSection']")
        except:
            has_education = False

    if has_experience:
        for i in range(1, 5):
            work_container = page_content.find_element(By.CSS_SELECTOR, f"div[data-automation-id='workExperience-{i}']")

            field = work_container.find_element(By.CSS_SELECTOR, "[data-automation-id='jobTitle']")
            question = f"job-title-{i}"
            answer = get_answer(PLATFORM, question, job_id)
            if answer is None:
                log_unknown_question(PLATFORM, question, url, job_id)
                unknown_questions.append(question)
                continue

            actual_answer = autofill(field, driver, answer)
            register_bid_qa(job_id, PLATFORM, question, actual_answer)

            field = work_container.find_element(By.CSS_SELECTOR, "[data-automation-id='company']")
            question = f"company-{i}"
            answer = get_answer(PLATFORM, question)
            if answer is None:
                log_unknown_question(PLATFORM, question, url, job_id)
                unknown_questions.append(question)
                continue
            actual_answer = autofill(field, driver, answer)
            register_bid_qa(job_id, PLATFORM, question, actual_answer)

            try:
                field = work_container.find_element(By.CSS_SELECTOR, "[data-automation-id='location']")
                question = f"location-{i}"
                answer = get_answer(PLATFORM, question)
                if answer is None:
                    log_unknown_question(PLATFORM, question, url, job_id)
                    unknown_questions.append(question)
                    continue
                actual_answer = autofill(field, driver, answer)
                register_bid_qa(job_id, PLATFORM, question, actual_answer)
            except: pass

            question = f"job-date-from-{i}"
            answer = get_answer(PLATFORM, question)
            if answer is None:
                log_unknown_question(PLATFORM, question, url, job_id)
                unknown_questions.append(question)
                continue
            answer = answer[0]
            register_bid_qa(job_id, PLATFORM, question, answer)
            date_container = work_container.find_element(By.CSS_SELECTOR, "[data-automation-id='formField-startDate']")
            field = date_container.find_element(By.CSS_SELECTOR, "[data-automation-id='dateSectionMonth-display']")
            field.click()
            time.sleep(.5)
            field.find_elements(By.XPATH, "following-sibling::*")[0].send_keys(answer.split("/")[0])
            time.sleep(.5)
            field = date_container.find_element(By.CSS_SELECTOR, "[data-automation-id='dateSectionYear-display']")
            field.click()
            time.sleep(.5)
            field.find_elements(By.XPATH, "following-sibling::*")[0].send_keys(answer.split("/")[1])
            time.sleep(.5)

            question = f"job-date-to-{i}"
            answer = get_answer(PLATFORM, question)
            if answer is None:
                log_unknown_question(PLATFORM, question, url, job_id)
                unknown_questions.append(question)
                continue
            answer = answer[0]
            register_bid_qa(job_id, PLATFORM, question, answer)
            date_container = work_container.find_element(By.CSS_SELECTOR, "[data-automation-id='formField-endDate']")
            field = date_container.find_element(By.CSS_SELECTOR, "[data-automation-id='dateSectionMonth-display']")
            field.click()
            time.sleep(.5)
            field.find_elements(By.XPATH, "following-sibling::*")[0].send_keys(answer.split("/")[0])
            time.sleep(.5)
            field = date_container.find_element(By.CSS_SELECTOR, "[data-automation-id='dateSectionYear-display']")
            field.click()
            time.sleep(.5)
            field.find_elements(By.XPATH, "following-sibling::*")[0].send_keys(answer.split("/")[1])
            time.sleep(.5)
            field.click()

            field = work_container.find_element(By.CSS_SELECTOR, "[data-automation-id='description']")
            question = f"role-description-{i}"
            answer = get_answer(PLATFORM, question, job_id)
            if answer is None:
                log_unknown_question(PLATFORM, question, url, job_id)
                unknown_questions.append(question)
                continue
            actual_answer = autofill(field, driver, answer)
            register_bid_qa(job_id, PLATFORM, question, actual_answer)
        time.sleep(1)

    if has_education:
        question = "school"
        answer = get_answer(PLATFORM, question)
        education_container = page_content.find_element(By.CSS_SELECTOR, "div[data-automation-id='education-1']")
        if answer is None:
            log_unknown_question(PLATFORM, question, url, job_id)
            unknown_questions.append(question)
        else:
            school_elements = education_container.find_elements(By.CSS_SELECTOR, "input[data-automation-id='school']")
            school_elements.extend(education_container.find_elements(By.CSS_SELECTOR, "input[data-automation-id='formField-schoolItem']"))
            actual_answer = autofill(school_elements[0], driver, answer)
            register_bid_qa(job_id, PLATFORM, question, actual_answer)

        question = "degree"
        answer = get_answer(PLATFORM, question)
        if answer is None:
            log_unknown_question(PLATFORM, question, url, job_id)
            unknown_questions.append(question)
        else:
            degree_elements = education_container.find_elements(By.CSS_SELECTOR, "button[data-automation-id='degree']")
            degree_elements.extend(education_container.find_elements(By.CSS_SELECTOR, "button[data-automation-id='formField-degree']"))
            actual_answer = autofill(degree_elements[0], driver, answer)
            register_bid_qa(job_id, PLATFORM, question, actual_answer)

        question = "field-of-study"
        answer = get_answer(PLATFORM, question)
        if answer is None:
            log_unknown_question(PLATFORM, question, url, job_id)
            unknown_questions.append(question)
        else:
            field_of_study_wapper = education_container.find_element(By.CSS_SELECTOR, "div[data-automation-id='formField-field-of-study']")
            field_of_study_element = field_of_study_wapper.find_element(By.CSS_SELECTOR, "input[placeholder='Search']")
            actual_answer = autofill(field_of_study_element, driver, answer)
            register_bid_qa(job_id, PLATFORM, question, actual_answer)

        try:
            date_container = education_container.find_element(By.CSS_SELECTOR, "[data-automation-id='formField-startDate']")
            question = "education-from"
            answer = get_answer(PLATFORM, question)
            if answer is None:
                log_unknown_question(PLATFORM, question, url, job_id)
                unknown_questions.append(question)
            else:
                field = date_container.find_element(By.CSS_SELECTOR, "[data-automation-id='dateSectionYear-display']")
                field.click()
                time.sleep(.5)
                field.find_elements(By.XPATH, "following-sibling::*")[0].send_keys(answer[0])
                time.sleep(.5)
                register_bid_qa(job_id, PLATFORM, question, answer[0])
        except:
            pass

        try:
            date_container = education_container.find_element(By.CSS_SELECTOR, "[data-automation-id='formField-endDate']")
            question = "education-to"
            answer = get_answer(PLATFORM, question)
            if answer is None:
                log_unknown_question(PLATFORM, question, url, job_id)
                unknown_questions.append(question)
            else:
                field = date_container.find_element(By.CSS_SELECTOR, "[data-automation-id='dateSectionYear-display']")
                field.click()
                time.sleep(.5)
                field.find_elements(By.XPATH, "following-sibling::*")[0].send_keys(answer[0])
                time.sleep(.5)
                field.click()
                register_bid_qa(job_id, PLATFORM, question, answer[0])
        except:
            pass

    try:
        skill_container = education_container.find_element(By.CSS_SELECTOR, "[data-automation-id='formField-skillsPrompt']")
        question = "skills"
        answer = get_answer(PLATFORM, question)
        if answer is None or type(answer) is not list:
            log_unknown_question(PLATFORM, question, url, job_id)
            unknown_questions.append(question)
        else:
            skill_container.click()
            input_element = skill_container.find_element(By.CSS_SELECTOR, "input[data-automation-id='searchBox']")
            input_element.send_keys(answer[0])
            input_element.send_keys(Keys.ENTER)
            time.sleep(1)
            register_bid_qa(job_id, PLATFORM, question, answer[0])
    except:
        pass

    try:
        resume_container = page_content.find_element(By.CSS_SELECTOR, "div[data-automation-id='resumeSection']")
        question = "Resume/CV"
        answer = get_answer(PLATFORM, question, job_id)
        if answer is None:
            log_unknown_question(PLATFORM, question, url, job_id)
            unknown_questions.append(question)
        else:
            file_element = resume_container.find_element(By.CSS_SELECTOR, "input[type='file']")
            file_element.send_keys(answer[0])
            register_bid_qa(job_id, PLATFORM, question, answer[0])
    except:
        pass

    try:
        button_website_experience = page_content.find_element(By.CSS_SELECTOR, "button[aria-label='Add Websites']")
        question = "Website"
        answer = get_answer(PLATFORM, question)
        if answer is None:
            log_unknown_question(PLATFORM, question, url, job_id)
            unknown_questions.append(question)
        else:
            button_website_experience.click()
            time.sleep(1)
            website_container = page_content.find_element(By.CSS_SELECTOR, "div[data-automation-id='formField-website']")
            website_element = website_container.find_element(By.CSS_SELECTOR, "input[data-automation-id='website']")
            website_element.send_keys(answer[0])
            register_bid_qa(job_id, PLATFORM, question, answer[0])
    except: pass


    try:
        linkedin_element = driver.find_element(By.CSS_SELECTOR, "[data-automation-id='linkedinQuestion']")
        question = "LinkedIn"
        answer = get_answer(PLATFORM, question)
        if answer is None:
            log_unknown_question(PLATFORM, question, url, job_id)
            unknown_questions.append(question)
        else:
            actual_answer = autofill(linkedin_element, driver, answer)
            register_bid_qa(job_id, PLATFORM, question, actual_answer)
    except: pass

    driver.execute_script('document.querySelector("header").setAttribute("style", "display: block")')
    driver.execute_script('document.querySelector("div[data-automation-id=\'footerContainer\'] + div").setAttribute("style", "display: block")')

    if len(unknown_questions) > 0:
        raise Exception("Has unknown question: \n" + "\n".join(unknown_questions))

    next_button = driver.find_element(By.CSS_SELECTOR, "button[data-automation-id='bottom-navigation-next-button']")
    next_button.click()
    

def bid(driver: webdriver.Chrome, url: str, job_id: str):
    parsed_url = urlparse(driver.current_url)
    if not parsed_url.path.endswith("/login"):
        if not step1(driver, url):
            raise Exception("Step1 failed.")
        print("Passed step1")
        if not step2(driver, url):
            raise Exception("Step2 failed.")
        print("Passed step2")
    
    parsed_url = urlparse(driver.current_url)
    if parsed_url.path.endswith("/login"):
        time.sleep(1)
        if not step3(driver, url):
            raise Exception("Step3 failed.")
        print("Passed step3")
        time.sleep(1)
        if not step4(driver, url, job_id):
            raise Exception("Step4 failed.")
        print("Passed step4")

    global previous_page
    previous_page = ""

    while True:
        time.sleep(3)
        content_page = wait_for_next_step(driver)
        print("Passed", previous_page)
        try:
            if previous_page == "Start Your Application":
                step2(driver, url)
            elif previous_page == "My Experience":
                step_experience(driver, content_page, url, job_id)
            elif previous_page == "Review":
                step_submit(driver, content_page, url)
                return
            else:
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