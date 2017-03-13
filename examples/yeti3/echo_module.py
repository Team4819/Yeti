import yeti
import sys


class EchoModule(yeti.IterativeModule):
    last_message = ""

    def update(self):
        if "target" in self.module_config:
            message = "This is {}, and {} says '{}'!".format(self.module_id, self.module_config["target"], self.get_state("message", self.module_config["target"]))
        else:
            message = "Hello from {}!".format(self.module_id)
        self.set_state("message", message)
        if message != self.last_message:
            print(message)
        self.last_message = message

if __name__ == "__main__":
    yeti.bootstrap_module(EchoModule, sys.argv[1], sys.argv[2])
