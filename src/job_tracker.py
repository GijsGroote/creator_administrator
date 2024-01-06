"""
Job tracker, a backup to check and repair the actual files on the file system.
"""

import json
import shutil
import os
import abc
import sys
from datetime import datetime
from typing import List

class JobTracker:

    def __init__(self, gv: dict):
        self.gv = gv
        self.job_keys = ['job_name', 'dynamic_job_name', 'status',
                         'folder_path', 'created_on_date']
        self.tracker_file_path = gv['TRACKER_FILE_PATH']
        self.tracker_backup_file_path = gv['TRACKER_FILE_PATH'].replace("job_log.json",
                                        "job_log_backup.json")

        self.checkTrackerFileHealth()

    @abc.abstractmethod
    def addJob(self, job_name: str, main_folder: str, files_dict: dict) -> dict:
        """ Add a job to the tracker. """

    @abc.abstractmethod
    def checkHealth(self):
        """ Check and repair system. """

    def createTrackerFile(self):
        """ Create the file that tracks jobs. """
        if os.path.exists(self.tracker_backup_file_path):
            if yes_or_no(f"Backup file detected at: {self.tracker_backup_file_path}, do you want to restore it (Y/n)?"):
                os.rename(self.tracker_backup_file_path, self.tracker_file_path)
                print("Backup restored!")
                return

        with open(self.tracker_file_path, 'w') as tracker_file:
            json.dump(dict(), tracker_file, indent=4)

        print(f"{self.tracker_file_path} created!\n")

    def checkTrackerFileHealth(self):
        # Create the tracker file if it doesn't exist
        if not os.path.exists(self.tracker_file_path):
            print(f"tracker file was not detected at: {self.tracker_file_path}")
            self.createTrackerFile()

        try:
            with open(self.tracker_file_path, 'r') as tracker_file:
                json.load(tracker_file)
        except Exception as e:
            print(f"Cannot read tracker file at: {self.tracker_file_path}")
            
            if os.path.isfile(self.tracker_backup_file_path):
                print("\nBackup file exists :)")
                if yes_or_no('Do you want to restore the backup tracker file (Y/n)?'):
                    os.remove(self.tracker_file_path)
                    os.rename(self.tracker_backup_file_path, self.tracker_file_path)
                print('backup tracker file restored.')
            else: 
                print(f"MANUALLY REPAIR TRACKER FILE!")

            sys.exit(0)

    def makeBackup(self):
        """ Make a backup of the tracker file. """
        try:
            shutil.copy(self.tracker_file_path, self.tracker_backup_file_path)
        except FileExistsError:
            os.remove(self.tracker_backup_file_path)
            shutil.copy(self.tracker_file_path, self.tracker_backup_file_path)    

    def isJobOld(self, created_on_date: str) -> bool:
        """ Check if the job is old. """
        created_on_date_object = datetime.strptime(created_on_date, "%d-%m-%Y")
        current_date_object = datetime.now()
        date_difference = current_date_object - created_on_date_object
        return date_difference.days > self.gv['DAYS_TO_KEEP_JOBS']

    def updateJobStatus(self, job_name, new_status):
        """ Update the main folder in the tracker. """
        with open(self.tracker_file_path, 'r') as tracker_file:
            tracker_dict = json.load(tracker_file)

        # tracker_dict[job_name]["main_folder"] = new_main_folder
        # if new_main_folder == 'VERWERKT':
        #     for file_dict in tracker_dict[job_name]['laser_files'].values():
        #         file_dict['done'] = True

        with open(self.tracker_file_path, 'w') as tracker_file:
            json.dump(tracker_dict, tracker_file, indent=4)

    def getStaticAndDynamicJobNamesWithStatus(self, status: str) -> List[tuple]:
        ''' Return a list containing all dynamic job names that have a given status '''

        with open(self.tracker_file_path, 'r') as tracker_file:
            tracker_dict = json.load(tracker_file)

        return [(job_name, job_dict['dynamic_job_name']) for job_name, job_dict in tracker_dict.items() if job_dict['status'] == status]

    def getAllStaticAndDynamicJobNames(self) -> List[tuple]:
        ''' Return a list containing all dynamic job names. '''

        with open(self.tracker_file_path, 'r') as tracker_file:
            tracker_dict = json.load(tracker_file)

        return [(job_name, job_dict['dynamic_job_name']) for job_name, job_dict in tracker_dict.items()]


    def getNumberOfJobsWithStatus(self, status_list: list) -> int:
        """ Return the number of jobs that have a certain status. """

        with open(self.tracker_file_path, 'r') as tracker_file:
            tracker_dict = json.load(tracker_file)

        return len([job_key for job_key, job_value in tracker_dict.items() if job_value['status'] in status_list])-1

