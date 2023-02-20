import logging
from datetime import datetime

# logging.basicConfig(filename="./debug.log", level=logging.DEBUG, format="%(asctime)s %(message)s", filemode="w")

with open('./debug.log', 'w') as debug_file:
    pass

def println(line: str):
    with open('./debug.log', 'a') as debug_file:
        debug_file.write(f'{line}\n')
