"""
Convert subfolders in a selected folder to print jobs.
"""
import os
import sys
import datetime
from typing import Tuple
from tkinter import filedialog

from create_batch_file import python_to_batch
from directory_functions import (
    copy,
    make_print_job_name_unique)
from global_variables import (
    FUNCTIONS_DIR_HOME,
    PRINT_DIR_HOME)
from cmd_farewell_handler import open_wachtrij_folder_cmd_farewell
from talk_to_sa import password_please


def is_folder_a_valid_print_job(global_path: str) -> Tuple[bool, str]:
    """ Check if a folder can be converted to a print job. """

    print_file_count = 0

    for root, _, files in os.walk(global_path):
        for file in files:
            if file.lower().endswith(('.stl', '.obj', '.3mf', '.amf', '.zip.amf', '.xml', '.step', '.stp')):
                print_file_count += 1

    if print_file_count == 0:
        return False, 'no .stl attachment found'

    return True, ' '

def create_print_job(job_name: str, job_content_global_path: str):
    """ Create a print job from content in job_content_global_path in folder WACHTRIJ. """

    today = datetime.date.today()
    job_folder_name = str(today.strftime('%d')) + '-' + str(today.strftime('%m')) + '_' + job_name

    job_global_path = os.path.join(os.path.join(PRINT_DIR_HOME, 'WACHTRIJ', job_folder_name))

    os.mkdir(job_global_path)
    copy(job_content_global_path, job_global_path)
    python_to_batch(os.path.join(FUNCTIONS_DIR_HOME, 'afgekeurd.py'), job_name=job_name)
    python_to_batch(os.path.join(FUNCTIONS_DIR_HOME, 'gesliced.py'), job_name=job_name)


def local_path_to_job_name(job_content_local_path: str) -> str:
    """ return a unique print job name. """
    return make_print_job_name_unique(job_content_local_path.replace(' ', '_'))


if __name__ == '__main__':

    print('You are using select_bestand.bat, the default method '
          ' is to click on the input.bat file')
    password_please()

    print('''select <FOLDER> with the following structure:
└───<FOLDER>
  ├───<SUBFOLDER_1>
  │  ├───3d_file.stl
  │  └───another_3d_file.stl
  └───<SUBFOLDER_2>
    ├───3d_file.stl
    └───another_3d_file.stl
    ''')

    folder_global_path = filedialog.askdirectory(initialdir=os.path.join(PRINT_DIR_HOME, '../'))

    potential_jobs_local_paths = [folder for folder in os.listdir(folder_global_path)
                                  if os.path.isdir(os.path.join(folder_global_path, folder))]

    if len(potential_jobs_local_paths) == 0:
        print(f'There are no subfolders in {folder_global_path}, aborting. . .')
        sys.exit(0)

    project_name = input(f'Where are the 3D prints for? Enter a name for the project:')
    n_valid_print_jobs = 0
    n_potential_jobs = len(potential_jobs_local_paths)

    for job_number, potential_job_local_path in enumerate(potential_jobs_local_paths):
        
        # check if the job is valid
        potential_job_global_path = os.path.join(folder_global_path, potential_job_local_path)
        is_valid_job, invalid_reason = is_folder_a_valid_print_job(potential_job_global_path)

        if is_valid_job:
            job_name = local_path_to_job_name(potential_job_local_path)
            job_folder_name = project_name + '_' + job_name

            create_print_job(job_folder_name, potential_job_global_path)
            n_valid_print_jobs += 1
            print(f'({job_number}/{n_potential_jobs}) created print job: {job_name}')

        else:
            print(f'({job_number}/{n_potential_jobs}) from folder {potential_job_local_path} not'
                  f' converted to print job because:\n {invalid_reason} abort!\n')

    print(f'created {n_valid_print_jobs} print jobs out of {n_potential_jobs} potential jobs')

    if n_valid_print_jobs > 0:
        open_wachtrij_folder_cmd_farewell()
