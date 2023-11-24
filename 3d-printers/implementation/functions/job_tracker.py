"""
Track jobs to repair system if there is a system shutdown at any moment.
"""

import json
import shutil
import os
import sys
from typing import Tuple
from datetime import datetime

from global_variables import gv

from src.batch import python_to_batch, create_batch_files_for_job_folder
from src.directory_functions import get_job_global_paths
from src.convert_functions import job_folder_name_to_job_name
from src.talk_to_sa import yes_or_no


class JobTracker:
    """
    Before a print job is modified, the modification is written to the 
    job tracker file at TRACKER_FILE_PATH. Then the print job is modified.

    Checking the health of the system does the following:
    - create a backup of the curretn csv file
    - test if every print job isunique, if not remove one
    - does every print job contain the correct .bat. if not, create them
    - remove old print jobs
    """

    def __init__(self):

        self.job_keys = ['print_job_name', 'main_folder', 'created_on_date', 'split_job']
        self.tracker_file_path = gv['TRACKER_FILE_PATH']
        self.tracker_backup_file_path = gv['TRACKER_FILE_PATH'].replace("3D_print_job_log.json",
                                                                  "3D_print_job_log_backup.json")

        self.check_tracker_file_health()

    def check_tracker_file_health(self):
        # Create the tracker file if it doesn't exist
        if not os.path.exists(self.tracker_file_path):
            print(f"tracker file was not detected at: {self.tracker_file_path}")
            self.create_tracker_file()

        try:
            with open(self.tracker_file_path, 'r') as tracker_file:
                tracker_dict = json.load(tracker_file)
        except Exception as e:
            print(f"Cannot read tracker file at: {self.tracker_file_path}")
            print(f"MANUALLY REPAIR TRACKER FILE!")
            if os.path.isfile(self.tracker_backup_file_path):
                print("\nTip: there exists a backup file :)")
                print(f"backup file location: {self.tracker_backup_file_path}")
            sys.exit(0)

    def create_tracker_file(self):
        """ Create the csv file that tracks jobs. """
        if os.path.exists(self.tracker_backup_file_path):
            if yes_or_no(f"Backup file detected at: {self.tracker_backup_file_path}, do you want to restore it (Y/n)?"):
                os.rename(self.tracker_backup_file_path, self.tracker_file_path)
                print("Backup restored!")
                return

        with open(self.tracker_file_path, 'w') as tracker_file:
            json.dump(dict(), tracker_file, indent=4)

        print(f"{self.tracker_file_path} created!\n")

    def check_health(self):
        """ Check and repair 3D print jobs. """

        self.check_tracker_file_health()

        print("Checking system health...")

        # Get print job info from tracker file
        with open(self.tracker_file_path, 'r') as tracker_file:
            tracker_dict = json.load(tracker_file)

        # get print job info from file system
        actual_job_global_paths = get_job_global_paths(gv)

        # keep track of the print jobs checked
        print_jobs_checked = {actual_print_job_name: False for actual_print_job_name in tracker_dict.keys()}

        for actual_job_global_path in actual_job_global_paths:
            actual_job_main_folder = os.path.basename(os.path.dirname(actual_job_global_path))

            tracker_job_name, tracker_job_dict = self.job_global_path_to_tracker_job_dict(tracker_dict,
                                                                                          actual_job_global_path)

            if tracker_job_name is None:
                print("SYNCHRONIZE ISSUES! Print Job Tracker and print jobs on File System are out of sync!\n")
                print(f"print job in: {actual_job_global_path} is not in the job tracker")

                if yes_or_no(
                        f"\n{actual_job_global_path} will be removed\nor do you want to add it to the print job tracker (Y/n)?"):
                    tracker_job_name = job_folder_name_to_job_name(os.path.basename(actual_job_global_path))

                    # remove all batch files (they will be recreated later)
                    for file in os.listdir(actual_job_global_path):
                        if file.endswith('.bat'):
                            os.remove(os.path.join(actual_job_global_path, file))

                    tracker_job_dict = {'print_job_name': tracker_job_name,
                                        'main_folder': actual_job_main_folder,
                                        'created_on_date': str(datetime.now().strftime("%d-%m-%Y")),
                                        'split_job': False}
                    tracker_dict[tracker_job_name] = tracker_job_dict

                else:
                    # remove that directory
                    shutil.rmtree(actual_job_global_path)
                    continue

            # check if the print job is in the correct main folder
            if not actual_job_main_folder == tracker_job_dict["main_folder"]:
                if not (tracker_job_dict["split_job"] and
                        actual_job_main_folder in ["GESLICED", "AAN_HET_PRINTEN"] and
                        tracker_job_dict["main_folder"] in ["GESLICED", "AAN_HET_PRINTEN"]):
                    print(f"\nWarning: Print Job Tracker and folders on File System disagree...")
                    print(f"Print Job: {tracker_job_name} location according to:")
                    print(f"    Print Job Tracker: {tracker_job_dict['main_folder']}")
                    print(f"    File System: {actual_job_main_folder}\n")
                    if yes_or_no(f"Delete print job {tracker_job_name} (Y/n)?"):
                        shutil.rmtree(actual_job_global_path)
                        print(f"print job {tracker_job_name} deleted")
                        continue
                    else:
                        print("aborting..")
                        sys.exit(0)

            if not all([os.path.exists(os.path.join(actual_job_global_path, batch_file)) for batch_file in 
                                       gv['MAIN_FOLDERS'][tracker_job_dict['main_folder']]['allowed_batch_files']]):
                create_batch_files_for_job_folder(gv, tracker_job_dict['print_job_name'], tracker_job_dict['main_folder'])

            if tracker_job_dict['split_job']:
                if not (os.path.exists(os.path.join(actual_job_global_path.replace('AAN_HET_PRINTEN', 'GESLICED'), 'afgekeurd.bat'))
                    or os.path.exists(os.path.join(actual_job_global_path.replace('AAN_HET_PRINTEN', 'GESLICED'), 'printer_aangezet.bat'))):
                    create_batch_files_for_job_folder(gv, tracker_job_dict['print_job_name'], 'GESLICED')
                    
                            
            print_jobs_checked[tracker_job_name] = True

        for tracker_job_name, pj_checked in print_jobs_checked.items():
            if not pj_checked:
                print(f"print job: {tracker_job_name} not found on file system and removed from print job tracker")

                tracker_dict.pop(tracker_job_name)

        with open(self.tracker_file_path, 'w') as tracker_file:
            json.dump(tracker_dict, tracker_file, indent=4)

        self.make_backup()
        print("system healthy :)\n")

    def job_global_path_to_tracker_job_dict(self, tracker_dict: dict, print_job_folder_name: str) -> Tuple[str, dict]:
        """ If exists, return job name and data from tracker dictionary
        corresponding to the print job with name print_job_folder_name. """
        for tracker_job_name, tracker_job_dict in tracker_dict.items():
            if print_job_folder_name.endswith(tracker_job_name):
                return tracker_job_name, tracker_job_dict
        return None, None

    def is_job_old(self, created_on_date: str) -> bool:
        """ Check if the job is old. """
        created_on_date_object = datetime.strptime(created_on_date, "%d-%m-%Y")
        current_date_object = datetime.now()
        date_difference = current_date_object - created_on_date_object
        return date_difference.days > gv['DAYS_TO_KEEP_JOBS']

    def make_backup(self):
        """ Make a backup of the tracker file. """
        try:
            shutil.copy(self.tracker_file_path, self.tracker_backup_file_path)
        except FileExistsError:
            os.remove(self.tracker_backup_file_path)
            shutil.copy(self.tracker_file_path, self.tracker_backup_file_path)

    def add_job(self, print_job_name: str, main_folder: str) -> dict:
        """ Add a job to the tracker. """

        with open(self.tracker_file_path, 'r') as tracker_file:
            tracker_dict = json.load(tracker_file)

        add_job_dict = {'print_job_name': print_job_name,
                        'main_folder': main_folder,
                        'created_on_date': str(datetime.now().strftime("%d-%m-%Y")),
                        'split_job': False}

        tracker_dict[print_job_name] = add_job_dict

        with open(self.tracker_file_path, 'w') as tracker_file:
            json.dump(tracker_dict, tracker_file, indent=4)

        return add_job_dict

    def update_job_main_folder(self, print_job_name, new_main_folder):
        """ Update the main folder in the tracker. """
        with open(self.tracker_file_path, 'r') as tracker_file:
            tracker_dict = json.load(tracker_file)

        tracker_dict[print_job_name]["main_folder"] = new_main_folder

        with open(self.tracker_file_path, 'w') as tracker_file:
            json.dump(tracker_dict, tracker_file, indent=4)

    def set_split_job_to(self, print_job_name, splitted: bool):
        """ Set split_job to True. """
        with open(self.tracker_file_path, 'r') as tracker_file:
            tracker_dict = json.load(tracker_file)

        tracker_dict[print_job_name]["split_job"] = splitted

        with open(self.tracker_file_path, 'w') as tracker_file:
            json.dump(tracker_dict, tracker_file, indent=4)