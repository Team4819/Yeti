import yeti


class ThrusterModule(yeti.IterativeModule):

    def __init__(self):
        self.add_property("value")
        self.update_on_property("value")
        self.set_update_rate(min=20, max=20)

    def start(self):
        # Start thruster
        pass

    def update(self):
        value = self.get_property("value", timeout=1000)
        # Drive thruster
        pass

    def stop(self):
        # Stop thruster
        pass

if __file__ == "__main__":
    yeti.bootstrap_module(ThrusterModule)