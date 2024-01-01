"""
Convert subfolders in a selected folder to laser jobs.
"""

import os
import sys
import datetime
from typing import Tuple

from global_variables import gv
from laser_job_tracker import LaserJobTracker
from src.create_batch_file import python_to_batch
from src.directory_functions import copy
from src.convert_functions import make_job_name_unique
from src.cmd_farewell_handler import open_wachtrij_folder_cmd_farewell


def create_laser_jobs(folder_global_path: str, project_name: str):

    potential_jobs_local_paths = [folder for folder in os.listdir(folder_global_path)
                                  if os.path.isdir(os.path.join(folder_global_path, folder))]



    if len(potential_jobs_local_paths) == 0:
        print(f'There are no subfolders in {folder_global_path}, aborting. . .')
        sys.exit(0)

    n_valid_laser_jobs = 0
    n_potential_jobs = len(potential_jobs_local_paths)

    for job_number, potential_job_local_path in enumerate(potential_jobs_local_paths):

        # check if the job is valid
        potential_job_global_path = os.path.join(folder_global_path, potential_job_local_path)
        is_valid_job, invalid_reason = is_folder_a_valid_laser_job(potential_job_global_path)

        if is_valid_job:
            job_name = local_path_to_job_name(potential_job_local_path)

            create_laser_job(job_name=make_job_name_unique(gv, project_name+'_'+job_name),
                             job_content_global_path=potential_job_global_path)
            n_valid_laser_jobs += 1
            print(f'({job_number+1}/{n_potential_jobs}) created laser job: {job_name}')


        else:
            print(f'({job_number+1}/{n_potential_jobs}) from folder {potential_job_local_path} not'
                  f' converted to laser job because:\n {invalid_reason} abort!\n')

    print(f'created {n_valid_laser_jobs} laser jobs out of {n_potential_jobs} potential jobs')



def is_folder_a_valid_laser_job(global_path: str) -> Tuple[bool, str]:
    """ Check if a folder can be converted to a laser job. """

    laser_file_count = 0

    for _, _, files in os.walk(global_path):
        for file in files:
            if file.lower().endswith(gv['ACCEPTED_EXTENSIONS']):
                laser_file_count += 1

    if laser_file_count == 0:
        return False, f'no {gv["ACCEPTED_EXTENSIONS"]} attachment found'

    return True, ' '

def create_laser_job(job_name: str, job_content_global_path: str):
    """ Create a laser job from content in job_content_global_path in folder WACHTRIJ. """

    job_tracker = LaserJobTracker()

    job_folder_name = str(datetime.date.today().strftime('%d-%m'))+'_'+job_name
    job_folder_global_path = os.path.join(os.path.join(gv['JOBS_DIR_HOME'], job_folder_name))

    laser_files_dict = {}
    # TODO: make this actual stuff
    for file in os.listdir(job_content_global_path):
        laser_files_dict[job_name + file] = {
                        'file_name': file,
                        'file_global_path': '/text/somewhre/',
                        'material': 'steel',
                        'thickness': '3cm',
                        'amount': '3',
                        'done': False}

    job_tracker.addJob(job_name, job_folder_global_path, laser_files_dict, status="WACHTRIJ")

    copy(job_content_global_path, job_folder_global_path)


def local_path_to_job_name(job_content_local_path: str) -> str:
    """ return a laser job name. """
    return job_content_local_path.replace(' ', '_')

