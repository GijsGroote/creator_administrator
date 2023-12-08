"""
Specify behavior when cmd is closing, the cmd saying farewell.

Communication from the python process to the cmd is through a exist status.
"""

import sys
import os

def get_cmd_farewells(gv: dict) -> str:
    """ Return the CMD farewells. """
    return rf"""rem custom exit code summary:
    rem 0 (default) - display "press any key to continue. . ." message
    rem 900 - close cmd that runs .bat file
    rem 901 - remove folder that runs .bat file
    rem 902 - remove folder and close cmd that runs .bat file
    rem [903, 910] - reserved error status numbers
    rem [911 - 920] call python script and pass exit status

    if %errorlevel% equ 900 (
        exit
    ) else if %errorlevel% equ 901 (
        "{gv['IOBIT_UNLOCKER_PATH']}" "/Delete" "%~dp0"
        pause
    ) else if %errorlevel% equ 902 (
        "{gv['IOBIT_UNLOCKER_PATH']}" "/Delete" "%~dp0"
        exit
    ) else if %errorlevel% geq 911 (
        if %errorlevel% leq 920 (
            pause            
            "{gv['PYTHON_PATH']}" "{os.path.join(gv['FUNCTIONS_DIR_HOME'], 'local_cmd_farewell_handler.py')}" %errorlevel%
        )
    ) else (
    pause
    )"""

def exit_cmd_farewell():
    """ Exit python with a 900 exit status which closes the cmd that runs the batch process. """
    sys.exit(900)

def remove_directory_cmd_farewell(gv: dict):
    """ Exit python and remove the directory that contains the .bat script. """

    if os.getcwd().startswith(gv['JOBS_DIR_HOME']):
        sys.exit(901)
    else:
        raise ValueError(f'the working directory must be a subdirectory of {gv["JOBS_DIR_HOME"]} '
                         f'and the working directory is {os.getcwd()}')

def remove_directory_and_close_cmd_farewell(gv: dict):
    """ Exit python, remove the directory and close cmd that contains the .bat script. """

    if os.getcwd().lower().startswith(gv['JOBS_DIR_HOME'].lower()):
        sys.exit(902)
    else:
        raise ValueError(f'the working directory must be a subdirectory of {gv["JOBS_DIR_HOME"]} '
                         f'and the working directory is {os.getcwd()}')

def goto_wachtrij_and_close_cmd_farewell():
    """ Change directory to the WACHTRIJ main folder and close cmd that contains the .bat script."""
    sys.exit(903)

def open_wachtrij_folder_cmd_farewell():
    """ Exit python with a 911 exit status which open the WACHTRIJ folder. """
    sys.exit(911)

def open_gesliced_folder_cmd_farewell():
    """ Exit python with a 912 exit status which open the GESLICED folder. """
    sys.exit(912)