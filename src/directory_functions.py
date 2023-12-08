"""
Functionality for moving/copying or searching in directories.
"""

import os
import shutil
import json
import subprocess
from typing import List

def create_new_job_folder(gv: dict, job_name, new_job_folder_name: str, target_main_folder: str, source_main_folder: str) -> str:
    """ Create a new job folder. """

    assert target_main_folder in gv['MAIN_FOLDERS'],\
        f"folder {target_main_folder} is not a main folder"
    assert source_main_folder in gv['MAIN_FOLDERS'],\
        f"folder {source_main_folder} is not a main folder"
    
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
        else:
            copy(source_item, target_item)


def copy(source_dir_global: str, target_dir_global: str):
    """ Copy directory and subdirectories recursively. """
    if os.path.exists(target_dir_global):
        return
    
    elif os.path.isdir(source_dir_global):
        shutil.copytree(source_dir_global, target_dir_global)   
    
    else:
        shutil.copy(source_dir_global, target_dir_global)
        
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

def delete(gv, item_global_path: str):
    """ Delete the file from the file system. """
    print(f'fuck lets remove {item_global_path}')
    if os.path.exists(item_global_path):
        try:
            if os.path.isdir(item_global_path):
                shutil.rmtree(item_global_path)
            else:
                os.remove(item_global_path)
        except Exception as e:
            subprocess.run(rf'{gv["IOBIT_UNLOCKER_PATH"]} /Delete {item_global_path}')

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
        main_folders = [folder for folder in os.listdir(gv['JOBS_DIR_HOME']) if folder.endswith(tuple(gv['MAIN_FOLDERS'].keys()))]
    
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

def global_path_to_main_folder(gv: dict, global_path: str) -> str:
    """ Return the main folder from a global path. """
    for main_folder in gv['MAIN_FOLDERS'].keys():
        if main_folder in global_path:
            return main_folder
    raise ValueError(f'could not find a main folder in {global_path}')

def get_prefix_of_subfolders(global_path: str) -> list:
    """ Return prefixes seperated by a '_' of subfolder names. """
    prefixes = set()
    for prefix_global_path in os.listdir(global_path):
        prefixes.add(os.path.basename(prefix_global_path).split('_')[0])

    return list(prefixes)

def read_json_file(json_file_global_path: str) -> dict:
    """ return the JSON file as dictionary. """

    with open(json_file_global_path, 'r') as file:
        json_dict = json.load(file)
    return json_dict

def write_json_file(dictionary: dict, json_file_global_path: str):
    """ Write dictionary to JSON file. """

    with open(json_file_global_path, 'w') as file:
        json.dump(dictionary, file, indent=4)

 