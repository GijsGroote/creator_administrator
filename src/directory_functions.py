"""
Functionality for moving/copying or searching in directories.
"""

import os
import re
import shutil
from typing import List

from src.convert_functions import (
    job_folder_name_to_date)

def does_job_name_exist(job_name: str) -> bool:
    """ Check if the job name exist, return boolean. """

    for folder_name in get_job_folder_names():
        if folder_name.endswith(job_name):
            return True

    return False

def make_job_name_unique(job_name: str) -> str:
    """ Make the job name unique.

    if the job name already exists append _(NUMBER) to job name to make it unique
    if the job_name is unique but job_name_(NUMBER) exist then return job_name_(NUMBER+1).
    """

    max_job_number = 0
    for folder_name in get_job_folder_names():

        match_job_number= re.search(rf'.*{job_name}_\((\d+)\)$', folder_name)

        if match_job_number:

            job_number = int(match_job_number.group(1))
            if job_number > max_job_number:
                max_job_number = job_number

    if max_job_number == 0:
        if does_job_name_exist(job_name):
            return job_name + '_(1)'
        return job_name
    return job_name + '_(' + str(max_job_number + 1) + ')'

def get_job_global_paths(gv: dict, search_in_main_folder=None) -> List[str]:
    """ Return global paths for all jobs. """

    job_global_paths = []

    if search_in_main_folder is None:
        main_folders = os.listdir(gv['JOBS_DIR_HOME'])
    else:
        main_folders = [search_in_main_folder]

    for main_folder in main_folders:
        temp_job_global_paths = [os.path.join(gv['JOBS_DIR_HOME'], main_folder, job_folder_name)
                   for job_folder_name in os.listdir(os.path.join(gv['JOBS_DIR_HOME'], main_folder))]

        if len(temp_job_global_paths) > 0:
            job_global_paths.extend(temp_job_global_paths)

    return job_global_paths

def get_job_folder_names(gv: dict, search_in_main_folder=None) -> List[str]:
    """ Return all folder names corresponding to a job name.  """

    job_names = []

    if search_in_main_folder is None:
        main_folders = os.listdir(gv['JOBS_DIR_HOME'])
    else:
        main_folders = [search_in_main_folder]

    for main_folder in main_folders:
        temp_job_names = list(os.listdir(os.path.join(gv['JOBS_DIR_HOME'], main_folder)))

        if len(temp_job_names) > 0:
            job_names.extend(temp_job_names)

    return job_names

def job_name_to_global_path(job_name: str, search_in_main_folder=None) -> str:
    """ Return global path of job. """

    for job_global_path in get_job_global_paths(search_in_main_folder):
        if job_global_path.endswith(job_name):
            return job_global_path

    raise ValueError(f"no job path found for job with name {job_name}")

def job_name_to_job_folder_name(job_name: str, search_in_main_folder=None) -> str:
    """ Get the job folder name from a job name. """

    for job_folder_name in get_job_folder_names(search_in_main_folder):
        if job_name in job_folder_name:
            return job_folder_name

    raise ValueError(f'could not find job folder name for job name: {job_name}')

def does_job_exist_in_main_folder(job_name: str, main_folder: str) -> bool:
    """ Check if a job exists in a main folder. """
    for job_folder_name in get_job_folder_names(main_folder):
        if job_name in job_folder_name:
            return True
    return False

def get_new_job_folder_name(job_name: str, source_dir_global_path: str,
                            target_main_folder: str) -> str:
    """ Get a job folder name for a job moved to a main folder. """

    job_folder_name = job_name_to_job_folder_name(job_name)

    if target_main_folder in ['AFGEKEURD', 'WACHTRIJ', 'VERWERKT']:
        return job_folder_name

    if target_main_folder == 'GESLICED':

        date = job_folder_name_to_date(job_folder_name)

        gcode_files = [file for file in os.listdir(source_dir_global_path) if file.lower().endswith(".gcode")]

        assert len(gcode_files) > 0, \
            f'no .gcode found in job: {job_name}, slice .stl first'

        max_time = gcode_files_to_max_time(gcode_files)

        return date + max_time + job_name

    if target_main_folder == 'AAN_HET_PRINTEN':
        return job_folder_name

    raise ValueError(f'{target_main_folder} is not a main folder')


def move(source_dir_global: str, target_dir_global: str):
    """ Move directory and subdirectories recursively. """

    if os.path.isdir(source_dir_global):
        for file_or_folder in os.listdir(source_dir_global):
            move(os.path.join(source_dir_global, file_or_folder), target_dir_global)
    else:
        try:
            shutil.move(source_dir_global, target_dir_global)
        except Exception as e:
            print(f"An error occurred: {e}")

def copy(source_dir_global: str, target_dir_global: str):
    """ Copy directory and subdirectories recursively. """

    if os.path.isdir(source_dir_global):
        for file_or_folder in os.listdir(source_dir_global):
            copy(os.path.join(source_dir_global, file_or_folder), target_dir_global)
    else:
        try:
            shutil.copy(source_dir_global, target_dir_global)
        except Exception as e:
            print(f"An error occurred: {e}")

