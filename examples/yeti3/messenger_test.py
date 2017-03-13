import yeti
import time

messenger_1 = yeti.Messenger()
messenger_2 = yeti.Messenger()

received = False
def on_telegram(data):
    global received
    print(data)
    received = data["data"] == "Hello World!"
    #time.sleep(1)
    return {
        "msg_type": "telegram",
        "data": "Wow, you are apparently enthusiastic!"
    }

messenger_2.message_types = {
    "telegram": {
        "handler": on_telegram
    }
}
messenger_1.message_types = messenger_2.message_types

messenger_1.start_server(9000, 9001)
messenger_2.start_server(9002, 9003)

message = {
    "to": "messenger_1",
    "msg_type": "telegram",
    "data": "Hello World!"
}

for _ in range(5):
    result = messenger_1.send_message(message, ("127.0.0.1", 9002), blocking=True)
    #print("test")
    print(result)
    time.sleep(1)

assert received
messenger_1.stop_server()
messenger_2.stop_server()
