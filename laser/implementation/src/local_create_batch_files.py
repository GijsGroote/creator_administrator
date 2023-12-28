"""
Convert python code to clickable batch functions.
"""

import os

from global_variables import gv
from create_batch_file import python_to_batch_in_folder


if __name__ == "__main__":

    batch_files_folder = os.path.join(gv['FUNCTIONS_DIR_HOME'], '../batch_files')
    
    # create inbox.bat
    python_to_batch_in_folder(gv, os.path.join(gv['FUNCTIONS_DIR_HOME'], 'inbox.py'), batch_files_folder)

    # create select_bestand.bat
    python_to_batch_in_folder(gv, os.path.join(gv['FUNCTIONS_DIR_HOME'], 'select_file.py'), batch_files_folder)

    # create checkhealth.bat
    python_to_batch_in_folder(gv, os.path.join(gv['FUNCTIONS_DIR_HOME'], 'check_health.py'), batch_files_folder)
