from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import yaml
from config import WORKSPACE_PATH, SERVICE_PORT
import time
from threading import Thread
from plyer import notification


def create_direct_driver(block_image: bool = True) -> webdriver.Chrome:
    chrome_options = Options()
    if block_image is True:
        chrome_options.add_extension('../bin/Block image 1.1.0.0.crx')
    chrome_options.add_argument('--disable-features=OptimizationGuideModelDownloading,OptimizationHintsFetching,OptimizationTargetPrediction,OptimizationHints')
    chrome_options.add_argument('user-data-dir=profile')

    return webdriver.Chrome(executable_path="../bin/chromedriver", chrome_options=chrome_options)

driver = create_direct_driver(True)
driver.get("https://www.linkedin.com/messaging")
# driver.get("https://sites.hopanatech.com/hopmon/")

chats = {}
try:
    with open(f'{WORKSPACE_PATH}/quick_chat.yaml', "r") as stream:
        chats = yaml.safe_load(stream) or {}
except: pass

driver.execute_script('''
    window.shortcut_queue = []
''')
with open('./style.css', "r") as stream:
    css = stream.read()
    driver.execute_script('''
        const styler = document.createElement('style');
        styler.innerText = arguments[0]
        document.head.appendChild(styler)
    ''', css)

wrapper = driver.execute_script('''
    const wrapper = document.createElement('div');
    wrapper.setAttribute('class', 'ext-sidebar')
    document.body.appendChild(wrapper);
    return wrapper
''')


items = []
for shortcut in chats:
    content = chats[shortcut]

    item = driver.execute_script('''
        const item = document.createElement('div');
        item.setAttribute('class', 'ext-shortcut-item')
        item.addEventListener('click', () => window.shortcut_queue.push(arguments[1]))
        arguments[0].appendChild(item);
        return item
    '''.replace("{PORT}", str(SERVICE_PORT)), wrapper, shortcut)
    shortcut_element = driver.execute_script('''
        const item = document.createElement('p');
        item.setAttribute('class', 'ext-shortcut-item-title')
        item.innerText = arguments[1]
        arguments[0].appendChild(item);
        return item
    ''', item, shortcut)
    title_element = driver.execute_script('''
        const item = document.createElement('div');
        item.setAttribute('class', 'ext-shortcut-item-content')
        item.innerText = arguments[1]
        arguments[0].appendChild(item);
        return item
    ''', item, content.replace('\n', ' '))
    
    items.append(item)

def process_operation(operations):
    try:
        message_box = driver.find_element(By.CLASS_NAME, "msg-form__contenteditable")
        for operation in operations:
            message = chats[operation]
            parts = message.split('\n')
            for part in parts:
                message_box.send_keys(part)
                action = ActionChains(driver)
                action.key_down(Keys.SHIFT)
                action.key_down(Keys.ENTER)
                action.key_up(Keys.ENTER)
                action.key_up(Keys.SHIFT)
                action.perform()
        if len(operations) > 0:
            message_box.send_keys(Keys.ENTER)
    except Exception as e:
        print(e)


def notification_handler():
    original = []
    clear_interval = 12
    clear_head = clear_interval
    while True:
        badges = driver.find_elements(By.CSS_SELECTOR, ".msg-conversation-card .msg-conversation-card__unread-count .notification-badge")
        notified = []
        if len(badges) > 0:
            for badge in badges:
                inter = badge.find_element(By.XPATH, "./../../../../..")
                title_element = inter.find_element(By.CSS_SELECTOR, ".msg-conversation-card__row > h3")
                notified.append(title_element.text)
        new_senders = []
        for item in notified:
            if item not in original:
                new_senders.append(item)
        original = notified
        if len(new_senders) > 0:
            notification.notify(
                title = "New LinkedIn Message",
                message=", ".join(new_senders) + " sent messages!",
                timeout=30
            )
        
        clear_head -= 1
        if clear_head == 0:
            clear_head = clear_interval
            original = []
        time.sleep(5)
notification_thread = Thread(target=notification_handler)
notification_thread.start()


def operation_handler():
    original = []
    clear_interval = 12
    clear_head = clear_interval
    while True:
        shortcut_queue = driver.execute_script('return window.shortcut_queue')
        driver.execute_script('window.shortcut_queue = []')
        process_operation(shortcut_queue)
        time.sleep(0.2)
operation_thread = Thread(target=operation_handler)
operation_thread.start()