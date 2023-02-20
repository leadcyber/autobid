import logging
from datetime import datetime
from utils.db import register_bid_qa

logging.basicConfig(filename="./log/bid/common_logs.log", level=logging.DEBUG, format="%(asctime)s %(message)s", filemode="w")

def log_unknown_question(platform: str, question: str, url: str, job_id: str = None):
    if job_id is not None:
        register_bid_qa(job_id, platform, question, None)
    with open('./log/bid/unknown_questions.log', 'a') as log_file:
        log_file.write(f'"{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}" - "{platform}" - "{question}" - "{url}"\n')

def log_bid(url: str, success: bool, message: str="succeed"):
    filename = './log/bid/bid_succeeded.log' if success else './log/bid/bid_failed.log'
    with open(filename, 'a') as log_file:
        log_file.write(f'"{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}" - "{url}" - "{message}"\n')

def log_indeed_external(url: str):
    filename = './log/bid/indeed_external.log'
    with open(filename, 'a') as log_file:
        # log_file.write(f'"{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}" - "{url}"\n')
        log_file.write(f'{url}\n')

def log_qa(platform: str, question: str, answer: str):
    filename = './log/bid/qa.log'
    with open(filename, 'a') as log_file:
        log_file.write(f'"{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}" - "{platform}" - "{question}" : "{answer}"\n')

def log_autobid(url: str, success: bool, message: str="succeed"):
    filename = './log/bid/autobid_success.log' if success else './log/bid/autobid_failed.log'
    if success is False:
        _log_autobid_fail_list(url)
    with open(filename, 'a') as log_file:
        log_file.write(f'"{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}" - "{url}" - "{message}"\n')

def _log_autobid_fail_list(url: str):
    filename = './log/bid/autobid_failed_list.log'
    with open(filename, 'a') as log_file:
        log_file.write(f'{url}\n')