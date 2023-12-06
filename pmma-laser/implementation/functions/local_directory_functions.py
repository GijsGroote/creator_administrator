"""
Functionality for moving/copying or searching in directories
specifically for the pmma-laser.
"""

import os
import shutil

from global_variables import gv

from src.directory_functions import (
    job_name_to_global_path,
    create_new_job_folder,
    job_name_to_job_folder_name,
    copy_job_files)
from src.directory_functions import read_json_file, write_json_file
from src.create_batch_file import create_batch_files_for_job_folder
from src.cmd_farewell_handler import remove_directory_and_close_cmd_farewell

def remove_files_from_wachtrij_materials(laser_job_log_global_path: str):
    """ Remove laser file from WACHTRIJ_MATERIAAL. """

    laser_job_dict = read_json_file(laser_job_log_global_path)

    for key, laser_file_dict in laser_job_dict.items():
            
        # remove the file
        os.remove(laser_file_dict['path_to_file_in_material_folder'])

        # update the materials_log
        material_log_global_path = os.path.join(
            os.path.dirname(laser_file_dict['path_to_file_in_material_folder']), 'materiaal_log.json')
        material_log_dict = read_json_file(material_log_global_path)

        material_log_dict.pop(key)

        if len(material_log_dict) == 0:
            shutil.rmtree(os.path.dirname(material_log_global_path))
        else:
            write_json_file(material_log_dict, material_log_global_path)


def move_job_to_main_folder(job_name: str, target_main_folder: str):
    """ Moves a job to another main folder.
        this function:
         - skips unwanted batch files
         - may rename the folder name and file names
         - removes the source_job_folder
         - stops the python thread
    """
    # update the job tracker
    # TODO: update job tracker

    # find source directory
    source_job_folder_global_path = job_name_to_global_path(gv, job_name, "WACHTRIJ")

    # create the target folder
    new_job_folder_name = job_name_to_job_folder_name(gv, job_name, "WACHTRIJ")
    target_job_folder_global_path = create_new_job_folder(
            gv, job_name, new_job_folder_name, target_main_folder, "WACHTRIJ")
    
    if target_main_folder in ['VERWERKT', 'AFGEURD']:
        remove_files_from_wachtrij_materials(os.path.join(source_job_folder_global_path, 'laser_job_log.json'))

    # create new batch files
    create_batch_files_for_job_folder(gv, target_job_folder_global_path, target_main_folder)

    # copy files
    copy_job_files(target_job_folder_global_path, source_job_folder_global_path, ['.bat'])


    # delete old job_folder and stop python thread
    remove_directory_and_close_cmd_farewell(gv)
