from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
from ast import literal_eval

chrome_options = Options()
chrome_options.add_argument('--disable-features=OptimizationGuideModelDownloading,OptimizationHintsFetching,OptimizationTargetPrediction,OptimizationHints')
chrome_options.add_argument('user-data-dir=/Users/mitnix/Library/Caches/Google/Chrome/Profile 25')

driver = webdriver.Chrome(executable_path="./bin/chromedriver", chrome_options=chrome_options)
driver.get("https://gmail.com")
while True:
    pass