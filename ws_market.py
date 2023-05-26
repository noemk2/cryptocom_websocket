import websocket
import json
import time

def on_message(ws, message):
    data = json.loads(message)
    if data['method'] == 'public/heartbeat':
        heartbeat_response = {
            'id': data['id'],
            'method': 'public/respond-heartbeat',
            'code': 0
        }
        ws.send(json.dumps(heartbeat_response))
    else:
        print(f"Received message: {message}")

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    subscribe_request = {
        'id': 1,
        'method': 'subscribe',
        'params': {
            'channels': ['book.BTCUSD-PERP']
        },
        'nonce': int(time.time() * 1000)
    }
    ws.send(json.dumps(subscribe_request))

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://deriv-stream.crypto.com/v1/market",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
