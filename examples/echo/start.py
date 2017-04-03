import os
import time

from py import yeti

#import echo_module

conf_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "echo_test.yml")

mon = yeti.Monitor("main_mon", conf_path)
mon.start()
mon.start_modules()

time.sleep(1)

# mon2 = yeti.Monitor("slave_mon", conf_path)
# mon2.start()
# mon2.start_modules()

time.sleep(1000)