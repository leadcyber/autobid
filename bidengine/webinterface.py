import json
from flask import Flask, request
from urllib import request as urlrequest, parse
from config import config
from threading import Thread

handlers = {}
def register_api_handler(h):
    global handlers
    handlers = h

def send_to_dashboard(data):
    request_body = json.dumps({"data": data}).encode()
    req = urlrequest.Request(f'{config.DASHBOARD_URL}/bidder', data=request_body) # this will make the method "POST"
    req.add_header('Content-Type', 'application/json')
    response = urlrequest.urlopen(req)

app = Flask(__name__)

@app.post("/invoke")
def invoke():
    body = json.loads(request.data)
    print(body)
    message_type = body["type"]
    payload = body["payload"]
    if message_type not in handlers:
        print("Message type is invalid.")
        return "invalid message type", 400
    print(f"[pipeline]: {message_type} - {payload}")
    try:
        handlers[message_type](payload)
        return "success", 200
    except Exception as e:
        print(e)
        return str(e), 500

def listen_bidder_interface():
    def ipc_thread_handler():
        print("Listening to bidder port.")
        app.run(port=config.BIDDER_PORT)
    
    global ipc_thread
    ipc_thread = Thread(target=ipc_thread_handler)
    ipc_thread.start()