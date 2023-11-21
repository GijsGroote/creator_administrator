"""
Specify behavior when cmd is closing, the cmd saying farewell.

Communication from the python process to the cmd is through a exist status.
"""

import sys
import os
from global_variables import gv
from src.cmd_farewell_handler import (
    exit_cmd_farewell,
    remove_directory_cmd_farewell,
    remove_directory_and_close_cmd_farewell,
    goto_wachtrij_and_close_cmd_farewell,
    open_wachtrij_folder_cmd_farewell,
    open_gesliced_folder_cmd_farewell
    )

def open_gesliced_folder_cmd_farewell():
    """ Exit python with a 912 exit status which open the GESLICED folder. """
    sys.exit(912)

if __name__ == '__main__':

    error_level = int(sys.argv[1])

    if error_level == 911:
        os.startfile(os.path.join(gv['JOBS_DIR_HOME'], 'WACHTRIJ'))
    elif error_level == 912:
        os.startfile(os.path.join(gv['JOBS_DIR_HOME'], 'GESLICED'))
    else:
        input(f'No behavior defined for exit status {error_level}')
