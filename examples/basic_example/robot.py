#!/usr/bin/env python3

import wpilib
from os.path import dirname, abspath
from yeti import YetiRobot


class MyRobot(YetiRobot):

    # Tell YetiRobot to look for yeti.yml in this directory.
    config_dir = abspath(dirname(__file__))

if __name__ == "__main__":
    wpilib.run(MyRobot)
