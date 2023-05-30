from pynput import keyboard
from threading import Thread
from urllib.parse import urlparse
from datetime import datetime
import time

period = 60
safe_window = ( 5, 3 )
warn_timestamp = datetime.now().timestamp() + period

def timer_thread_handler():
    global warn_timestamp
    while True:
        current_timestamp = datetime.now().timestamp()

        left = warn_timestamp - current_timestamp - safe_window[0]
        print("s")
        time.sleep(left)

        # Risky session
        print("---------")
        while True:
            current_timestamp = datetime.now().timestamp()
            if current_timestamp >= warn_timestamp + safe_window[1]:
                break

        warn_timestamp += period

timer_thread = Thread(target=timer_thread_handler)


seq_count = 0

def record_moment():
    global warn_timestamp
    warn_timestamp = datetime.now().timestamp() + period
    timer_thread.start()

def on_press(key):
    global seq_count
    if key == keyboard.Key.caps_lock:
        seq_count += 1
        if seq_count == 2:
            record_moment()
            # seq_count = 0



with keyboard.Listener(on_press=on_press) as listener:
    print("Listening to autobid urls.")
    listener.join()