import sys
import time
import yeti


class PingModule(yeti.IterativeModule):
    first_start = True

    def start(self):
        print("Started!")
        if self.first_start:
            self.set_state("flag", False)
            self.first_start = False
        self.last_set = time.time()
        self.last_value = False

    def update(self):
        if "target" in self.module_config:
            if time.time() - self.last_set > 5:
                print("Setting flag on {}".format(self.module_config["target"]))
                self.set_state("flag", True, self.module_config["target"])
                self.last_set = time.time()
            curr_value = self.get_state("flag", self.module_config["target"])
            if not curr_value and self.last_value:
                print("Remote value reset in {} seconds.".format(time.time() - self.last_set))
            self.last_value = curr_value
        if self.get_state("flag"):
            print("Reset flag!")
            self.set_state("flag", False)

if __name__ == "__main__":
    yeti.bootstrap_module(PingModule, sys.argv[1], sys.argv[2])
