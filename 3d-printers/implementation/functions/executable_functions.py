#! /usr/bin/env python3

import os
import sys
import subprocess

from global_variables import (
    LOCKHUNTER_PATH,
    PYTHON_PATH)
from directory_functions import job_name_to_global_path

def read_job_name_file() -> str:
    """ read and return the content from job_name.txt """
    # Check if MEIPASS attribute is available in sys else return current file path
    bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))

    with open(os.path.abspath(os.path.join(
                bundle_dir, 'job_name.txt')), "r+") as job_name_file:
        return job_name_file.read()

def python_to_batch(python_path: str, job_name: str):
    """ convert a python file to an batch file. """

    assert os.path.isfile(python_path), f"file {python_path} does not exist."
    job_global_path = job_name_to_global_path(job_name)
    assert os.path.exists(job_global_path), f"path {job_global_path} does not exist."

    function_name = os.path.splitext(os.path.basename(python_path))[0]

    myBat = open(os.path.join(job_global_path, f'{function_name}.bat'), 'w+')
    myBat.write(rf"""
@echo off
"{PYTHON_PATH}" "{python_path}" "{job_name}"
pause
""")
    myBat.close()

def unlock_and_delete_folder(folder_global_path: str):
    """ remove a file folder using lockhunter """

    # TODO: this is a dangerous functions and needs extra care.

    print(f'unlocking and deleting the directory {folder_global_path}')

    command = ' '.join([LOCKHUNTER_PATH, f'/delete /silent {folder_global_path}'])
    subprocess.Popen(command)
