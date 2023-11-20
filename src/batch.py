"""
Convert python code to clickable batch functions.
"""

import os
from src.cmd_farewell_handler import get_cmd_farewells
from src.directory_functions import job_name_to_global_path

def python_to_batch(gv: dict, python_path: str, job_name=None, search_in_main_folder=None):
    """ Convert a python file to an batch file. """

    if job_name is not None:
        batch_file_target_folder = job_name_to_global_path(gv, job_name, search_in_main_folder)
        python_command = f'"{gv["PYTHON_PATH"]}" "{python_path}" "{job_name}"'
    else:
        batch_file_target_folder = os.path.join(gv['FUNCTIONS_DIR_HOME'], '../batch_files')  
        python_command = f'"{gv["PYTHON_PATH"]}" "{python_path}"'
    
    assert os.path.exists(batch_file_target_folder),\
        f"path {batch_file_target_folder} does not exist."  

    with open(os.path.join(batch_file_target_folder, os.path.basename(python_path).replace('.py', '.bat')), 'w+') as bat_file:
        bat_file.write(rf"""@echo off

{python_command}

{get_cmd_farewells(gv)}""")
        
def create_batch_files_for_job_folder(gv: dict, job_name: str, main_folder: str):
    """ Create batch files for a job_folder in main_folder. """
    assert main_folder in gv['MAIN_FOLDERS'],\
        f'main folder {main_folder} should be in {gv["MAIN_FOLDERS"]}'

    for batch_file in gv['MAIN_FOLDERS'][main_folder]['allowed_batch_files']:
        python_file_global_path = os.path.join(gv['FUNCTIONS_DIR_HOME'], batch_file.replace('.bat', '.py')) 
        python_to_batch(gv, python_file_global_path, job_name, main_folder)