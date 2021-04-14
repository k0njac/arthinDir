#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from lib.controller import *

if sys.version_info < (3, 0):
    sys.stdout.write("Sorry, dirsearch requires Python 3.x\n")
    sys.exit(1)
import config
class Program:
    def __init__(self):

        self.script_path = os.path.dirname(os.path.realpath(__file__))
        self.controller = Controller(self.script_path, config)

if __name__ == "__main__":
    main = Program()
