#! /usr/bin/env python3

import os

from global_variables import (
    PRINT_DIR_HOME,
    PYTHON_PATH,
    FUNCTIONS_DIR_HOME)
from cmd_farewell_handler import cmd_farewells

if __name__ == "__main__":
    """ create inbox.bat in the parent folder of PRINT_DIR_HOME """
    python_path = os.path.join(FUNCTIONS_DIR_HOME, 'inbox.py')
    bat_file = open(os.path.join(PRINT_DIR_HOME, '../', 'inbox.bat'), 'w+')
    bat_file.write(rf"""
@echo off
"{PYTHON_PATH}" "{python_path}"
    
{cmd_farewells}
""")
    bat_file.close()