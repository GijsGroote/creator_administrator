"""
Functionality for moving/copying or searching in directories
specifically for the pmma-laser.
"""

import os
import shutil

from global_variables import gv
from pmma_talk_to_ta import enter_material_thickness_amount

from src.directory_functions import (
    job_name_to_global_path,
    create_new_job_folder,
    job_name_to_job_folder_name,
    copy_job_files)
from src.talk_to_sa import yes_or_no
from src.directory_functions import read_json_file, write_json_file
from src.create_batch_file import create_batch_files_for_job_folder
from src.cmd_farewell_handler import remove_directory_and_close_cmd_farewell


def move_job_to_main_folder(job_name: str, target_main_folder: str):
    """ Moves a job to another main folder.
        this function:
         - skips unwanted batch files
         - may rename the folder name and file names
         - removes the source_job_folder
         - stops the python thread
    """

    # find source directory
    source_job_folder_global_path = job_name_to_global_path(gv, job_name, "WACHTRIJ")

    # create the target folder
    new_job_folder_name = job_name_to_job_folder_name(gv, job_name, "WACHTRIJ")
    target_job_folder_global_path = create_new_job_folder(
            gv, job_name, new_job_folder_name, target_main_folder, "WACHTRIJ")

    # create new batch files
    create_batch_files_for_job_folder(gv, target_job_folder_global_path, target_main_folder)

    # copy files
    copy_job_files(target_job_folder_global_path, source_job_folder_global_path, ['.bat'])

    # delete old job_folder and stop python thread
    remove_directory_and_close_cmd_farewell(gv)

def create_files_dict(job_name: str) -> dict:
    """ Return a dictionary with laser files info from file system. """
    files_dict = {}

    for file in os.listdir(job_name_to_global_path(gv, job_name)):
        if file.endswith(gv['ACCEPTED_EXTENSIONS']):

            file_name = os.path.basename(file)

            while True:
                material, thickness, amount = enter_material_thickness_amount(file_name)
        
                if yes_or_no(f'File {file_name}: \n   material: {material}'\
                                    f'\n   thickness: {thickness}\n   amount: {amount}\n'\
                                    'is this correct (Y/n)?\n'):
                    break
                else:
                    continue
                
            files_dict[job_name + '_' + file_name] = {
                            'file_name': file_name,
                            'file_global_path': file,
                            'material': material,
                            'thickness': thickness,
                            'amount': amount,
                            'done': False}
    
    return files_dict

