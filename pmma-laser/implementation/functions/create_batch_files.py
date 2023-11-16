"""
Convert python code to clickable batch functions.
"""

import os

from global_variables import FUNCTIONS_DIR_HOME
from batch import python_to_batch


if __name__ == "__main__":

    # create inbox.bat
    python_to_batch(os.path.join(FUNCTIONS_DIR_HOME, 'inbox.py'))

    # create select_bestand.bat
    python_to_batch(os.path.join(FUNCTIONS_DIR_HOME, 'select_file.py'))

    # create checkhealth.bat
    python_to_batch(os.path.join(FUNCTIONS_DIR_HOME, 'check_health.py'))
