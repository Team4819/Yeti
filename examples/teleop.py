import sys

from py import yeti


class TeleopModule(yeti.IterativeModule):

    def update(self):
        axes = yeti.get_property("joystick", "axes", timeout=1000)
        # Mix the axes!!!
        yeti.set_property("left_thruster", "value", axes[0] + axes[1] + axes[2])
        # repeat

if __file__ == "__main__":
    yeti.bootstrap_module(TeleopModule, sys.argv[1], sys.argv[2])
