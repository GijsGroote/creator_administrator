"""
Convert subfolders in a selected folder to laser jobs.
"""

import os
import sys
import datetime
from typing import Tuple
from tkinter import filedialog

from global_variables import gv
# from job_tracker import JobTracker
from src.batch import python_to_batch
from src.directory_functions import copy
from src.convert_functions import make_job_name_unique
from src.cmd_farewell_handler import open_wachtrij_folder_cmd_farewell
from src.talk_to_sa import password_please


def is_folder_a_valid_laser_job(global_path: str) -> Tuple[bool, str]:
    """ Check if a folder can be converted to a laser job. """

    laser_file_count = 0

    for _, _, files in os.walk(global_path):
        for file in files:
            if file.lower().endswith(gv['ACCEPETED_EXTENSIONS']):
                laser_file_count += 1

    if laser_file_count == 0:
        return False, 'no .stl attachment found'

    return True, ' '

def create_laser_job(job_name: str, job_content_global_path: str):
    """ Create a laser job from content in job_content_global_path in folder WACHTRIJ. """

    today = datetime.date.today()
    job_folder_name = str(today.strftime('%d')) + '-' + str(today.strftime('%m')) + '_' + job_name

    job_global_path = os.path.join(os.path.join(gv['JOBS_DIR_HOME'], 'WACHTRIJ', job_folder_name))

    os.mkdir(job_global_path)
    copy(job_content_global_path, job_global_path)
    python_to_batch(gv, os.path.join(gv['FUNCTIONS_DIR_HOME'], 'afgekeurd.py'), job_name=job_name)
    python_to_batch(gv, os.path.join(gv['FUNCTIONS_DIR_HOME'], 'gesliced.py'), job_name=job_name)


def local_path_to_job_name(job_content_local_path: str) -> str:
    """ return a unique laser job name. """
    return make_job_name_unique(job_content_local_path.replace(' ', '_'))


if __name__ == '__main__':

    # check health
    # job_tracker = JobTracker()
    # job_tracker.check_health()

    print('You are using select_bestand.bat, the default method is the input.bat file')
    password_please(gv)

    print('''select <FOLDER> with the following structure:
└───<FOLDER>
  ├───<SUBFOLDER_1>
  │  ├───3d_file.stl
  │  └───another_3d_file.stl
  └───<SUBFOLDER_2>
    ├───3d_file.stl
    └───another_3d_file.stl
    ''')

    folder_global_path = filedialog.askdirectory(initialdir=os.path.join(gv['JOBS_DIR_HOME'], '../'))

    potential_jobs_local_paths = [folder for folder in os.listdir(folder_global_path)
                                  if os.path.isdir(os.path.join(folder_global_path, folder))]


    if len(potential_jobs_local_paths) == 0:
        print(f'There are no subfolders in {folder_global_path}, aborting. . .')
        sys.exit(0)

    project_name = input('Where are the 3D lasers for? Enter a name for the project:')
    n_valid_laser_jobs = 0
    n_potential_jobs = len(potential_jobs_local_paths)

    for job_number, potential_job_local_path in enumerate(potential_jobs_local_paths):

        # check if the job is valid
        potential_job_global_path = os.path.join(folder_global_path, potential_job_local_path)
        is_valid_job, invalid_reason = is_folder_a_valid_laser_job(potential_job_global_path)

        if is_valid_job:
            job_name = local_path_to_job_name(potential_job_local_path)
            job_folder_name = project_name + '_' + job_name

            create_laser_job(job_folder_name, potential_job_global_path)
            n_valid_laser_jobs += 1
            print(f'({job_number}/{n_potential_jobs}) created laser job: {job_name}')

            # job_tracker.add_job(job_name, "WACHTRIJ")

        else:
            print(f'({job_number}/{n_potential_jobs}) from folder {potential_job_local_path} not'
                  f' converted to laser job because:\n {invalid_reason} abort!\n')

    print(f'created {n_valid_laser_jobs} laser jobs out of {n_potential_jobs} potential jobs')

    if n_valid_laser_jobs > 0:
        open_wachtrij_folder_cmd_farewell()