# TODO: this should be an abstracted function from the files and functions
def file_should_be_skipped(source_file_global_path: str,
                           target_file_global_path: str) -> bool:
    """ Return boolean indicating if the file should be skipped when moving to the target folder."""

    if target_file_global_path.startswith(os.path.join(JOBS_DIR_HOME, 'AFGEKEURD')) and \
            (source_file_global_path.endswith('afgekeurd.bat') and
             target_file_global_path.endswith('afgekeurd.bat')) or \
            (source_file_global_path.endswith('gesliced.bat') and
             target_file_global_path.endswith('gesliced.bat')):
        return True

    elif source_file_global_path.startswith(os.path.join(JOBS_DIR_HOME, 'WACHTRIJ')) and \
            target_file_global_path.startswith(os.path.join(JOBS_DIR_HOME, 'GESLICED')) and \
            source_file_global_path.endswith('gesliced.bat') and \
            target_file_global_path.endswith('gesliced.bat'):
        return True

    elif source_file_global_path.startswith(os.path.join(JOBS_DIR_HOME, 'GESLICED')) and \
            target_file_global_path.startswith(os.path.join(JOBS_DIR_HOME, 'AAN_HET_PRINTEN')) and \
            source_file_global_path.endswith('laserer_aangezet.bat') and \
            target_file_global_path.endswith('laserer_aangezet.bat'):
        return True

    elif source_file_global_path.startswith(os.path.join(JOBS_DIR_HOME, 'AAN_HET_PRINTEN')) and \
            target_file_global_path.startswith(os.path.join(JOBS_DIR_HOME, 'VERWERKT')) and \
            ((source_file_global_path.endswith('laserer_klaar.bat') :
        return True

    elif source_file_global_path.startswith(os.path.join(JOBS_DIR_HOME, 'WACHTRIJ')) and \
            target_file_global_path.startswith(os.path.join(JOBS_DIR_HOME, 'GESLICED')) and \
            source_file_global_path.endswith('gesliced.bat') and \
            target_file_global_path.endswith('gesliced.bat'):
        return True

    elif source_file_global_path.startswith(os.path.join(JOBS_DIR_HOME, 'GESLICED')) and \
            target_file_global_path.startswith(os.path.join(JOBS_DIR_HOME, 'AAN_HET_PRINTEN')) and \
            source_file_global_path.endswith('laserer_aangezet.bat') and \
            target_file_global_path.endswith('laserer_aangezet.bat'):
        return True

    elif source_file_global_path.startswith(os.path.join(JOBS_DIR_HOME, 'AAN_HET_PRINTEN')) and \
            target_file_global_path.startswith(os.path.join(JOBS_DIR_HOME, 'VERWERKT')) and \
            ((source_file_global_path.endswith('laserer_klaar.bat') and
              target_file_global_path.endswith('laserer_klaar.bat')) or
             (source_file_global_path.endswith('afgekeurd.bat') and
and
              target_file_global_path.endswith('laserer_klaar.bat')) or
             (source_file_global_path.endswith('afgekeurd.bat') and
              target_file_global_path.endswith('afgekeurd.bat'))):
        return True
    else:
        return False

def rename_target_item(job_name: str, target_item: str) -> str:
    """ Rename the target item. """

    if target_item.lower().endswith('.gcode') and \
            'GESLICED' in target_item:

        dir_path, filename = os.path.split(target_item)

        return os.path.join(dir_path, job_name + '_' + filename)
    else:
        return target_item

def copy_job(job_name: str, target_main_folder: str, source_main_folder=None):
    """ Move laser job to target_main_folder. """

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
            JOBS_DIR_HOME,
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
            copy(source_item, target_dir_global_path)
        else:
            if file_should_be_skipped(source_item, target_item):
                continue
            target_item = rename_target_item(job_name, target_item)
            copy(source_item, target_item)


def move_job_partly(gv: dict, job_name: str, exclude_files: List):
    """ Partly move, partly copy job from GESLICED to AAN_HET_PRINTEN folder. """

    # find source directory
    source_dir_global_path = job_name_to_global_path(job_name, 'GESLICED')

    if does_job_exist_in_main_folder(job_name, 'AAN_HET_PRINTEN'):
        target_dir_global_path = job_name_to_global_path(
            job_name, search_in_main_folder='AAN_HET_PRINTEN')
    else:
        date = job_folder_name_to_date(
            job_name_to_job_folder_name(job_name))

        new_job_folder_name = date + job_name

        target_dir_global_path = os.path.join(
            gv['JOBS_DIR_HOME'],
            'AAN_HET_PRINTEN',
            new_job_folder_name)
        os.mkdir(target_dir_global_path)

    # partly move some files to target
    # move items from source to target directory
    for item in os.listdir(source_dir_global_path):
        source_item = os.path.join(source_dir_global_path, item)
        target_item = os.path.join(target_dir_global_path, item)

        if item.lower().endswith('.gcode'):
            if item in exclude_files:
                continue
            move(source_item, target_item)
            continue

        if os.path.isdir(source_item):
            copy(source_item, target_dir_global_path)
        if file_should_be_skipped(source_item, target_item):
            continue
        copy(source_item, target_item)

def get_jobs_in_queue(gv: dict) -> int:
    """ return the laser jobs in the main folder WACHTRIJ. """

    n_dirs_in_wachtrij = len([job_folder_name for job_folder_name in
                              os.listdir(os.path.join(gv['JOBS_DIR_HOME'], 'WACHTRIJ'))
                              if os.path.isdir(os.path.join(
                                  gv['JOBS_DIR_HOME'], 'WACHTRIJ', job_folder_name))])

    return n_dirs_in_wachtrij

def folder_contains_3d_file(gv: dict, global_path: str) -> bool:
    """ Check if a folder contains at least one 3D laser file. """

    # Iterate through the files and check if any of them have a valid 3D laser extension
    if any(file.endswith(gv['ACCEPTED_EXTENSIONS']) for file in os.listdir(global_path)):
        return True
    return False
