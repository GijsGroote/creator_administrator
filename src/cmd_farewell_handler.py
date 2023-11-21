"""
Specify behavior when cmd is closing, the cmd saying farewell.

Communication from the python process to the cmd is through a exist status.
"""

import sys
import os

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
        raise ValueError(f'the working directory must be a subdirectory of {gv['JOBS_DIR_HOME']} '
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