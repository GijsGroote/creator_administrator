"""
Specify behavior when cmd is closing, the cmd saying farewell.

Communication from the python process to the cmd is through a exist status.
"""

import sys
import os

from global_variables import gv

if __name__ == '__main__':

    error_level = int(sys.argv[1])

    if error_level == 911:
        os.startfile(os.path.join(gv['JOBS_DIR_HOME'], 'WACHTRIJ'))
    elif error_level == 912:
        os.startfile(os.path.join(gv['JOBS_DIR_HOME'], 'GESLICED'))
    else:
        input(f'No behavior defined for exit status {error_level}')
