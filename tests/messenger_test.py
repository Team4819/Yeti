from yeti import Messenger



m1 = Messenger()
m2 = Messenger()

def m1_msg(message):
    print(message["data"])

m1.message_types = {"telegram": {"handler": m1_msg}}
