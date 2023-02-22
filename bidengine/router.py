from webbrowser import Chrome
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from driver import create_direct_driver, get_free_profile, set_profile_state, is_profile_free
from urllib.parse import urlparse

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bidders.linkedin import bid as bid_linkedin
from bidders.linkedin import wait_for_apply as wait_linkedin_apply

from bidders.lever import bid as bid_lever
from bidders.lever import wait_for_apply as wait_lever_apply

from bidders.greenhouse import bid as bid_greenhouse
from bidders.greenhouse import get_inner_greenhouse
from bidders.greenhouse import wait_for_apply as wait_greenhouse_apply

from bidders.jobprotocol import bid as bid_jobprotocol
from bidders.jobprotocol import wait_for_apply as wait_jobprotocol_apply

from bidders.resumator import bid as bid_resumator
from bidders.resumator import is_resumator
from bidders.resumator import wait_for_apply as wait_resumator_apply

from bidders.ashbyhq import bid as bid_ashbyhq
from bidders.ashbyhq import wait_for_apply as wait_ashbyhq_apply

from bidders.dover import bid as bid_dover
from bidders.dover import wait_for_apply as wait_dover_apply

from bidders.bamboohr import bid as bid_bamboohr
from bidders.bamboohr import wait_for_apply as wait_bamboohr_apply

from bidders.newrelic import bid as bid_newrelic
from bidders.newrelic import wait_for_apply as wait_newrelic_apply

from bidders.newrelic import bid as bid_laskie
from bidders.newrelic import wait_for_apply as wait_laskie_apply

from bidders.jobvite import bid as bid_jobvite
from bidders.jobvite import wait_for_apply as wait_jobvite_apply

from bidders.myworkdayjobs import bid as bid_myworkdayjobs
from bidders.myworkdayjobs import wait_for_apply as wait_myworkdayjobs_apply

from bidders.smartrecruiters import bid as bid_smartrecruiters
from bidders.smartrecruiters import wait_for_apply as wait_smartrecruiters_apply

from bidders.dice import bid as bid_dice
from bidders.dice import wait_for_apply as wait_dice_apply

from bidders.recruitics import bid as bid_recruitics
from bidders.recruitics import wait_for_apply as wait_recruitics_apply

from bidders.icims import bid as bid_icims
from bidders.icims import wait_for_apply as wait_icims_apply

from bidders.common import wait_window_close

from threading import Thread, Lock

from utils import logger, db
import os
import json
from webinterface import send_to_dashboard

profile_lock = Lock()

def preprocessed_url(parse_result, url: str):
    print(parse_result)
    if parse_result.netloc.endswith("lever.co") and not parse_result.path.endswith("/apply"):
        return f"{parse_result.scheme}://{parse_result.netloc}{parse_result.path}/apply"
    if parse_result.netloc.endswith("ashbyhq.com") and not parse_result.path.endswith("/application"):
        return f"{parse_result.scheme}://{parse_result.netloc}{parse_result.path}/application"
    if parse_result.netloc.endswith("jobvite.com") and not parse_result.path.endswith("/apply"):
        return f"{parse_result.scheme}://{parse_result.netloc}{parse_result.path.replace('careers/', '')}/apply"
    return url

def get_redirected_url(driver: webdriver.Chrome):
    url = get_inner_greenhouse(driver)
    if url is not None:
        return url
    return None

def wait_redirect(driver: webdriver.Chrome):
    parse_result = urlparse(driver.current_url)
    if parse_result.hostname.endswith("greenhouse.io"):
        return driver.current_url
    if parse_result.hostname.endswith("dice.com"):
        return driver.current_url
    if parse_result.hostname.endswith("grnh.se"):
        WebDriverWait(driver, 60).until(EC.url_matches("(greenhouse.io)$"))
        return driver.current_url
    if parse_result.hostname.endswith("click.appcast.io"):
        WebDriverWait(driver, 60).until(EC.url_matches("(dice.com)$"))
        return driver.current_url
    return None

