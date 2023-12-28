"""
Convert python code to clickable batch functions.
"""

import os
# from directory_functions import job_name_to_global_path

def python_to_batch(gv: dict, python_path: str, job_name: str, search_in_main_folder=None):
    """ Convert a python file to an batch file. """
    # batch_file_target_folder = job_name_to_global_path(gv, job_name, search_in_main_folder)  
    
    assert os.path.exists(batch_file_target_folder),\
        f"path {batch_file_target_folder} does not exist."  

    with open(os.path.join(batch_file_target_folder, os.path.basename(python_path).replace('.py', '.bat')), 'w+') as bat_file:
        bat_file.write(rf"""@echo off

"{gv["PYTHON_PATH"]}" "{python_path}" "{job_name}"

{gv["CMD_FAREWELLS"]}""")
        
def python_to_batch_in_folder(gv: dict, python_path: str, batch_file_target_folder: str, pass_parameter=None):
    """ Convert a python file to an batch file and place in target directory. """
     
    assert os.path.exists(batch_file_target_folder),\
        f"path {batch_file_target_folder} does not exist."
    
    if pass_parameter is None:
        python_command = f'"{gv["PYTHON_PATH"]}" "{python_path}"'
    else:
        python_command = f'"{gv["PYTHON_PATH"]}" "{python_path}" "{pass_parameter}"'
        
    with open(os.path.join(batch_file_target_folder, os.path.basename(python_path).replace('.py', '.bat')), 'w+') as bat_file:
        bat_file.write(rf"""@echo off

{python_command}

{gv["CMD_FAREWELLS"]}""")
        
def create_batch_files_for_job_folder(gv: dict, job_name: str, main_folder: str):
    """ Create batch files for a job_folder in main_folder. """
    assert main_folder in gv['MAIN_FOLDERS'],\
        f'main folder {main_folder} should be in {gv["MAIN_FOLDERS"]}'

    for batch_file in gv['MAIN_FOLDERS'][main_folder]['allowed_batch_files']:
        python_file_global_path = os.path.join(gv['FUNCTIONS_DIR_HOME'], batch_file.replace('.bat', '.py')) 
        python_to_batch(gv, python_file_global_path, job_name, main_folder)
