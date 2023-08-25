"""
Convert python code to clickable batch functions.
"""

import os

from global_variables import (
    PYTHON_PATH,
    FUNCTIONS_DIR_HOME)
from cmd_farewell_handler import cmd_farewells
from directory_functions import job_name_to_global_path

def python_to_batch(python_path: str, job_name=None):
    """ Convert a python file to an batch file. """

    assert os.path.isfile(python_path), f"file {python_path} does not exist."

    if job_name is not None:
        batch_file_global_path = job_name_to_global_path(job_name)
        assert os.path.exists(batch_file_global_path), f"path {batch_file_global_path} does not exist."
        python_command = f'"{PYTHON_PATH}" "{python_path}" "{job_name}"'
    else:
        batch_file_global_path = os.path.join(FUNCTIONS_DIR_HOME, '../batch_files')
        assert os.path.exists(batch_file_global_path), f"path {batch_file_global_path} does not exist."
        python_command = f'"{PYTHON_PATH}" "{python_path}"'


    function_name = os.path.splitext(os.path.basename(python_path))[0]

    bat_file = open(os.path.join(batch_file_global_path, f'{function_name}.bat'), 'w+')
    bat_file.write(rf"""@echo off
    
{python_command}

{cmd_farewells}""")

    bat_file.close()

if __name__ == "__main__":

    # create inbox.bat
    python_to_batch(os.path.join(FUNCTIONS_DIR_HOME, 'inbox.py'))

    # create select_bestand.bat
    python_to_batch(os.path.join(FUNCTIONS_DIR_HOME, 'select_bestand.py'))
