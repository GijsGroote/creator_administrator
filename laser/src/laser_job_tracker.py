"""
Laser Job tracker, tracking laser jobs.
"""

import json
import shutil
import os
import sys
import subprocess


import glob
import sys

from typing import Tuple
from datetime import datetime

from global_variables import gv

from src.directory_functions import delete

from src.job_tracker import JobTracker


class LaserJobTracker(JobTracker):
    """
    Before changing files on file system, change the job_log.json

    use the check_health function to check the file system health based on the job_log.json file
    """

    def __init__(self):
        JobTracker.__init__(self, gv)

        self.job_keys.append(['laserfiles'])

    def addJob(self, job_name: str, job_folder_global_path: str, files_dict: dict, status='WACHTRIJ') -> dict:
        """ Add a job to the tracker. """

        with open(self.tracker_file_path, 'r') as tracker_file:
            tracker_dict = json.load(tracker_file)

        add_job_dict = {'job_name': job_name,
                        'job_folder_global_path': job_folder_global_path,
                        'dynamic_job_name': str(datetime.now().strftime("%d-%m"))+'_'+job_name,
                        'status': status,
                        'created_on_date': str(datetime.now().strftime("%d-%m-%Y")),
                        'laser_files': files_dict
                        }

        tracker_dict[job_name] = add_job_dict

        with open(self.tracker_file_path, 'w') as tracker_file:
            json.dump(tracker_dict, tracker_file, indent=4)

        return add_job_dict
    
    def deleteJob(self, job_name: str) -> dict:
        """ Delete a job from the job tracker. """

        with open(self.tracker_file_path, 'r') as tracker_file:
            tracker_dict = json.load(tracker_file)

        deleted_job_dict = tracker_dict.pop(job_name)

        delete(gv, deleted_job_dict['job_folder_global_path'])
        

        with open(self.tracker_file_path, 'w') as tracker_file:
            json.dump(tracker_dict, tracker_file, indent=4)


    def updateJobStatus(self, job_name: str, new_job_status: str):
        ''' Update status of a job. '''

        with open(self.tracker_file_path, 'r') as tracker_file:
            tracker_dict = json.load(tracker_file)

        tracker_dict[job_name]['status'] = new_job_status

        with open(self.tracker_file_path, 'w') as tracker_file:
            json.dump(tracker_dict, tracker_file, indent=4)

    def getJobDict(self, job_name: str) -> dict:
        ''' Return the job dict from a job name. '''
        
        with open(self.tracker_file_path, 'r') as tracker_file:
            return json.load(tracker_file)[job_name]

    def jobNameToJobFolderGlobalPath(self, job_name: str) -> str:
        ''' Return the job folder global path from the job name. '''
        with open(self.tracker_file_path, 'r') as tracker_file:
            tracker_dict = json.load(tracker_file)

        return tracker_dict[job_name]['job_folder_global_path']
                        
    # TODO: This checkhealth really is not up-to-date
    def checkHealth(self):
        """ Check and repair system. """
        pass

#         self.checkTrackerFileHealth()

#         print("Checking system health...")

#         # check JOBS_DIR_HOME and MAIN_FOLDERS existance
#         for folder in ['', *gv['MAIN_FOLDERS'].keys(), *gv['MINOR_FOLDERS'].keys()]:
#             folder_global_path = os.path.join(gv['JOBS_DIR_HOME'], folder)

#             if not os.path.exists(folder_global_path):
#                 os.mkdir(folder_global_path)
#                 print(f'created folder: {folder_global_path}')

#         # Get job info from tracker file
#         with open(self.tracker_file_path, 'r') as tracker_file:
#             tracker_dict = json.load(tracker_file)

#         # get job info from file system
#         actual_job_global_paths = get_job_global_paths(gv)

#         # keep track of the jobs checked
#         jobs_checked = {actual_job_name: False for actual_job_name in tracker_dict.keys()}

#         for actual_job_global_path in actual_job_global_paths:
#             actual_job_main_folder = os.path.basename(os.path.dirname(actual_job_global_path))

#             tracker_job_name, tracker_job_dict = self.job_global_path_to_tracker_job_dict(
#                 tracker_dict, actual_job_global_path)

#             if tracker_job_name is None:
#                 print("SYNCHRONIZE ISSUES! Job Tracker and jobs on File System are out of sync!\n")
#                 print(f"Job in: {actual_job_global_path} is not in the job tracker")

