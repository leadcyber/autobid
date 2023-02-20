from config import config
from driver import create_direct_driver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.answers import get_answer, is_correct_answer
from utils.logger import log_unknown_question
from selenium.webdriver.remote.webelement import WebElement
from utils import logger, db
from utils.job_parser import is_proper_job_detail, is_proper_job_title, is_proper_job_detail, get_required_skills
from datetime import datetime
from utils.resume import get_most_relevant_template, get_most_relevant_headline, generate_resume_by_data
from selenium.webdriver.common.keys import Keys

PLATFORM = "indeed"

config.current_profile_id = 1
driver = create_direct_driver("indeed")

DEFAULT_RESUME_FILE_NAME = "Resume-Michael-Chilelli.pdf"

def set_indeed_input(field: WebElement, value: str):
    # driver.execute_script(f"arguments[0].setAttribute('value', arguments[1])", field, value)
    # driver.execute_script(f"arguments[0].value = arguments[1]", field, value)
    for i in range(0, 30):
        field.send_keys(Keys.BACKSPACE)
    field.send_keys(value)
def autofill(field: WebElement, answer):
    if field.tag_name == "textarea":
        if field.get_attribute("value") != "":
            return
        field.send_keys(answer[0])
        return
    if field.tag_name == "input":
        input_type = field.get_attribute("type")
        if input_type == "" or input_type == "text" or input_type == "password" or input_type == "number" or input_type == "tel" or input_type == "email":
            if field.get_attribute("value") != "":
                return
            field.send_keys(answer[0])
        else:
            pass
        return
    if field.tag_name == "fieldset":
        label_elements = field.find_elements(By.TAG_NAME, "label")
        label_texts = [ label_element.text for label_element in label_elements ]
        for ans in answer:
            for (index, label_text) in enumerate(label_texts):
                if is_correct_answer(label_text, [ans]):
                    target_id = label_elements[index].get_attribute("for")
                    target_element = field.find_element(By.ID, target_id)
                    driver.execute_script("arguments[0].click()", target_element)
                    if target_element.get_attribute("type") == "radio":
                        return

def autofill_page(page: WebElement, detail_url: str):
    unknown_questions = []
    question_elements = page.find_elements(By.CLASS_NAME, "ia-Questions-item")
    for question_element in question_elements:
        # Find label element
        label_element = question_element.find_element(By.TAG_NAME, "label")

        # Find legend element
        legend_element = None
        try:
            legend_element = question_element.find_element(By.TAG_NAME, "legend")
        except:
            pass

        target_element = None
        question = None
        
        if legend_element is not None:
            question = legend_element.text
            target_element = legend_element.find_element(By.XPATH, "..")
            print("legend", question)
        else:
            question = label_element.text
            target_id = label_element.get_attribute("for")
            if target_id is None or target_id == "":
                continue
            target_element = question_element.find_element(By.ID, target_id)
            if target_element.tag_name == "input" and target_element.get_attribute("radio"):
                continue
            question = question_element.text
        
        if question == "":
            continue
        answer = get_answer(PLATFORM, question)
        if answer is None:
            log_unknown_question(PLATFORM, question, detail_url)
            unknown_questions.append(question)
            continue

        print(question, " : ", answer)
        autofill(target_element, answer)

    if len(unknown_questions) > 0:
        raise Exception("Has unknown question: \n" + "\n".join(unknown_questions))

def add_resume(page: WebElement, position: str, description: str):
    resume_path = generate_resume_by_data("indeed", position, description)
    resume_input = page.find_element(By.CSS_SELECTOR, "input[data-testid='ResumeFileInfoCardReplaceButton-input']")
    resume_input.send_keys(resume_path)
    while True:
        try:
            replace_button = page.find_element(By.CSS_SELECTOR, "[data-testid='ResumeFileInfoCardReplaceButton-button']")
            if replace_button.get_attribute("disabled") != "true":
                return
        except:
            continue
def fill_relevant_experience(page:WebElement, headline: str):
    job_title_element = page.find_element(By.ID, "jobTitle")
    if job_title_element.get_attribute("value") == headline:
        return
    set_indeed_input(job_title_element, headline)

def review_application(page: WebElement, headline: str, resume_composed: bool):
    resume_section_elements = page.find_elements(By.CLASS_NAME, "ia-Review-Resume")
    if len(resume_section_elements) > 0:
        resume_section_element = resume_section_elements[0]
        if resume_composed is False:
            edit_element = resume_section_element.find_element(By.XPATH, ".//a[text()='Edit']")
            edit_element.click()
            return True
    
    exp_section_elements = page.find_elements(By.CLASS_NAME, "ia-Review-WorkExperience")
    if len(exp_section_elements) > 0:
        exp_section_element = exp_section_elements[0]
        if len(exp_section_element.find_elements(By.XPATH, f".//div[text()='{headline}']")) == 0:
            edit_element = exp_section_element.find_element(By.XPATH, ".//a[text()='Edit']")
            edit_element.click()
            return True
    return False

