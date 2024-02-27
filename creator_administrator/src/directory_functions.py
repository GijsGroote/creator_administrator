"""
Functionality for moving/copying or searching in directories.
"""

import os
import sys
import shutil
import subprocess

def copy_item(source_dir_global: str, target_dir_global: str):
    """ Copy directory and subdirectories recursively. """

    if os.path.exists(target_dir_global):
        return

    if os.path.isdir(source_dir_global):
        shutil.copytree(source_dir_global, target_dir_global)   

    else:
        shutil.copy(source_dir_global, target_dir_global)
        
# TODO: move source_dir to target_dir (and content), but target_dir already exist
# result: content from source_dir is not copied to target_dir
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

def delete(item_global_path: str):
    """ Delete the file from the file system. """
    if os.path.exists(item_global_path):
        try:
            if os.path.isdir(item_global_path):
                shutil.rmtree(item_global_path)
            else:
                os.remove(item_global_path)
        except Exception as e:
            print(f"An error occurred: {e}") # TODO: better to not print anything in a GUI based application

def delete_directory_content(folder_global_path: str):
        ''' Delete all contents of a folder. '''
        for item in os.listdir(folder_global_path):
            delete(os.path.join(folder_global_path, item))

def open_file(file_global_path: str):
    ''' Open a folder in the default file explorer. '''

    assert os.path.exists(file_global_path), f'could not find file: {file_global_path}'

    if sys.platform == 'linux':
        subprocess.Popen(['xdg-open', file_global_path])
    elif sys.platform == 'win32':
        subprocess.Popen(['explorer', file_global_path])
    else: 
        raise ValueError(f'unknown platform: {sys.platform}')

def open_folder(folder_global_path: str):
    ''' Open a folder in the default file explorer. '''

    assert os.path.exists(folder_global_path), f'could not find folder: {folder_global_path}'

    if sys.platform == 'linux':
        subprocess.Popen(['xdg-open', folder_global_path])
    elif sys.platform == 'win32':
        subprocess.Popen(['explorer', folder_global_path])
    else: 
        raise ValueError(f'unknown platform: {sys.platform}')

def shorten_folder_name(path: str, max_char_length: int) -> str:
        ''' Return a short folder name. '''
        if len(path) <= 2:
            return path

        if len(path) > max_char_length:
            path = '..'+path[-max_char_length+2:]
        return path
