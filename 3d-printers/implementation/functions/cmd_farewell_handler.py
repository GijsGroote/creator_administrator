#! /usr/bin/env python3

import sys
import os
from global_variables import PRINT_DIR_HOME

"""
below this point cmd_farewell functions. That specify the behavior of the cmd prompt when
closing. communication from the python process to the cmd is through a custom exist code

custom exit code summary:
0 - (default) display "press any key to continue. . ." message
900 - close cmd that runs .bat file
901 - open the WACHTRIJ folder
902 - open the GESLICED folder

"""

def exit_cmd_farewell():
    """ exit python with a 900 exit status which closes the cmd that runs the batch process """
    sys.exit(900)




def open_wachtrij_folder_cmd_farewell():
    """ exit python with a 901 exit status which open the WACHTRIJ folder """
    sys.exit(901)

def open_gesliced_folder_cmd_farewell():
    """ exit python with a 901 exit status which open the GESLICED folder """
    sys.exit(902)

def remove_directory_cmd_farewell():
    """ exit python and remove the directory that holds the .bat script """
    sys.exit(1000)


if __name__ == '__main__':
    """ handle the cmd farewell based on the exit_status """

    exit_status = int(sys.argv[1])

    if exit_status == 901:
        os.startfile(os.path.join(PRINT_DIR_HOME, 'WACHTRIJ'))
    elif exit_status == 902:
        os.startfile(os.path.join(PRINT_DIR_HOME, 'GESLICED'))
    else:
        input(f'No behavior defined for exit status {exit_status}')
