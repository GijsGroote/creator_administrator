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
from src.qmessagebox import TimedMessage, YesOrNoMessageBox

class LaserJobTracker(JobTracker):
    """
    Before changing files on file system, change the job_log.json

    use the check_health function to check the file system health based on the job_log.json file
    """

    def __init__(self, parent_widget):
        super().__init__(gv, parent_widget)

        self.checkTrackerFileHealth()

        self.job_keys.append(['laserfiles'])

    def addJob(self, job_name: str, job_folder_global_path: str, files_dict: dict, status='WACHTRIJ') -> dict:
        """ Add a job to the tracker. """

        with open(self.tracker_file_path, 'r') as tracker_file:
            tracker_dict = json.load(tracker_file)

        job_name = self.makeJobNameUnique(job_name)

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

        delete(deleted_job_dict['job_folder_global_path'])
        

        with open(self.tracker_file_path, 'w') as tracker_file:
            json.dump(tracker_dict, tracker_file, indent=4)


    def updateJobStatus(self, job_name: str, new_job_status: str):
        ''' Update status of a job. '''

        with open(self.tracker_file_path, 'r') as tracker_file:
            tracker_dict = json.load(tracker_file)

        tracker_dict[job_name]['status'] = new_job_status

        with open(self.tracker_file_path, 'w') as tracker_file:
            json.dump(tracker_dict, tracker_file, indent=4)

    def markFileIsDone(self, job_name: str, file_global_path: str):
        ''' Update file status to done = True. '''
        assert job_name is not None, f'Job name is None'

        with open(self.tracker_file_path, 'r') as tracker_file:
            tracker_dict = json.load(tracker_file)

        for file_dict in tracker_dict[job_name]['laser_files'].values():
            if file_dict['file_global_path']==file_global_path:
                file_dict['done'] = True

        with open(self.tracker_file_path, 'w') as tracker_file:
            json.dump(tracker_dict, tracker_file, indent=4)


    def getJobDict(self, job_name: str) -> dict:
        ''' Return the job dict from a job name. '''
        
        with open(self.tracker_file_path, 'r') as tracker_file:
            tracker_file = json.load(tracker_file)

        if job_name in tracker_file:
            return tracker_file[job_name]
        return None

    def getJobFolderGlobalPathFromJobName(self, job_name: str) -> str:
        ''' Return the job folder global path from the job name. '''
        with open(self.tracker_file_path, 'r') as tracker_file:
            tracker_dict = json.load(tracker_file)

        return tracker_dict[job_name]['job_folder_global_path']
                        
    def checkHealth(self):
        """ Check and repair system. """

        self.checkTrackerFileHealth()

        # Check folder laser_jobs
        jobs_folder_global_path = os.path.join(gv['DATA_DIR_HOME'], 'laser_jobs')
        if not os.path.exists(jobs_folder_global_path):
                os.mkdir(jobs_folder_global_path)

        # Get job info from tracker file
        with open(self.tracker_file_path, 'r') as tracker_file:
            tracker_dict = json.load(tracker_file)

        # remove old jobs
        for job_key, job_dict in tracker_dict.items():
            if self.isJobOld(job_dict['created_on_date']) and job_dict['status'] != 'WACHTRIJ':
                self.deleteJob(job_key)

        # get job info from file system
        jobs_global_paths = [os.path.join(jobs_folder_global_path, job_folder) for job_folder in os.listdir(jobs_folder_global_path) 
                                   if os.path.isdir(os.path.join(jobs_folder_global_path, job_folder) )]

        # keep track of the jobs checked
        jobs_checked = {job_name: False for job_name in tracker_dict.keys()}

        for job_global_path in jobs_global_paths:
            # actual_job_main_folder = os.path.basename(os.path.dirname(actual_job_global_path))

            job_key, job_dict = self.jobGlobalPathToTrackerJobDict(
                tracker_dict, job_global_path)

            
            if job_dict is None:
                yes_or_no = YesOrNoMessageBox(parent=self.parent_widget, text=f'SYNCHRONIZE ISSUES! Job Tracker and jobs on File System are out of sync!\n'\
                                              f'what do you want to do with {job_global_path}?', yes_button_text='Add to  job tracker', no_button_tex='Remove from file system')

                if yes_or_no.answer():
                    # TODO: find the material details from the .dxf files first please
                    # add this file to the to tracker
                    print('TODO: add job to tracker')
                    pass

                else:
                    # remove that directory
                    delete(job_global_path)
                    continue

            if not self.IsJobDictAndFileSystemInSync(job_dict, job_global_path):
                tracker_dict[job_key] = self.syncronizeJobDictWithFileSystem(job_dict, job_global_path)
            jobs_checked[job_dict['job_name']] = True

        for tracker_job_name, job_checked in jobs_checked.items():
            if not job_checked:
                tracker_dict.pop(tracker_job_name)

        with open(self.tracker_file_path, 'w') as tracker_file:
            json.dump(tracker_dict, tracker_file, indent=4)

        self.makeBackup()

    def IsJobDictAndFileSystemInSync(self, job_dict, job_folder_global_path):
        ''' Check if all files are in both the tracker and the file system. '''
        valid_file_names = [file_name for file_name in os.listdir(job_folder_global_path) if file_name.lower().endswith(gv['ACCEPTED_EXTENSIONS'])]

        for file in valid_file_names:
            if not any([os.path.basename(laser_file_dict['file_global_path'])==file for laser_file_dict in job_dict['laser_files'].values()]):
                return False
            
        for key, file_dict in job_dict['laser_files'].items():
            if not os.path.basename(file_dict['file_global_path']) in valid_file_names:
                return False
            
        return True
    
    def syncronizeJobDictWithFileSystem(self, job_dict: dict, job_folder_global_path: str):
        ''' Sychronize job dict based on file system. '''
        valid_file_names = [file_name for file_name in os.listdir(job_folder_global_path) if file_name.lower().endswith(gv['ACCEPTED_EXTENSIONS'])]

        # delete file from job dict if it is not on the file system
        remove_keys = []
        for key, file_dict in job_dict['laser_files'].items():
            if not os.path.basename(file_dict['file_global_path']) in valid_file_names:
                print(f'could not find tracker file name on file system, detete it')
                remove_keys.append(key)

        for key in remove_keys:
            print(f'remove the key {key}')
            job_dict['laser_files'].pop(key)
        
        # add files that are on the file system and not in the tracker job dict
        for file in valid_file_names:
            if not any([os.path.basename(laser_file_dict['file_global_path'])==file for laser_file_dict in job_dict['laser_files'].values()]):
                print(f'could not find file with name: {file} add it to tracker')
                # TODO: add this file to files

        return job_dict


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
                for laser_file_dict in job_dict['laser_files'].values():
                    materials.add(laser_file_dict['material'])
                    
        return materials

    def getMaterialAndThicknessList(self) -> list:
        ''' Return all materials and thickness with status WACHTRIJ. '''

        with open(self.tracker_file_path, 'r') as tracker_file:
            tracker_dict = json.load(tracker_file)

        materials_and_thickness_set = set()
        for job_dict in tracker_dict.values():
            if job_dict['status'] == 'WACHTRIJ':
                for laser_file_dict in job_dict['laser_files'].values():
                    if not laser_file_dict['done']:
                        materials_and_thickness_set.add(
                                laser_file_dict['material']+'_'+laser_file_dict['thickness']+'mm')
                    
        return list(materials_and_thickness_set)

    def getDXFsAndPaths(self, material: str, thickness: str) -> list:
        ''' Return all names and global paths of dxf files with
        material, thickness and status WACHTRIJ. '''

        with open(self.tracker_file_path, 'r') as tracker_file:
            tracker_dict = json.load(tracker_file)

        dxfs_names_and_global_paths = []
        for job_dict in tracker_dict.values():
            if job_dict['status'] == 'WACHTRIJ':
                for key, laser_file_dict in job_dict['laser_files'].items():
                    if laser_file_dict['material'] == material and laser_file_dict['thickness'] == thickness:
                        dxfs_names_and_global_paths.append((key, laser_file_dict['file_global_path']))
                   
        return dxfs_names_and_global_paths
    
    def getLaserFilesDict(self, job_name) -> dict:
        ''' TODO '''

        with open(self.tracker_file_path, 'r') as tracker_file:
            tracker_dict = json.load(tracker_file)
        return tracker_dict[job_name]['laser_files']

    def fileGlobalPathToJobName(self, file_global_path: str) -> str:
        ''' Return a job name from a file. '''
        with open(self.tracker_file_path, 'r') as tracker_file:
            tracker_dict = json.load(tracker_file)

        job_name = None
        for job_dict in tracker_dict.values():
            for laser_file_dict in job_dict['laser_files'].values():
                if laser_file_dict['file_global_path'] == file_global_path:
                    job_name = job_dict['job_name']
        return job_name

    def isJobDone(self, job_name: str) -> bool: 
        ''' Return boolean indicating if a job is done. '''
        with open(self.tracker_file_path, 'r') as tracker_file:
            tracker_dict = json.load(tracker_file)

        for file_dict in tracker_dict[job_name]['laser_files'].values():
            if not file_dict['done']:
                return False
        return True


    def getLaserFilesString(self, job_name: str) -> str:
        ''' Return a sting representation of all laser files. '''

        with open(self.tracker_file_path, 'r') as tracker_file:
            tracker_dict = json.load(tracker_file)

        return_string = ""
        for file_dict in tracker_dict[job_name]['laser_files'].values():
            return_string += f'{file_dict["file_name"]}\n'

        return return_string

