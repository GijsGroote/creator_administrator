"""
Functionality for moving/copying or searching in directories.
"""

import os
import shutil
from typing import List

def create_new_job_folder(gv: dict, job_name, new_job_folder_name: str, target_main_folder: str, source_main_folder: str) -> str:
    """ Create a new job folder. """

    assert target_main_folder in gv['MAIN_FOLDERS'].keys(),\
        f"folder {target_main_folder} is not a main folder"
    assert source_main_folder in gv['MAIN_FOLDERS'].keys(),\
        f"folder {target_main_folder} is not a main folder"
    
    # find source directory
    source_job_folder_global_path = job_name_to_global_path(gv, job_name, source_main_folder)

    target_job_folder_global_path = os.path.join(
        gv['JOBS_DIR_HOME'],
        target_main_folder,
        new_job_folder_name)

    assert target_job_folder_global_path != source_job_folder_global_path, \
            'the source directory is equal to the target directory'
    os.mkdir(target_job_folder_global_path)
    return target_job_folder_global_path


def copy_job_files(target_dir_global_path: str, source_dir_global_path: str, exclude_extensions: list):
    """ Copy files from source to target print job folder, exclude files with that end with a exluce_extension. """   

    for item in os.listdir(source_dir_global_path):
        source_item = os.path.join(source_dir_global_path, item)
        target_item = os.path.join(target_dir_global_path, item)

        if source_item.endswith(tuple(exclude_extensions)):
            continue
        elif os.path.isdir(source_item):
            copy(source_item, target_dir_global_path)
        else:
            copy(source_item, target_item)

def copy(source_dir_global: str, target_dir_global: str):
    """ Copy directory and subdirectories recursively. """

    if os.path.isdir(source_dir_global):
        for item in os.listdir(source_dir_global):
            copy(os.path.join(source_dir_global, item), target_dir_global)
    else:
        try:
            shutil.copy(source_dir_global, target_dir_global)
        except Exception as e:
            print(f"An error occurred: {e}")

def move(source_dir_global: str, target_dir_global: str):
    """ Move directory and subdirectories recursively. """

    if os.path.isdir(source_dir_global):
        for item in os.listdir(source_dir_global):
            move(os.path.join(source_dir_global, item), target_dir_global)
    else:
        try:
            shutil.move(source_dir_global, target_dir_global)
        except Exception as e:
            print(f"An error occurred: {e}")

def does_job_name_exist(gv: dict, job_name: str) -> bool:
    """ Check if the job name exist, return boolean. """

    for folder_name in get_job_folder_names(gv):
        if folder_name.endswith(job_name):
            return True

    return False

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

def job_name_to_global_path(gv: dict, job_name: str, search_in_main_folder=None) -> str:
    """ Return global path of job. """

    for job_global_path in get_job_global_paths(gv, search_in_main_folder):
        if job_global_path.endswith(job_name):
            return job_global_path

    raise ValueError(f"no job path found for job with name {job_name}")

def job_name_to_job_folder_name(gv: dict, job_name: str, search_in_main_folder=None) -> str:
    """ Get the job folder name from a job name. """

    for job_folder_name in get_job_folder_names(gv, search_in_main_folder):
        if job_name in job_folder_name:
            return job_folder_name

    raise ValueError(f'could not find job folder name for job name: {job_name}')

def does_job_exist_in_main_folder(gv: dict, job_name: str, main_folder: str) -> bool:
    """ Check if a job exists in a main folder. """
    for job_folder_name in get_job_folder_names(gv, main_folder):
        if job_name in job_folder_name:
            return True
    return False

def get_jobs_in_queue(gv: dict) -> int:
    """ return the jobs in the main folders, exluding  the folders AAN_HET_PRINTEN, WACHTRIJ and AFGEKEURD. """

    n_dirs_in_wachtrij = 0

    for main_folder in gv['MAIN_FOLDERS']:
        if main_folder in ['AAN_HET_PRINTEN', 'VERWERKT', 'AFGEKEURD']:
            continue
        n_dirs_in_wachtrij += len(os.listdir(os.path.join(gv['JOBS_DIR_HOME'], main_folder)))
                                              
    return n_dirs_in_wachtrij

def folder_contains_accepted_extension_file(gv: dict, global_path: str) -> bool:
    """ Check if a folder contains at least one file with accepted extension. """
    if any(file.endswith(gv['ACCEPTED_EXTENSIONS']) for file in os.listdir(global_path)):
        return True
    return False

# move to specific functions
# def get_new_job_folder_name(gv: dict, job_name: str, source_dir_global_path: str,
#                             target_main_folder: str) -> str:
#     """ Get a job folder name for a job moved to a main folder. """

#     job_folder_name = job_name_to_job_folder_name(gv, job_name)

#     if target_main_folder in ['AFGEKEURD', 'WACHTRIJ', 'VERWERKT']:
#         return job_folder_name

#     if target_main_folder == 'GESLICED':

#         date = job_folder_name_to_date(gv, job_folder_name)

#         gcode_files = [file for file in os.listdir(source_dir_global_path) if file.lower().endswith(".gcode")]

#         assert len(gcode_files) > 0, \
#             f'no .gcode found in job: {job_name}, slice .stl first'

#         max_time = gcode_files_to_max_time(gcode_files)

#         return date + max_time + job_name

#     if target_main_folder == 'AAN_HET_PRINTEN':
#         return job_folder_name

#     raise ValueError(f'{target_main_folder} is not a main folder')


# TODO: this function should only exist in the 3D printers piece
# def rename_target_item(job_name: str, target_item: str) -> str:
#     """ Rename the target item. """

#     if target_item.lower().endswith('.gcode') and \
#             'GESLICED' in target_item:

#         dir_path, filename = os.path.split(target_item)

#         return os.path.join(dir_path, job_name + '_' + filename)
#     else:
#         return target_item



# TOOD: this function should only exist in the 3D part
# def move_job_partly(gv: dict, job_name: str, exclude_files: List):
#     """ Partly move, partly copy job from GESLICED to AAN_HET_PRINTEN folder. """

#     # find source directory
#     source_dir_global_path = job_name_to_global_path(gv, job_name, 'GESLICED')

#     if does_job_exist_in_main_folder(gv, job_name, 'AAN_HET_PRINTEN'):
#         target_dir_global_path = job_name_to_global_path(gv,
#             job_name, search_in_main_folder='AAN_HET_PRINTEN')
#     else:
#         date = job_folder_name_to_date(gv,
#             job_name_to_job_folder_name(job_name))

#         new_job_folder_name = date + job_name

#         target_dir_global_path = os.path.join(
#             gv['JOBS_DIR_HOME'],
#             'AAN_HET_PRINTEN',
#             new_job_folder_name)
#         os.mkdir(target_dir_global_path)

#     # partly move some files to target
#     # move items from source to target directory
#     for item in os.listdir(source_dir_global_path):
#         source_item = os.path.join(source_dir_global_path, item)
#         target_item = os.path.join(target_dir_global_path, item)

#         if item.lower().endswith('.gcode'):
#             if item in exclude_files:
#                 continue
#             move(source_item, target_item)
#             continue

#         if os.path.isdir(source_item):
#             copy(source_item, target_dir_global_path)
#         if target_dir_global_path.endswith('.bat'):
#             if prevent_batch_file(gv, target_item):
#                 continue
#         copy(source_item, target_item)


