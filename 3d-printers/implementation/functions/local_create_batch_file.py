"""
Create the batch files.
"""

import os
from global_variables import gv
from src.batch import python_to_batch


if __name__ == '__main__':
     # create inbox.bat
    python_to_batch(gv, os.path.join(gv['FUNCTIONS_DIR_HOME'], 'inbox.py'))

    # create select_bestand.bat
    python_to_batch(gv, os.path.join(gv['FUNCTIONS_DIR_HOME'], 'select_file.py'))

    # create check_health.bat
    python_to_batch(gv, os.path.join(gv['FUNCTIONS_DIR_HOME'], 'check_health.py'))