#                 if yes_or_no(
#                         f"\n{actual_job_global_path} will be removed\nor do you want to add it to the job tracker (Y/n)?"):
#                     tracker_job_name = job_folder_name_to_job_name(os.path.basename(actual_job_global_path))

#                     # remove all batch files (they will be recreated later)
#                     for file in os.listdir(actual_job_global_path):
#                         if file.endswith('.bat'):
#                             delete(gv['IOBIT_UNLOCKER_PATH'], os.path.join(actual_job_global_path, file))

#                     tracker_job_dict = {
#                         'job_name': tracker_job_name,
#                         'main_folder': global_path_to_main_folder(gv, actual_job_global_path),
#                         'created_on_date': str(datetime.now().strftime("%d-%m-%Y")),
#                         'laser_files': create_files_dict(tracker_job_name)
#                         }
                    
#                     tracker_dict[tracker_job_name] = tracker_job_dict

#                 else:
#                     # remove that directory
#                     delete(gv['IOBIT_UNLOCKER_PATH'], actual_job_global_path)
#                     continue

#             # check if the job is in the correct main folder
#             if not actual_job_main_folder == tracker_job_dict["main_folder"]:
#                 print(f"\nWarning: Job Tracker and folders on File System disagree...")
#                 print(f"Job: {tracker_job_name} location according to:")
#                 print(f"    Job Tracker: {tracker_job_dict['main_folder']}")
#                 print(f"    File System: {actual_job_main_folder}\n")
#                 if yes_or_no(f"Delete job {tracker_job_name} (Y/n)?"):
#                     delete(gv['IOBIT_UNLOCKER_PATH'], actual_job_global_path)
#                     print(f"Job {tracker_job_name} deleted")
#                     continue
#                 else:
#                     print("aborting..")
#                     sys.exit(0)
            
#             # create batch files for jobs
#             if not all([os.path.exists(os.path.join(actual_job_global_path, batch_file)) for batch_file in 
#                                        gv['MAIN_FOLDERS'][tracker_job_dict['main_folder']]['allowed_batch_files']]):
#                 create_batch_files_for_job_folder(gv, tracker_job_dict['job_name'], tracker_job_dict['main_folder'])
                    
#             # repair the WACHTRIJ_MATERIAAL folder
#             for job_dict in tracker_dict.values():
#                 if job_dict['main_folder'] == 'WACHTRIJ':
#                     for key, file_dict in job_dict['laser_files'].items():
                                        
#                         material_folder_global_path = os.path.join(gv['JOBS_DIR_HOME'],
#                                                     'WACHTRIJ_MATERIAAL', file_dict['material']+'_'+file_dict['thickness'])

#                         # repair WACHTRIJ_MATERIAAL folder
#                         if not (os.path.exists(material_folder_global_path) and
#                                 os.path.exists(os.path.join(material_folder_global_path,
#                                 file_dict['amount']+'x_'+key)) and
#                                 os.path.exists(os.path.join(material_folder_global_path, 'materiaal_klaar.bat'))):
#                             self.add_file_to_wachtrij_material(job_dict)

#             jobs_checked[tracker_job_name] = True

#         for tracker_job_name, pj_checked in jobs_checked.items():
#             if not pj_checked:
#                 print(f"Job: {tracker_job_name} not found on file system and removed from job tracker")

#                 tracker_dict.pop(tracker_job_name)

#         with open(self.tracker_file_path, 'w') as tracker_file:
#             json.dump(tracker_dict, tracker_file, indent=4)

#         self.make_backup()
#         print("system healthy :)\n")


    def getNumberOfJobsInQueue(self) -> int:
        ''' Return the number of jobs with status WACHTRIJ. '''
        return self.getNumberOfJobsWithStatus(['WACHTRIJ'])

    def getExistingMaterials(self) -> set:
        ''' Return all materials that exist in the jobs with a wachtrij status. '''
        with open(self.tracker_file_path, 'r') as tracker_file:
            tracker_dict = json.load(tracker_file)

        materials = set()
        for job_dict in tracker_dict.values():
            if job_dict['status'] == 'WACHTRIJ':
                for laser_files_dict in job_dict['laser_files'].values():
                    materials.add(laser_files_dict['material'])
                    
        return materials

