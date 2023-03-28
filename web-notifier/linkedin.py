from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def create_direct_driver(block_image: bool = True) -> webdriver.Chrome:
    chrome_options = Options()
    if block_image is True:
        chrome_options.add_extension('./bin/Block image 1.1.0.0.crx')
    chrome_options.add_argument('--disable-features=OptimizationGuideModelDownloading,OptimizationHintsFetching,OptimizationTargetPrediction,OptimizationHints')
    chrome_options.add_argument('user-data-dir=profile')

    return webdriver.Chrome(executable_path="./bin/chromedriver", chrome_options=chrome_options)