def iterate_job_board():

    while True:
        try:
            header = driver.find_element(By.CSS_SELECTOR, "nav[class='gnav']")
            try:
                header.find_element(By.CSS_SELECTOR, "[data-gnav-element-name='SignIn']")
            except: break
        except: pass

    job_list_element = driver.find_element(By.CLASS_NAME, "jobsearch-ResultsList")
    job_item_elements = job_list_element.find_elements(By.XPATH, "*")

    board_window_before = driver.current_window_handle


    for job_item_element in job_item_elements:
        try:
            result_content_element = job_item_element.find_element(By.CSS_SELECTOR, "td[class='resultContent']")
        except:
            continue
        job_title_element = result_content_element.find_element(By.TAG_NAME, "h2")
        job_link_element = job_title_element.find_element(By.TAG_NAME, "a")

        # Check if the job title is proper
        job_title = job_link_element.text
        print("\n", job_title)
        if not is_proper_job_title(job_title):
            continue
        driver.execute_script("arguments[0].click()", job_link_element)
        time.sleep(8)


        # Parse detail page
        detail_element = WebDriverWait(driver, 10000).until(lambda dr: dr.find_element(By.ID, "jobDescriptionText"))
        # detail_element = driver.find_element(By.ID, "jobDescriptionText")
        company_wrapper_element = driver.find_element(By.CLASS_NAME, "jobsearch-InlineCompanyRating")
        company_element = None
        try:
            company_element = company_wrapper_element.find_element(By.TAG_NAME, "a")
        except:
            try:
                company_element = company_wrapper_element.find_element(By.CLASS_NAME, "jobsearch-InlineCompanyRating-companyHeader")
            except:
                pass
        company_name = company_element.text

        # Display job detail
        # print("title", job_title)
        # print("company", company_element.text)
        # print("salary", salary_element.text)

        # Check if it is proper to bid
        job_detail_html = detail_element.get_attribute('innerHTML')
        # print(job_detail)
        if not is_proper_job_detail(job_detail_html):
            driver.switch_to.window(board_window_before)
            continue

        # job = db.job_collection.insert_one({
        #     "category": "React&Frontend",
        #     "company": company_name,
        #     "position": job_title,
        #     "postedAgo": "1 minutes ago",
        #     "postedDate": datetime.now(),
        #     "scannedDate": datetime.now(),
        #     "copiedDate": datetime.now(),
        #     "location": "",
        #     "salary": "",
        # })

        # Click apply button
        button_element = None
        try:
            button_wrapper_element = driver.find_element(By.CLASS_NAME, "jobsearch-IndeedApplyButton-buttonWrapper")
            button_element = button_wrapper_element.find_element(By.TAG_NAME, "button")
            if button_element.get_attribute("disabled") == "true":
                continue
        except:
            button_wrapper_element = driver.find_element(By.ID, "applyButtonLinkContainer")
            link_element = button_wrapper_element.find_element(By.TAG_NAME, "a")
            external_url = link_element.get_attribute("href")
            print(f"Detected external site {external_url}")
            logger.log_indeed_external(external_url)
            continue

        # Close detail page
        apply_window = None
        while True:
            driver.execute_script("arguments[0].click()", button_element)
            time.sleep(1)
            apply_windows = [x for x in driver.window_handles if x != board_window_before]
            if len(apply_windows) > 0:
                apply_window = apply_windows[0]
                driver.switch_to.window(apply_window)
                break

        # Start filling forms
        previous_page_title_element_id = None
        is_completed = False
        closed = False
        detail_url = "https://indeed.com"
        resume_composed = False
        while True:
            page = None
            continue_button = None
            while True:
                if apply_window not in driver.window_handles:
                    closed = True
                    break
                try:
                    page = driver.find_element(By.CLASS_NAME, "ia-PageAnimation")
                    page_title_element = page.find_element(By.TAG_NAME, "h1")
                except:
                    if apply_window not in driver.window_handles:
                        closed = True
                        break
                    if driver.current_url.endswith("/post-apply"):
                        is_completed = True
                        break
                    continue
                try:
                    page_title = page_title_element.text
                    page_title_element_id = page_title_element.id
                except:
                    page_title = None
                    page_title_element_id = None
                continue_button = page.find_element(By.CLASS_NAME, "ia-continueButton")
                # print(continue_button.get_attribute("disabled"))
                if previous_page_title_element_id != page_title_element_id:
                # if not continue_button.get_attribute("disabled"):
                    break
                time.sleep(1)
            if closed:
                break
            if is_completed:
                break
            previous_page_title_element_id = page_title_element_id
            time.sleep(2)
            # Research page element again after few seconds
            page = driver.find_element(By.CLASS_NAME, "ia-PageAnimation")
            headline = get_most_relevant_headline(job_title)
            
            print("on-page: ", page_title)
            if page_title.startswith("Please review"):
                if review_application(page, headline, resume_composed):
                    time.sleep(2)
                    continue

            is_log = True
            while True:
                try:
                    if "resume" in page_title:
                        resume_composed = True
                        add_resume(page, job_title, job_detail)
                    elif "relevant experience" in page_title:
                        fill_relevant_experience(page, headline)
                    else:
                        autofill_page(page, detail_url)
                    continue_button.click()
                    break
                except Exception as e:
                    print(f"\nBid failed on {detail_url} with following error.\n'{str(e)}'!")
                    if is_log is True:
                        logger.log_bid(detail_url, False, str(e))
                    is_log = False
                    if str(e).startswith("Has unknown question"):
                        time.sleep(10)
                        continue
                    else:
                        break
                        
            time.sleep(2)
        if not closed:
            driver.close()
        driver.switch_to.window(board_window_before)
    time.sleep(1)

def try_next_page():
    try:
        pagination_element = driver.find_element(By.CSS_SELECTOR, "nav[aria-label='pagination']")
        print(pagination_element)
        next_page_button = pagination_element.find_element(By.CSS_SELECTOR, "a[data-testid='pagination-page-next']")
        print(next_page_button)
        driver.execute_script("arguments[0].click()", next_page_button)
        return True
    except: return False

start_url = "https://www.indeed.com/jobs?q=react+OR+angular+OR+vue+OR+frontend+OR+fullstack&rbl=Remote&jlid=aaa2b906602aa8f5&fromage=1&vjk=18cbf0dd614bd9bb"
driver.get(start_url)
while True:
    iterate_job_board()
    if not try_next_page():
        driver.get(start_url)
    time.sleep(60 * 3)
