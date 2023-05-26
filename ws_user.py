import requests
import hmac
import hashlib
import time
import json
from websocket import create_connection

# ... (tu función generate_signature y get_user_balance aquí) ...
def generate_signature(req, secret_key):
    # First ensure the params are alphabetically sorted by key
    param_str = ""

    def params_to_str(obj):
        return_str = ""
        for key in sorted(obj):
            return_str += key
            if obj[key] is None:
                return_str += 'null'
            else:
                return_str += str(obj[key])
        return return_str

    if "params" in req:
        param_str = params_to_str(req['params'])

    payload_str = req['method'] + \
        str(req['id']) + req['api_key'] + param_str + str(req['nonce'])

    sig = hmac.new(
        bytes(str(secret_key), 'utf-8'),
        msg=bytes(payload_str, 'utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()

    return sig


def on_message(ws, message):
    msg = json.loads(message)
    if msg['method'] == 'public/heartbeat':
        heartbeat_response = {
            "id": msg['id'],
            "method": "public/respond-heartbeat",
            "code": 0
        }
        ws.send(json.dumps(heartbeat_response))
    else:
        print("Received message:", message)


def connect_websocket(api_key, secret_key, channel):
    ws = create_connection("wss://deriv-stream.crypto.com/v1/user")

    ws.settimeout(5)

    nonce = int(time.time() * 1000)
    auth_req = {
        "id": 1,
        "method": "public/auth",
        "api_key": api_key,
        "nonce": nonce
    }
    auth_req['sig'] = generate_signature(auth_req, secret_key)
    ws.send(json.dumps(auth_req))

    auth_response = json.loads(ws.recv())
    if auth_response['code'] == 0:
        print("Authentication successful")
        subscribe_req = {
            "id": 2,
            "method": "subscribe",
            "params": {
                "channels": [channel]
            }
        }
        ws.send(json.dumps(subscribe_req))

        while True:
            try:
                message = ws.recv()
                on_message(ws, message)
            except Exception as e:
                print("Error:", e)
                break
    else:
        print("Authentication failed")

    ws.close()

    
# config    
api_key = 'your_api_key'
secret_key = 'your_secret_key'
# channel balance for example : https://exchange-docs.crypto.com/derivatives/index.html?javascript#user-balance
channel = 'user.balance' 

# execute
connect_websocket(api_key, secret_key, channel )

