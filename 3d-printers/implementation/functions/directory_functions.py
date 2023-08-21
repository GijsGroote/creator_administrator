"""
Functionality for moving/copying or searching in directories.
"""

import os
import shutil
from typing import List

from global_variables import PRINT_DIR_HOME
from conversion_functions import (
    job_folder_name_to_date,
    gcode_files_to_max_print_time)

def get_print_job_global_paths(search_in_main_folder=None) -> List[str]:
    """
    TODO: this docstring

    return global path for all print jobs
    """

    print_job_global_paths = []

    if search_in_main_folder is None:
        main_folders = os.listdir(PRINT_DIR_HOME)
    else:
        main_folders = [search_in_main_folder]

    for main_folder in main_folders:
        temp_print_job_global_paths = [os.path.join(PRINT_DIR_HOME, main_folder, job_folder_name)
                                       for job_folder_name in os.listdir(os.path.join(PRINT_DIR_HOME, main_folder))]

        if len(temp_print_job_global_paths) > 0:
            print_job_global_paths.extend(temp_print_job_global_paths)

    return print_job_global_paths


def get_print_job_folder_names(search_in_main_folder=None) -> List[str]:
    """ return all print job names """

    print_job_names = []

    if search_in_main_folder is None:
        main_folders = os.listdir(PRINT_DIR_HOME)
    else:
        main_folders = [search_in_main_folder]

    for main_folder in main_folders:
        temp_print_job_names = [print_job_name for print_job_name in
                                os.listdir(os.path.join(PRINT_DIR_HOME, main_folder))]

        if len(temp_print_job_names) > 0:
            print_job_names.extend(temp_print_job_names)

    return print_job_names


def job_name_to_global_path(job_name: str, search_in_main_folder=None) -> str:
    """ return global path of print job """

    # TODO: job A_B is creatd, A_B_(1) is created,  A_B is removed. Using this function
    # the job called A_B will return job A_B_(1), which IS A DIFFERENT JOB
    # edit this function so that it raises a valueError('no job found')
    # when A_B is searched but only A_B_(1) is present

    for print_job_global_path in get_print_job_global_paths(search_in_main_folder):
        if job_name in print_job_global_path:
            return print_job_global_path

    raise ValueError(f"no print job path found for print job with name {job_name}")


def job_name_to_job_folder_name(job_name: str, search_in_main_folder=None) -> str:
    """ get the job folder name from a job name """

    for print_job_folder_name in get_print_job_folder_names(search_in_main_folder):
        if job_name in print_job_folder_name:
            return print_job_folder_name

    raise ValueError(f'could not find job folder name for job name: {job_name}')


def does_job_exist_in_main_folder(job_name: str, main_folder: str) -> bool:
    """ check if a job exists in a main folder """
    for print_job_folder_name in get_print_job_folder_names(main_folder):
        if job_name in print_job_folder_name:
            return True
    return False


def get_new_job_folder_name(job_name: str, source_dir_global_path: str, target_main_folder: str) -> str:
    """ get a job folder name for a print job moved to a main folder """

    job_folder_name = job_name_to_job_folder_name(job_name)

    if target_main_folder in ['AFGEKEURD', 'WACHTRIJ', 'VERWERKT']:
        return job_folder_name

    elif target_main_folder == 'GESLICED':

        date = job_folder_name_to_date(job_folder_name)

        gcode_files = [file for file in os.listdir(source_dir_global_path) if file.lower().endswith(".gcode")]

        assert len(gcode_files) > 0, \
            f'no .gcode found in print job: {job_name}, slice .stl first'

        max_print_time = gcode_files_to_max_print_time(gcode_files)

        return date + max_print_time + job_name

    elif target_main_folder == 'AAN_HET_PRINTEN':
        return job_folder_name

    else:
        raise ValueError(f'{target_main_folder} is not a main folder')


def move_directory_recursive(source_dir_global: str, target_dir_global: str):
    """ move directory and subdirectories recursively """
    try:
        shutil.move(source_dir_global, target_dir_global)
    except Exception as e:
        print(f"An error occurred: {e}")


