"""
Functionality for moving/copying or searching in directories
specifically for the pmma-laser.
"""

import os
import shutil

from global_variables import gv
from local_convert_functions import gcode_files_to_max_print_time
from job_tracker import JobTracker

from src.directory_functions import (
    job_name_to_global_path,
    create_new_job_folder,
    job_name_to_job_folder_name,
    copy_job_files,
    does_job_exist_in_main_folder,
    copy,
    move)
from src.convert_functions import job_folder_name_to_date
from src.batch import create_batch_files_for_job_folder

def move_job_to_main_folder(job_name: str, target_main_folder: str, source_main_folder=None):
    """ Moves a job to another main folder.
        this function:
         - skips unwanted batch files
         - may rename the folder name and file names
         - removes the source_job_folder
         - stops the python thread.
    """
    # update the job tracker
    # JobTracker().update_job_main_folder(job_name, target_main_folder)

    
    # find source directory
    source_job_folder_global_path = job_name_to_global_path(gv, job_name, source_main_folder)

    # create the target folder
    if (target_main_folder == 'AAN_HET_PRINTEN' and
            does_job_exist_in_main_folder(gv, job_name, 'AAN_HET_PRINTEN')):
        target_job_folder_global_path = job_name_to_global_path(gv, 
            job_name, search_in_main_folder='AAN_HET_PRINTEN')
    else:      
         new_job_folder_name = get_new_job_folder_name(job_name, source_job_folder_global_path, target_main_folder)
         target_job_folder_global_path = create_new_job_folder(
            gv, job_name, new_job_folder_name, target_main_folder, source_main_folder)

    # create new batch files
    create_batch_files_for_job_folder(gv, job_name, target_main_folder)

    # copy files    
    copy_gcode_files(job_name, target_job_folder_global_path, source_job_folder_global_path)
    copy_job_files(target_job_folder_global_path, source_job_folder_global_path, ['.bat', '.gcode'])

def move_print_job_partly(job_name: str, exclude_files: list):
    """ Partly move, partly copy print job from GESLICED to AAN_HET_PRINTEN folder. """

    job_tracker = JobTracker()
    job_tracker.update_job_main_folder(job_name, 'AAN_HET_PRINTEN')
    job_tracker.set_split_job_to(job_name, True)

    # find source directory
    source_job_folder_global_path = job_name_to_global_path(gv, job_name, 'GESLICED')

    if does_job_exist_in_main_folder(gv, job_name, 'AAN_HET_PRINTEN'):
        target_job_folder_global_path = job_name_to_global_path(gv,
            job_name, search_in_main_folder='AAN_HET_PRINTEN')
    else:
        date = job_folder_name_to_date(job_name_to_job_folder_name(gv, job_name))

        new_job_folder_name = date + job_name

        target_job_folder_global_path = create_new_job_folder(
            gv, job_name, new_job_folder_name, 'AAN_HET_PRINTEN', 'GESLICED')
        

    # partly move some files to target
    # move items from source to target directory
    for item in os.listdir(source_job_folder_global_path):
        source_item = os.path.join(source_job_folder_global_path, item)
        target_item = os.path.join(target_job_folder_global_path, item)

        if item.lower().endswith('.bat'):
            continue

        if item.lower().endswith('.gcode'):
            if item in exclude_files:
                print(f'hey we should exluce {item}')
                continue
            shutil.move(source_item, target_item)
            continue

        shutil.copy(source_item, target_item)

    # create new batch files
    create_batch_files_for_job_folder(gv, target_job_folder_global_path, 'AAN_HET_PRINTEN')


def get_new_job_folder_name(job_name: str, source_dir_global_path: str,
                            target_main_folder: str) -> str:
    """ Get a job folder name for a print job moved to a main folder. """

    job_folder_name = job_name_to_job_folder_name(gv, job_name)

    if target_main_folder in ['AFGEKEURD', 'WACHTRIJ', 'VERWERKT']:
        return job_folder_name

    if target_main_folder == 'GESLICED':

        date = job_folder_name_to_date(job_folder_name)

        gcode_files = [file for file in os.listdir(source_dir_global_path) if file.lower().endswith(".gcode")]

        assert len(gcode_files) > 0, \
            f'no .gcode found in print job: {job_name}, slice .stl first'

        max_print_time = gcode_files_to_max_print_time(gcode_files)

        return date + max_print_time + job_name

    if target_main_folder == 'AAN_HET_PRINTEN':
        return job_folder_name

    raise ValueError(f'{target_main_folder} is not a main folder')


def copy_gcode_files(job_name: str, target_job_folder_global_path, source_job_folder_global_path: str):
    """ Move gcode, rename if moving to GESLICED main folder. """

    for item in os.listdir(source_job_folder_global_path):
        if item.lower().endswith('.gcode'):
        
            source_item = os.path.join(source_job_folder_global_path, item)

            if 'GESLICED' in target_job_folder_global_path:
                _, filename = os.path.split(item)
                target_item = os.path.join(target_job_folder_global_path, job_name + '_' + filename)
            else:
                target_item = os.path.join(target_job_folder_global_path, item)

            copy(source_item, target_item)