def process_external_bid_thread(parse_result, bid_data):
    global profile_lock

    url = bid_data["url"]
    auto_mode = bid_data["autoMode"]
    exception_mode = bid_data["exceptionMode"]
    request_connect = bid_data["requestConnect"]

    job_id = ""
    if "id" in bid_data:
        job_id = bid_data["id"]
    else:
        striped_url = url.strip("\n").strip(" ").strip("/")
        job = db.job_collection.find_one({"jobUrl": striped_url}) or db.job_collection.find_one({ "pageData.applyUrl": striped_url })
        if job is not None:
            job_id = job["_id"]
            print(job_id)
    original_url = url
    
    driver = None
    free_profile_name = None
    try:
        if parse_result.netloc.endswith("linkedin.com"):
            free_profile_name = get_free_profile("linkedin")
        else:
            free_profile_name = get_free_profile("")
    except:
        print("No available profiles now.")
        if auto_mode == True:
            logger.log_autobid(url, False, f"Failed to get free profile")
            send_to_dashboard({"type":"failed", "payload": {"id": job_id, "reason": "no-free-profile"}})
        return


    try:
        driver = create_direct_driver(free_profile_name)
    except Exception as e:
        print(f"Unable to launch browser with error: {str(e)}")
        logger.log_bid(url, False, f"Unable to launch browser with error: {str(e)}")
        if auto_mode == True:
            logger.log_autobid(url, False, "Unable to launch browser with error")
            send_to_dashboard({"type":"failed", "payload": {"id": job_id, "reason": "unable-launch-browser"}})
        return
    
    set_profile_state(free_profile_name, 1)
    profile_lock.release()

    driver.get(preprocessed_url(parse_result, url))

    try:
        redirected_url = get_redirected_url(driver)
        if redirected_url is not None:
            url = redirected_url
            driver.get(url)
            parse_result = urlparse(url)

        awaited_url = wait_redirect(driver)
        if awaited_url is not None:
            print(awaited_url)
            url = awaited_url
            parse_result = urlparse(awaited_url)
    except:
        try:
            driver.quit()
        except: pass
        set_profile_state(free_profile_name, 0)
        if exception_mode == False:
            wait_window_close(driver, original_url)
        else:
            try:
                driver.close()
            except: pass
        if auto_mode == True:
            logger.log_autobid(url, False, "URL preprocessing failed.")
            send_to_dashboard({"type":"failed", "payload": {"id": job_id, "reason": "url-preprocess-failed"}})
        return

    bid = None
    wait = None

    if parse_result.netloc.endswith("linkedin.com"):
        bid, wait = bid_linkedin, wait_linkedin_apply
    elif parse_result.netloc.endswith("lever.co"):
        bid, wait = bid_lever, wait_lever_apply
    elif parse_result.netloc.endswith("greenhouse.io"):
        bid, wait = bid_greenhouse, wait_greenhouse_apply
    elif parse_result.netloc.endswith("jobprotocol.xyz"):
        bid, wait = bid_jobprotocol, wait_jobprotocol_apply
    elif is_resumator(driver):
        bid, wait = bid_resumator, wait_resumator_apply
    elif parse_result.netloc.endswith("ashbyhq.com"):
        bid, wait = bid_ashbyhq, wait_ashbyhq_apply
    elif parse_result.netloc.endswith("dover.io"):
        bid, wait = bid_dover, wait_dover_apply
    elif parse_result.netloc.endswith("bamboohr.com"):
        bid, wait = bid_bamboohr, wait_bamboohr_apply
    elif parse_result.netloc.endswith("newrelic.com"):
        bid, wait = bid_newrelic, wait_newrelic_apply
    elif parse_result.netloc.endswith("laskie.com"):
        bid, wait = bid_laskie, wait_laskie_apply
    elif parse_result.netloc.endswith("jobvite.com"):
        bid, wait = bid_jobvite, wait_jobvite_apply
    elif parse_result.netloc.endswith("myworkdayjobs.com") or parse_result.netloc.endswith("myworkdaysite.com"):
        bid, wait = bid_myworkdayjobs, wait_myworkdayjobs_apply
    elif parse_result.netloc.endswith("smartrecruiters.com"):
        bid, wait = bid_smartrecruiters, wait_smartrecruiters_apply
    elif parse_result.netloc.endswith("dice.com"):
        bid, wait = bid_dice, wait_dice_apply
    elif parse_result.netloc.endswith("recruitics.com"):
        bid, wait = bid_recruitics, wait_recruitics_apply
    elif parse_result.netloc.endswith("icims.com"):
        bid, wait = bid_icims, wait_icims_apply
    else:
        pass
    
    if bid is None:
        print(f"Unknown job platform on {url}!")
        logger.log_bid(url, False, "Unknown job platform")
        if exception_mode == False:
            wait_window_close(driver, original_url)
        else:
            try:
                driver.close()
            except: pass
        set_profile_state(free_profile_name, 0)
        if auto_mode == True:
            logger.log_autobid(url, False, "Unknown job platform")
            send_to_dashboard({"type":"failed", "payload": {"id": job_id, "reason": "unknown-job-platform"}})
        return

    bid_succeed = True
    try:
        if bid == bid_linkedin:
            bid(driver, url, job_id, request_connect)
        else:
            bid(driver, url, job_id)
        print(f"\nBid succeeded on {url}!")
        logger.log_bid(url, True)
        bid_succeed = True
        if auto_mode == True:
            logger.log_autobid(url, True)
    except Exception as e:
        print(f"\nBid failed on {url} with following error!\n'{str(e)}'\n")
        logger.log_bid(url, False, str(e))
        bid_succeed = False
        if auto_mode == True:
            logger.log_autobid(url, False, str(e))
    finally:
        end_reason = False
        if exception_mode is False:
            end_reason = wait(driver, original_url)
        try:
            driver.quit()
        except: pass
        if end_reason != "rebid":
            if bid_succeed:
                send_to_dashboard({"type":"success", "payload": {"id": job_id}})
            else:
                send_to_dashboard({"type":"failed", "payload": {"id": job_id, "reason": "bid_failed"}})
        set_profile_state(free_profile_name, 0)

def process(bid_data) -> Thread:
    global profile_lock
    
    print("bidata", bid_data)
    parse_result = urlparse(bid_data["url"])
    bid_thread = process_external_bid_thread
    if parse_result.hostname is None:
        return None
    profile_lock.acquire()
    p_handle = Thread(target=bid_thread, args=[ parse_result, bid_data ])
    p_handle.start()
    return p_handle