def copy_directory_recursive(source_dir_global: str, target_dir_global: str):
    """ copy directory and subdirectories recursively """
    try:
        shutil.copy(source_dir_global, target_dir_global)
    except Exception as e:
        print(f"An error occurred: {e}")


def copy_print_job(job_name: str, target_main_folder: str, source_main_folder=None):
    """ move print job to target_main_folder """
    # TODO: this function is to long and does to much, split this function into multiple

    assert target_main_folder in ["AFGEKEURD", "WACHTRIJ", "GESLICED", "AAN_HET_PRINTEN", "VERWERKT"], \
        f"folder {target_main_folder} is not a main folder"
    assert source_main_folder in [None, "AFGEKEURD", "WACHTRIJ", "GESLICED", "AAN_HET_PRINTEN", "VERWERKT"], \
        f"folder {target_main_folder} is not a main folder or None"

    # find source directory
    source_dir_global_path = job_name_to_global_path(job_name, source_main_folder)

    if (target_main_folder == 'AAN_HET_PRINTEN' and
            does_job_exist_in_main_folder(job_name, 'AAN_HET_PRINTEN')):
        target_dir_global_path = job_name_to_global_path(
            job_name, search_in_main_folder='AAN_HET_PRINTEN')
    else:
        # make target directory
        target_dir_global_path = os.path.join(
            PRINT_DIR_HOME,
            target_main_folder,
            get_new_job_folder_name(
                job_name,
                source_dir_global_path,
                target_main_folder))

        assert target_dir_global_path != source_dir_global_path, \
            'the source directory is equal to the target directory'
        os.mkdir(target_dir_global_path)

    # move items from source to target directory
    for item in os.listdir(source_dir_global_path):
        source_item = os.path.join(source_dir_global_path, item)
        target_item = os.path.join(target_dir_global_path, item)

        if os.path.isdir(source_item):
            copy_directory_recursive(source_item, target_dir_global_path)
        else:
            # TODO: you will get problems moving because op files (especially .stl) which are still open
            shutil.copy(source_item, target_item)


def move_print_job_partly(job_name: str, exclude_files: List):
    """ partly move, partly copy print job from GESLICED to AAN_HET_PRINTEN folder """

    # find source directory
    source_dir_global_path = job_name_to_global_path(job_name, 'GESLICED')

    if does_job_exist_in_main_folder(job_name, 'AAN_HET_PRINTEN'):
        target_dir_global_path = job_name_to_global_path(
            job_name, search_in_main_folder='AAN_HET_PRINTEN')
    else:
        date = job_folder_name_to_date(
            job_name_to_job_folder_name(job_name))

        printing_gcode_files = [file for file in os.listdir(source_dir_global_path)
                                if (file.lower().endswith(".gcode") and
                                    file not in exclude_files)]

        max_print_time = gcode_files_to_max_print_time(printing_gcode_files)
        new_job_folder_name = date + max_print_time + job_name

        target_dir_global_path = os.path.join(
            PRINT_DIR_HOME,
            'AAN_HET_PRINTEN',
            new_job_folder_name)
        os.mkdir(target_dir_global_path)

    # partly move some files to target
    # move items from source to target directory
    for item in os.listdir(source_dir_global_path):
        if item.lower().endswith('.gcode'):
            if item in exclude_files:
                print(f'not moveing {item}')
                # pass
            else:
                print(f'moveing {item}')
                shutil.move(
                    os.path.join(source_dir_global_path, item),
                    os.path.join(target_dir_global_path, item))
        else:
            source_item = os.path.join(source_dir_global_path, item)
            target_item = os.path.join(target_dir_global_path, item)

            if os.path.isdir(source_item):
                copy_directory_recursive(source_item, target_dir_global_path)
            else:
                # TODO: you will get problems moving because op files (especially .stl) which are still open
                shutil.copy(source_item, target_item)

        # update name of the source_dir_global_path


