#! /usr/bin/env python3

import sys
import os
from global_variables import (
    PRINT_DIR_HOME,
    PYTHON_PATH,
    FUNCTIONS_DIR_HOME)

"""
below this point cmd_farewell functions. That specify the behavior of the cmd prompt when
closing. communication from the python process to the cmd is through a custom exist code
"""

cmd_farewells =rf"""rem custom exit code summary:
rem 0 (default) - display "press any key to continue. . ." message
rem 900 - close cmd that runs .bat file
rem 901 - remove folder that runs .bat file
rem [902, 910] - reserved error status numbers
rem >910 - call python script and pass exit status

if %errorlevel% equ 900 (
    exit
) else if %errorlevel% equ 901 (
rem set "script_folder=%~dp0"
"C:\Program Files (x86)\IObit\IObit Unlocker\IObitUnlocker.exe" "/Delete" "%~dp0"
) else if %errorlevel% gtr 910 (
    pause
"{PYTHON_PATH}" "{os.path.join(FUNCTIONS_DIR_HOME, 'cmd_farewell_handler.py')}" "%errorlevel%
) else (
    pause
)"""

def exit_cmd_farewell():
    """ exit python with a 900 exit status which closes the cmd that runs the batch process """
    sys.exit(900)

def remove_directory_cmd_farewell():
    """ exit python and remove the directory that holds the .bat script """
    # TODO: much more needs to be checked, this is outright dangurous

    sys.exit(901)

def open_wachtrij_folder_cmd_farewell():
    """ exit python with a 911 exit status which open the WACHTRIJ folder """
    sys.exit(911)

def open_gesliced_folder_cmd_farewell():
    """ exit python with a 912 exit status which open the GESLICED folder """
    sys.exit(912)


if __name__ == '__main__':
    """ handle the cmd farewell based on the exit_status """

    exit_status = int(sys.argv[1])

    if exit_status == 911:
        os.startfile(os.path.join(PRINT_DIR_HOME, 'WACHTRIJ'))
    elif exit_status == 912:
        os.startfile(os.path.join(PRINT_DIR_HOME, 'GESLICED'))
    else:
        input(f'No behavior defined for exit status {exit_status}')
