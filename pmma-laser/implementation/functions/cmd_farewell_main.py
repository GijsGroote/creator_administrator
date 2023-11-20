""" The main functions for cmd_farewell_handler. """

import sys
import os
from global_variables import gv

if __name__ == '__main__':

    error_level = int(sys.argv[1])

    if error_level == 911:
        os.startfile(os.path.join(gv['JOBS_DIR_HOME'], 'WACHTRIJ'))
    else:
        input(f'No behavior defined for exit status {error_level}')
