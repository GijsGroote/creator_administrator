import csv
import os
from global_variables import CSV_FILE_PATH
from directory_functions import get_print_job_global_paths, get_print_job_folder_names
from collections import defaultdict
import shutil
from datetime import datetime

class JobTrackerCSV:
    """
    A class to track email jobs in a CSV file
    saves the following fields:
    - print_job_name
    - sender
    - subject
    - date_sent
    - current_state"
        - "AFGEKEURD"
        - "WACHTRIJ"
        - "AAN HET PRINTEN"
        - "VERWERKT"
        - "GESCLICED"
    - split_job
    """
    def __init__(self):
        self.csv_filename = CSV_FILE_PATH
        self.fieldnames = ['print_job_name', 'sender', 'subject', 'date_sent', 'current_state', 'split_job']

        # Create the CSV file if it doesn't exist
        if not os.path.exists(self.csv_filename):
            with open(self.csv_filename, 'w', newline='') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames)
                writer.writeheader()
        
        self.check_header()

    def check_header(self):
        """
        Check if the header in the CSV file matches the expected header.
        If not, replace it with the correct one.
        """
        with open(self.csv_filename, 'r', newline='') as csv_file:
            reader = csv.reader(csv_file)
            existing_header = next(reader, None)  # Read the existing header, if any.

            if existing_header != self.fieldnames:
                print("Header in the CSV file is incorrect. Replacing with the correct header.")
                with open(self.csv_filename, 'w', newline='') as new_csv_file:
                    writer = csv.DictWriter(new_csv_file, fieldnames=self.fieldnames)
                    writer.writeheader()
    
    def add_job(self, print_job_name: str, sender: str, subject: str, date_sent: str, current_state: str, split_job="False"):
        """Adds a job to the CSV file"""
        with open(self.csv_filename, 'a', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames)
            writer.writerow({
                'print_job_name': print_job_name,
                'sender': sender,
                'subject': subject,
                'date_sent': date_sent,
                'current_state': current_state,
                'split_job': split_job
            })

    def get_jobs_from_sender(self, sender):
        """returns a list of jobs from a specific sender"""
        with open(self.csv_filename, 'r', newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            jobs = []
            for row in reader:
                if row['sender'] == sender:
                    jobs.append(row)
            return jobs

    def get_job_by_print_job_name(self, print_job_name):
        with open(self.csv_filename, 'r', newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                if row['print_job_name'] == print_job_name:
                    return row
    
    def get_job_from_folder_name(self, folder_name):
        """get a job from the folder name"""
        with open(self.csv_filename, 'r', newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                job_name = row['print_job_name']
                if folder_name.endswith(job_name):
                    return row
            else:
                return None

    def update_job_status(self, print_job_name, new_status):
        with open(self.csv_filename, 'r', newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            rows = list(reader)
            for row in rows:
                if row['print_job_name'] == print_job_name:
                    row['current_state'] = new_status
                    break
        with open(self.csv_filename, 'w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    
    def get_job_status(self, print_job_name):
        with open(self.csv_filename, 'r', newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                if row['print_job_name'] == print_job_name:
                    return row['current_state']
    
    def split_job(self, print_job_name):
        """set split_job to True"""
        with open(self.csv_filename, 'r', newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            rows = list(reader)
            for row in rows:
                if row['print_job_name'] == print_job_name:
                    row['split_job'] = "True"
                    break
        with open(self.csv_filename, 'w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    
    def merge_job(self, print_job_name):
        """set split_job to False"""
        with open(self.csv_filename, 'r', newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            rows = list(reader)
            for row in rows:
                if row['print_job_name'] == print_job_name:
                    row['split_job'] = "False"
                    break
        with open(self.csv_filename, 'w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    
    def job_is_to_old(self, print_job_name, number_of_days):
        """check if the job is older then a certain date"""
        job = self.get_job_by_print_job_name(print_job_name)
        date_job = job["date_sent"]
        date_object = datetime.strptime(date_job, "%Y-%m-%d")
        current_date = datetime.now()
        date_difference = current_date - date_object
        return date_difference.days > number_of_days
        
    
    def _fill_csv(self):
        """developer function so the csv file is filled with data that matches current workflow"""
        pass    
    
    #TODO: Maybe some useful functions to add:
    
    def check_if_jobs_same_sender_in_wachtrij(self, sender):
        """checks if the sender has any jobs in the wachtrij so they can be merged"""
        pass
    
    def clean_csv_by_date(self, date):
        """removes all jobs before a certain date"""
        pass

def check_health_folders():
    """Check if folders are in the right place and if duplicates exist, if so, delete them"""
    # Get all the folders in the print directory
    all_job_folders = get_print_job_global_paths()
    
    #create dictionary with folder name as key and list of folders as value
    folder_dict = defaultdict(list)

    #make list of duplicate end folders
    for job_folder in all_job_folders:
        folder_name = os.path.basename(job_folder)
        folder_dict[folder_name].append(job_folder)
    
    # open csv log
    csv_log = JobTrackerCSV()
    
    # loop over all folder names and check if the corresponding job_name is in the csv log
    for folder_name in folder_dict.keys():
        job = csv_log.get_job_from_folder_name(folder_name) # returns None if job is not in csv log, otherwise return job as dictionary
        
        if job is None:     # job does not exist in csv log and is deleted
            print(f"Folder {folder_name} is not in the csv log, delete it")
            for folder in folder_dict[folder_name]:
                shutil.rmtree(folder)
                print(f"deleted folder: {folder}")
        
        elif job['split_job'] == "True":  # job is split and is deleted
            print(f"Folder {folder_name} is split up, skipping the job")
            continue
        
        elif len(folder_dict[folder_name]) > 1: # if multiple folders exist with the same name, remove the ones with the wrong job status
            print(f"Folder {folder_name} has {len(folder_dict[folder_name])} duplicates, delete the wrong ones")
            job_status = csv_log.get_job_status(job['print_job_name'])
            print(f"Job status is {job_status}, removing all other folders")
            
            job_status_match = False
            for folder in folder_dict[folder_name]:
                if job_status in folder:
                    job_status_match = True
                else:
                    shutil.rmtree(folder)
                    print(f"deleted folder: {folder}")
            
            if not job_status_match: # if no folder with the right job status is found, remove all folders and make a warning
                print(f"Warning! No folder with job status {job_status} found, removed all folders")
                
        else:
            if job["current_state"] in ["AFGEKEURD", "VERWERKT"]: # if the job is in the right folder, but the job is to old, remove it
                if csv_log.job_is_to_old(job['print_job_name'], 14):
                    print(f"Folder {folder_name} is to old, delete it")
                    shutil.rmtree(folder_dict[folder_name][0])
                    print(f"deleted folder: {folder_dict[folder_name][0]}")
            else:
                print(f"Folder {folder_name} is in the csv log, keep it")
            
    
if __name__ == '__main__':
    # check_health_folders()