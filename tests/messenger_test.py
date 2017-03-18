from yeti import Messenger

m0 = Messenger("m0")
m1 = Messenger("m1")
m2 = Messenger("m2")
m3 = Messenger("m3")
m4 = Messenger("m4")
m5 = Messenger("m5")


def on_m0_telegram(data):
    print(data)
    return "Gotcha!"

m0.register_message_type("telegram", on_m0_telegram)

m4.register_messenger_address("m0", "127.0.0.1", 9000, 9010)
m2.register_messenger_address("m4", "127.0.0.1", 9004, 9014)
m5.register_messenger_address("m2", "127.0.0.1", 9002, 9012)
m2.register_messenger_address("m5", "127.0.0.1", 9005, 9015)
m5.register_messenger_address("m3", "127.0.0.1", 9003, 9013)

m0.start_server("127.0.0.1", 9000, 9010)
m1.start_server("127.0.0.1", 9001, 9011)
m2.start_server("127.0.0.1", 9002, 9012)
m3.start_server("127.0.0.1", 9003, 9013)
m4.start_server("127.0.0.1", 9004, 9014)
m5.start_server("127.0.0.1", 9005, 9015)

response = m5.send_message("telegram", "Hi!", "m0", blocking=True)
print(response)