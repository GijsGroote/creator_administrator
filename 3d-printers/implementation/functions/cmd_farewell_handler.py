"""
Specify behavior when cmd is closing, the cmd saying farewell.

Communication from the python process to the cmd is through a exist status.
"""

import sys
import os

from global_variables import (
    PRINT_DIR_HOME,
    PYTHON_PATH,
    FUNCTIONS_DIR_HOME,
    IOBIT_UNLOCKER_PATH)


cmd_farewells = rf"""rem custom exit code summary:
rem 0 (default) - display "press any key to continue. . ." message
rem 900 - close cmd that runs .bat file
rem 901 - remove folder that runs .bat file
rem 902 - remove folder and close cmd that runs .bat file
rem [903, 910] - reserved error status numbers
rem >910 - call python script and pass exit status

if %errorlevel% equ 900 (
    exit
) else if %errorlevel% equ 901 (
    "{IOBIT_UNLOCKER_PATH}" "/Delete" "%~dp0"
    pause
) else if %errorlevel% equ 902 (
    "{IOBIT_UNLOCKER_PATH}" "/Delete" "%~dp0"
    exit
) else if %errorlevel% gtr 910 (
rem error level could be higher than 910 and should not do this
    pause
"{PYTHON_PATH}" "{os.path.join(FUNCTIONS_DIR_HOME, 'cmd_farewell_handler.py')}" "%errorlevel%
) else (
    pause
)"""


def exit_cmd_farewell():
    """ Exit python with a 900 exit status which closes the cmd that runs the batch process. """
    sys.exit(900)


def remove_directory_cmd_farewell():
    """ Exit python and remove the directory that holds the .bat script. """

    if os.getcwd().startswith(PRINT_DIR_HOME):
        sys.exit(901)
    else:
        raise ValueError(f'the working directory must be a subdirectory of {PRINT_DIR_HOME} '
                         f'and the working directory is {os.getcwd()}')



def remove_directory_and_close_cmd_farewell():
    """ Exit python, remove the directory and close cmd that holds the .bat script. """

    if os.getcwd().lower().startswith(PRINT_DIR_HOME.lower()):
        sys.exit(902)
    else:
        raise ValueError(f'the working directory must be a subdirectory of {PRINT_DIR_HOME} '
                         f'and the working directory is {os.getcwd()}')



def open_wachtrij_folder_cmd_farewell():
    """ Exit python with a 911 exit status which open the WACHTRIJ folder. """
    sys.exit(911)


def open_gesliced_folder_cmd_farewell():
    """ Exit python with a 912 exit status which open the GESLICED folder. """
    sys.exit(912)


if __name__ == '__main__':

    error_level = int(sys.argv[1])

    if error_level == 911:
        os.startfile(os.path.join(PRINT_DIR_HOME, 'WACHTRIJ'))
    elif error_level == 912:
        os.startfile(os.path.join(PRINT_DIR_HOME, 'GESLICED'))
    else:
        input(f'No behavior defined for exit status {error_level}')
