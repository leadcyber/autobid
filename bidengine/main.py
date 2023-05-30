from pynput import keyboard
import pyperclip
from threading import Thread
import router
from config import config
import glvar
from webinterface import register_api_handler, listen_bidder_interface
from urllib.parse import urlparse
from autobid.env import WORKSPACE_PATH
from utils.resume import generate_resume_to_file

pressed_keys = set()
triggered = []
bid_queue = []

latest_bid = ""
latest_bid_thread: Thread = None

def h_thread_handler():
    global bid_queue, latest_bid, latest_bid_thread
    while True:
        if len(bid_queue) == 0:
            continue
        current_bid = bid_queue[0]
        latest_bid = current_bid
        print(f"\nStart processing {current_bid['url']} ...")
        latest_bid_thread = router.process(current_bid)
        bid_queue = bid_queue[1:]

h_thread = Thread(target=h_thread_handler)
h_thread.start()

def request_bid(bid_data):
    parse_result = urlparse(bid_data["url"])
    if parse_result.hostname is None:
        return None
    
    if bid_data is not None:
        bid_queue.append(bid_data)

def request_bid_from_clipboard():
    copied_str = pyperclip.paste()
    request_bid({ "url": copied_str, "autoMode": False, "exceptionMode": False, "requestConnect": False})

def request_generate_resume_from_clipboard_jd(position):
    copied_jd = pyperclip.paste()
    print(copied_jd)
    generate_resume_to_file(position, copied_jd, '/Users/snyper/Downloads/Michael.C Resume.pdf')

def request_rebid():
    if latest_bid_thread is not None:
        print("Attempting rebid...")
        glvar.terminate(latest_bid["url"])
        latest_bid_thread.join()
        glvar.terminate("")
        bid_queue.append(latest_bid)
    else:
        print("No previous bid attempt.")
def set_current_profile(id: int):
    config.set_current_profile(id)



COMBINATIONS = [
    { "keys": { keyboard.Key.cmd_r, keyboard.Key.ctrl_l, keyboard.KeyCode(char='e') }, "handler": request_rebid },
    { "keys": { keyboard.Key.cmd_r, keyboard.KeyCode(char='e') }, "handler": request_bid_from_clipboard },
    { "keys": { keyboard.Key.cmd_r, keyboard.Key.ctrl, keyboard.KeyCode(char='1') }, "handler": lambda: request_generate_resume_from_clipboard_jd("Senior Front End Engineer") },
    { "keys": { keyboard.Key.cmd_r, keyboard.Key.ctrl, keyboard.KeyCode(char='2') }, "handler": lambda: request_generate_resume_from_clipboard_jd("Senior Full Stack Engineer") },
    { "keys": { keyboard.Key.cmd_r, keyboard.Key.ctrl, keyboard.KeyCode(char='3') }, "handler": lambda: request_generate_resume_from_clipboard_jd("Senior Software Engineer") },
    { "keys": { keyboard.Key.cmd_r, keyboard.Key.ctrl, keyboard.KeyCode(char='4') }, "handler": lambda: set_current_profile(4) },
    { "keys": { keyboard.Key.cmd_r, keyboard.Key.ctrl, keyboard.KeyCode(char='5') }, "handler": lambda: set_current_profile(5) },
    { "keys": { keyboard.Key.cmd_r, keyboard.Key.ctrl, keyboard.KeyCode(char='6') }, "handler": lambda: set_current_profile(6) },
    { "keys": { keyboard.Key.cmd_r, keyboard.Key.ctrl, keyboard.KeyCode(char='7') }, "handler": lambda: set_current_profile(7) },
    { "keys": { keyboard.Key.cmd_r, keyboard.Key.ctrl, keyboard.KeyCode(char='8') }, "handler": lambda: set_current_profile(8) },
    { "keys": { keyboard.Key.cmd_r, keyboard.Key.ctrl, keyboard.KeyCode(char='9') }, "handler": lambda: set_current_profile(9) },
]

def on_press(key):
    if any([key in COMBO['keys'] for COMBO in COMBINATIONS]):
        pressed_keys.add(key)
        matches = [ all(k in pressed_keys for k in COMBO['keys']) for COMBO in COMBINATIONS ]
        for index, match in enumerate(matches):
            if match is True:
                triggered.append(COMBINATIONS[index]['handler'])
                break

def on_release(key):
    if any([key in COMBO['keys'] for COMBO in COMBINATIONS]):
        if key in pressed_keys:
            pressed_keys.remove(key)
    if len(pressed_keys) == 0:
        for handler in triggered:
            handler()
        triggered.clear()

register_api_handler({ "apply": request_bid })
listen_bidder_interface()

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    print("Listening to autobid urls.")
    listener.join()