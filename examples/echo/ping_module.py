import sys
import time
from py import yeti


class PingModule(yeti.IterativeModule):
    last_time = 0

    def start(self):
        last_time = time.time()

    def update(self):
        if "target" in self.module_config:
            ping = self.get_state("ping", self.module_config["target"])

            message = "This is {}, and {} says '{}'!".format(self.module_id, self.module_config["target"],
                                                             self.get_state("message", self.module_config["target"]))
