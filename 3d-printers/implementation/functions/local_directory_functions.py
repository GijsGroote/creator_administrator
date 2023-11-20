"""
Functionality for moving/copying or searching in directories
specifically for the pmma-laser.
"""

import os

from global_variables import gv
from job_tracker import JobTracker

from src.directory_functions import (
    job_name_to_global_path,
    create_new_job_folder,
    job_name_to_job_folder_name,
    copy_job_files,
    job_folder_name_to_date,
    does_job_exist_in_main_folder,
    copy,
    move
    )
from src.batch import create_batch_files_for_job_folder
from src.cmd_farewell_handler import remove_directory_and_close_cmd_farewell

def move_job_to_main_folder(job_name: str, target_main_folder: str):
    """ Moves a job to another main folder.
        this function:
         - skips unwanted batch files
         - may rename the folder name and file names
         - removes the source_job_folder
         - stops the python thread.
    """
    # update the job tracker
    JobTracker().update_job_main_folder(job_name, target_main_folder)

    # find source directory
    source_job_folder_global_path = job_name_to_global_path(gv, job_name, 'WACHTRIJ')

    # create the target folder
    new_job_folder_name = job_name_to_job_folder_name(gv, job_name, 'WACHTRIJ')
    target_job_folder_global_path = create_new_job_folder(
            gv, job_name, new_job_folder_name, target_main_folder, 'WACHTRIJ')


    # create new batch files
    create_batch_files_for_job_folder(gv, target_job_folder_global_path, target_main_folder)

    # copy files
    copy_job_files(target_job_folder_global_path, source_job_folder_global_path, ['.bat'])

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
        date = job_folder_name_to_date(gv,
            job_name_to_job_folder_name(job_name))

        new_job_folder_name = date + job_name

        target_job_folder_global_path = os.path.join(
            gv['JOBS_DIR_HOME'],
            'AAN_HET_PRINTEN',
            new_job_folder_name)
        os.mkdir(target_job_folder_global_path)

    # partly move some files to target
    # move items from source to target directory
    for item in os.listdir(source_job_folder_global_path):
        source_item = os.path.join(source_job_folder_global_path, item)
        target_item = os.path.join(target_job_folder_global_path, item)

        if item.lower.endswith('.bat'):
            continue

        if item.lower().endswith('.gcode'):
            if item in exclude_files:
                continue
            move(source_item, target_item)
            continue

        if os.path.isdir(source_item):
            copy(source_item, target_job_folder_global_path)

        copy(source_item, target_item)

    # create new batch files
    create_batch_files_for_job_folder(gv, target_job_folder_global_path, 'AAN_HET_PRINTEN')
