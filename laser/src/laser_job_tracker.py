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
from laser_directory_functions import create_files_dict, move_job_to_main_folder

# from mail_functions import EmailManager
from src.directory_functions import (
    copy, 
    delete,
    get_job_global_paths, 
    global_path_to_main_folder,
    job_name_to_global_path,
    create_new_job_folder,
    job_name_to_job_folder_name,
    copy_job_files)
from convert_functions import job_folder_name_to_job_name
from talk_to_sa import yes_or_no

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

        # self.addFileToWachtrijMaterial(add_job_dict)      

        return add_job_dict
    
    # TODO: copy all files from materials 
    def addFileToWachtrijMaterial(self, job_dict: dict):

        """ Add a file to the WACHTRIJ_MATERIAAL folder. """
        pass

        # for file_key, file_dict in job_dict['laser_files'].items():
        #     material_folder_global_path = os.path.join(gv['JOBS_DIR_HOME'], 'WACHTRIJ_MATERIAAL',
        #                                                 file_dict['material']+'_'+file_dict['thickness'])
        #     if not os.path.exists(material_folder_global_path):
        #         os.mkdir(material_folder_global_path)
        #     if not os.path.exists(os.path.join(material_folder_global_path, 'materiaal_klaar.bat')):
        #         python_to_batch_in_folder(gv, 
        #                     os.path.join(gv['FUNCTIONS_DIR_HOME'], 'materiaal_klaar.py'),
        #                     material_folder_global_path,
        #                     pass_parameter=material_folder_global_path)
                
        #     file_global_path = os.path.join(material_folder_global_path,
        #                                     file_dict['amount']+'x_'+file_key)
            
        #     if os.path.exists(file_dict['file_global_path']):
        #         copy(file_dict['file_global_path'], file_global_path)
        #     else: 
        #         print(f'Warning, could not find {file_dict["file_global_path"]}')
        #         raise ValueError('here ai m')

    def removeJobFromWachtrijMaterial(self, job_name: str, remove_material_folder='true'):
        """ Remove a job from the WACHTRIJ_MATERIAAL folder. """

        job_dict = self.job_name_to_job_dict(job_name)

        for file_key, file_dict in job_dict['laser_files'].items():

            material_dir_global_path = os.path.join(gv['JOBS_DIR_HOME'], 'WACHTRIJ_MATERIAAL',
                        file_dict['material']+'_'+file_dict['thickness'])
        
            if os.path.exists(material_dir_global_path):
                # TODO: remove from tracker if it is at wachtrij, but not in wachtrij_material
                number_of_laser_files_in_wachtrij_material = len([
                    file for file in os.listdir(material_dir_global_path) if file.endswith(gv['ACCEPTED_EXTENSIONS'])])

                if number_of_laser_files_in_wachtrij_material <= 1:
                    delete(gv, material_dir_global_path)
                else: 
                    delete(gv, os.path.join(material_dir_global_path,
                            file_dict['amount']+'x_'+file_key))
                
    def removeFilesFromWachtrijMaterial(self, files_keys: list, call_fake_laser_klaar=False):
        """ Remove multiple files from the WACHTRIJ_MATERIAAL folder. """

        print('in remove files from wachtrij')
        # read job log
        with open(self.tracker_file_path, 'r') as tracker_file:
                job_log_dict = json.load(tracker_file)

        print(f'the file keys {files_keys}')
        
        for file_key in files_keys:
            print(f'now at file key: {file_key}')
            for job_dict in job_log_dict.values():
                if file_key in job_dict['laser_files'].keys():
                   
                    file_dict = job_dict['laser_files'][file_key]
                    file_dict['done'] = True
                
                    # call laser_klaar.bat if all laser files in a laser job are done 
                    if all(file_dict['done'] for file_dict in job_dict['laser_files'].values()):

                        for file_name in job_dict['laser_files'].keys():
                            print(f'    {file_name}')
                        
                        if call_fake_laser_klaar:
                            self.fake_laser_klaar(job_dict['job_name'])

                        
                        # subprocess.run([os.path.join(job_name_to_global_path(gv, job_dict['job_name']),
                        #                 'laser_klaar.bat'), job_dict['job_name']])

                        print('yes I see')
                        
                    else:
                        material_dir_global_path = os.path.join(gv['JOBS_DIR_HOME'], 'WACHTRIJ_MATERIAAL',
                                    file_dict['material']+'_'+file_dict['thickness'])
                        
                        number_of_laser_files_in_wachtrij_material = len([
                            file for file in os.listdir(material_dir_global_path) if file.endswith(gv['ACCEPTED_EXTENSIONS'])])

                        if number_of_laser_files_in_wachtrij_material <= 0:
                            delete(gv, material_dir_global_path)
                        else:      
                            delete(gv, os.path.join(material_dir_global_path,
                                file_dict['amount']+'x_'+file_key))
                        
    def checkHealth(self):
        """ Check and repair system. """

        self.checkTrackerFileHealth()

        print("Checking system health...")

        # check JOBS_DIR_HOME and MAIN_FOLDERS existance
        for folder in ['', *gv['MAIN_FOLDERS'].keys(), *gv['MINOR_FOLDERS'].keys()]:
            folder_global_path = os.path.join(gv['JOBS_DIR_HOME'], folder)

            if not os.path.exists(folder_global_path):
                os.mkdir(folder_global_path)
                print(f'created folder: {folder_global_path}')

        # Get job info from tracker file
        with open(self.tracker_file_path, 'r') as tracker_file:
            tracker_dict = json.load(tracker_file)

        # get job info from file system
        actual_job_global_paths = get_job_global_paths(gv)

        # keep track of the jobs checked
        jobs_checked = {actual_job_name: False for actual_job_name in tracker_dict.keys()}

        for actual_job_global_path in actual_job_global_paths:
            actual_job_main_folder = os.path.basename(os.path.dirname(actual_job_global_path))

            tracker_job_name, tracker_job_dict = self.job_global_path_to_tracker_job_dict(
                tracker_dict, actual_job_global_path)

            if tracker_job_name is None:
                print("SYNCHRONIZE ISSUES! Job Tracker and jobs on File System are out of sync!\n")
                print(f"Job in: {actual_job_global_path} is not in the job tracker")

                if yes_or_no(
                        f"\n{actual_job_global_path} will be removed\nor do you want to add it to the job tracker (Y/n)?"):
                    tracker_job_name = job_folder_name_to_job_name(os.path.basename(actual_job_global_path))

                    # remove all batch files (they will be recreated later)
                    for file in os.listdir(actual_job_global_path):
                        if file.endswith('.bat'):
                            delete(gv['IOBIT_UNLOCKER_PATH'], os.path.join(actual_job_global_path, file))

                    tracker_job_dict = {
                        'job_name': tracker_job_name,
                        'main_folder': global_path_to_main_folder(gv, actual_job_global_path),
                        'created_on_date': str(datetime.now().strftime("%d-%m-%Y")),
                        'laser_files': create_files_dict(tracker_job_name)
                        }
                    
                    tracker_dict[tracker_job_name] = tracker_job_dict

                else:
                    # remove that directory
                    delete(gv['IOBIT_UNLOCKER_PATH'], actual_job_global_path)
                    continue

            # check if the job is in the correct main folder
            if not actual_job_main_folder == tracker_job_dict["main_folder"]:
                print(f"\nWarning: Job Tracker and folders on File System disagree...")
                print(f"Job: {tracker_job_name} location according to:")
                print(f"    Job Tracker: {tracker_job_dict['main_folder']}")
                print(f"    File System: {actual_job_main_folder}\n")
                if yes_or_no(f"Delete job {tracker_job_name} (Y/n)?"):
                    delete(gv['IOBIT_UNLOCKER_PATH'], actual_job_global_path)
                    print(f"Job {tracker_job_name} deleted")
                    continue
                else:
                    print("aborting..")
                    sys.exit(0)
            
            # create batch files for jobs
            if not all([os.path.exists(os.path.join(actual_job_global_path, batch_file)) for batch_file in 
                                       gv['MAIN_FOLDERS'][tracker_job_dict['main_folder']]['allowed_batch_files']]):
                create_batch_files_for_job_folder(gv, tracker_job_dict['job_name'], tracker_job_dict['main_folder'])
                    
            # repair the WACHTRIJ_MATERIAAL folder
            for job_dict in tracker_dict.values():
                if job_dict['main_folder'] == 'WACHTRIJ':
                    for key, file_dict in job_dict['laser_files'].items():
                                        
                        material_folder_global_path = os.path.join(gv['JOBS_DIR_HOME'],
                                                    'WACHTRIJ_MATERIAAL', file_dict['material']+'_'+file_dict['thickness'])

                        # repair WACHTRIJ_MATERIAAL folder
                        if not (os.path.exists(material_folder_global_path) and
                                os.path.exists(os.path.join(material_folder_global_path,
                                file_dict['amount']+'x_'+key)) and
                                os.path.exists(os.path.join(material_folder_global_path, 'materiaal_klaar.bat'))):
                            self.add_file_to_wachtrij_material(job_dict)

            jobs_checked[tracker_job_name] = True

        for tracker_job_name, pj_checked in jobs_checked.items():
            if not pj_checked:
                print(f"Job: {tracker_job_name} not found on file system and removed from job tracker")

                tracker_dict.pop(tracker_job_name)

        with open(self.tracker_file_path, 'w') as tracker_file:
            json.dump(tracker_dict, tracker_file, indent=4)

        self.make_backup()
        print("system healthy :)\n")


    # TODO: call this stuff materiaal_klaar
    def fake_laser_klaar(self, job_name):
        """ Laser is klaar function, to be called from material klaar. """
        job_global_path = job_name_to_global_path(gv,
        job_name, search_in_main_folder='WACHTRIJ')

        # send response mail
        msg_file_paths = list(glob.glob(job_global_path + "/*.msg"))

        if len(msg_file_paths) > 1:
            print(f'Warning! more than one: {len(msg_file_paths)} .msg files detected')
            input('press enter to send response mail...')

        if len(msg_file_paths) > 0:
            pass
            # email_manager = EmailManager()
            # email_manager.reply_to_email_from_file_using_template(gv,
            #                                         msg_file_paths[0],
            #                                         "FINISHED_MAIL_TEMPLATE",
            #                                         {},
            #                                         popup_reply=False)
        else:
            print(f'folder: {job_global_path} does not contain any .msg files,'\
                    f'no response mail can be send')
        
        
        # find source directory
        source_job_folder_global_path = job_name_to_global_path(gv, job_name, "WACHTRIJ")

        # create the target folder
        new_job_folder_name = job_name_to_job_folder_name(gv, job_name, "WACHTRIJ")
        target_job_folder_global_path = create_new_job_folder(
                gv, job_name, new_job_folder_name, 'VERWERKT', "WACHTRIJ")

        # create new batch files
        create_batch_files_for_job_folder(gv, target_job_folder_global_path, 'VERWERKT')

        # copy files
        copy_job_files(target_job_folder_global_path, source_job_folder_global_path, ['.bat'])

        delete(gv, source_job_folder_global_path)

    def getWachtrijMaterialsFolderNames(self):
        ''' return back all folder names for the materials and thickness in the wachtrij. '''
        return []

# def main():

#     job_name = 'test_jn'
#     file_name = '_attachment_1' 

#     files_dict = {}
#     files_dict[job_name + file_name] = {
#                         'file_name': file_name,
#                         'file_global_path': '/text/somewhre/',
#                         'material': 'steel',
#                         'thickness': '3cm',
#                         'amount': '3',
#                         'done': False}

#     LaserJobTracker().addJob(job_name, files_dict)


# if __name__ == '__main__':
#     main()
