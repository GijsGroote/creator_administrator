'''
Functionality for moving/copying or searching in directories.
'''

import os
import sys
import shutil
import subprocess


from PyQt6.QtWidgets import QWidget
from src.qmessagebox import  ErrorQMessageBox



def copy_item(source_dir_global: str, target_dir_global: str):
    ''' Copy directory and subdirectories recursively. '''

    if os.path.exists(target_dir_global):
        return

    if os.path.isdir(source_dir_global):
        shutil.copytree(source_dir_global, target_dir_global)   

    else:
        shutil.copy(source_dir_global, target_dir_global)
        
def delete_item(parent: QWidget, gv: dict, item_global_path: str):
    ''' Delete the file from the file system. '''

    assert item_global_path.startswith((gv['DATA_DIR_HOME'], gv['TODO_DIR_HOME'])), f'Can only delete files in subdirectoreis of DATA_DIR_HOME or TODO_DIR_HOME.\nCannot delete {item_global_path}'

    if os.path.exists(item_global_path):
        try:
            if os.path.isdir(item_global_path):
                shutil.rmtree(item_global_path)
            else:
                os.remove(item_global_path)

        except PermissionError as exc:
            ErrorQMessageBox(parent, text=f'Error Occured: {str(exc)}')

def delete_directory_content(parent: QWidget, gv: dict, folder_global_path: str):
        ''' Delete all contents of a folder. '''
        for item in os.listdir(folder_global_path):
            delete_item(parent, gv, os.path.join(folder_global_path, item))

def open_file(file_global_path: str, executable_global_path=None):
    ''' Open a folder in the default file explorer. '''

    assert os.path.exists(file_global_path), f'could not find file: {file_global_path}'

    if sys.platform == 'linux':
        subprocess.Popen(['xdg-open', file_global_path]) # pylint: disable=consider-using-with

    elif sys.platform == 'win32':
        if executable_global_path is not None:
            assert os.path.exists(executable_global_path), f'executable {executable_global_path} does not exist'
            subprocess.Popen([executable_global_path, file_global_path]) # pylint: disable=consider-using-with

        else:
            subprocess.Popen(['explorer', file_global_path]) # pylint: disable=consider-using-with

    else: 
        raise ValueError(f'unknown platform: {sys.platform}')

def open_folder(folder_global_path: str):
    ''' Open a folder in the default file explorer. '''

    assert os.path.exists(folder_global_path), f'could not find folder: {folder_global_path}'

    if sys.platform == 'linux':
        with subprocess.Popen(['xdg-open', folder_global_path]):
            pass
    elif sys.platform == 'win32':
        with subprocess.Popen(['explorer', folder_global_path]):
            pass
    else: 
        raise ValueError(f'unknown platform: {sys.platform}')

def shorten_folder_name(path: str, max_char_length=45) -> str:
        ''' Return a short folder name. '''
        if len(path) <= 2:
            return path

        if len(path) > max_char_length:
            path = '..'+path[-max_char_length+2:]
        return path
