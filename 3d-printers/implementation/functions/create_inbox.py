#! /usr/bin/env python3

import os

from global_variables import (
    PRINT_DIR_HOME,
    PYTHON_DIR_HOME,
    FUNCTIONS_DIR_HOME)


if __name__ == "__main__":
    """ create inbox.bat in the parent folder of PRINT_DIR_HOME """
    python_path = os.path.join(FUNCTIONS_DIR_HOME, 'inbox.py')
    myBat = open(os.path.join(PRINT_DIR_HOME, '../', 'inbox.bat'), 'w+')
    myBat.write(rf"""
    @echo off
    "{PYTHON_DIR_HOME}" "{python_path}"
    pause
    """)
    myBat.close()