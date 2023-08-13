#! /usr/bin/env python3

import os
import sys
import PyInstaller.__main__

from global_variables import FIG_DIR_HOME
from directory_functions import job_name_to_global_path

def read_job_name_file():
    """ read and return the content from job_name.txt """
    # Check if MEIPASS attribute is available in sys else return current file path
    bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))

    with open(os.path.abspath(os.path.join(
                bundle_dir, 'job_name.txt')), "r+") as job_name_file:
        return job_name_file.read()

def python_to_exe(python_path: str, job_name: str):
    """ convert a python file to an executable file an move to local_path. """

    assert os.path.isfile(python_path), f"file {python_path} does not exist."
    global_path = job_name_to_global_path(job_name)
    assert os.path.exists(global_path), f"path {global_path} does not exist."

    with open("job_name.txt", "w") as file:
        file.write(job_name)

    try:
        PyInstaller.__main__.run([
            python_path,
            '--onefile',
            '--console',
            f'--distpath={global_path}',
            f'--icon={os.path.join(FIG_DIR_HOME, "download.ico")}',
            '--add-data=job_name.txt;.',
        ])

    except FileExistsError as exc:
        print(exc)

