import os
import re
from datetime import datetime

from PyQt6.QtWidgets import QWidget

from global_variables import gv


from src.directory_functions import delete_item
from src.job_tracker import JobTracker
from src.qmessagebox import TimedMessage, YesOrNoMessageBox, WarningQMessageBox
from src.mail_manager import MailManager


class PrintJobTracker(JobTracker):
    """
    Before changing files on file system, change the job_log.json

    use the check_health function to check the file system health based on the job_log.json file
    """

    def __init__(self, parent: QWidget):
        super().__init__(parent, gv)
        self.job_keys.append('split_job')

        self.checkTrackerFileHealth()

    def addJob(self,
               job_name: str,
               job_folder_global_path: str,
               make_files: dict,
               sender_name=None,
               sender_mail_adress=None,
               sender_mail_receive_time=None,
               status='WACHTRIJ',
               job_dict=None) -> dict:
        """ Add a job to the tracker. """

        self.readTrackerFile()

        if job_dict is not None:
            add_job_dict = job_dict
        else:

            job_name = self.makeJobNameUnique(job_name)

            add_job_dict = {'job_name': job_name,
                            'job_folder_global_path': job_folder_global_path,
                            'dynamic_job_name': str(datetime.now().strftime("%d-%m"))+'_'+job_name,
                            'status': status,
                            'created_on_date': str(datetime.now().strftime("%d-%m-%Y")),
                            'make_files': make_files,
                            'split_job': False}

            if sender_name is not None:
                add_job_dict['sender_name'] = sender_name
            if sender_mail_adress is not None:
                add_job_dict['sender_mail_adress'] = sender_mail_adress
            if sender_mail_receive_time is not None:
                add_job_dict['sender_mail_receive_time'] = sender_mail_receive_time

        self.tracker_dict[job_name] = add_job_dict

        self.writeTrackerFile()

        return add_job_dict

    def getExistingMaterials(self) -> set:
        ''' Return all materials that exist in the jobs with a wachtrij status. '''
        self.readTrackerFile()

        materials = set()
        for job_dict in self.tracker_dict.values():
            if job_dict['status'] == 'WACHTRIJ':
                for print_file_dict in job_dict['make_files'].values():
                    materials.add(print_file_dict['material'])
                    
        return materials

    def checkHealth(self):
        """ Check and repair system. """

        self.checkTrackerFileHealth()

        # create jobs_folder if it does not yet exist 
        if not os.path.exists(gv['JOBS_DIR_HOME']):
            os.mkdir(gv['JOBS_DIR_HOME'])

        self.deleteOldJobs()

        self.deleteNonExitentJobsFromTrackerFile()
        self.deleteNonExitentFilesFromTrackerFile()

        self.addNewJobstoTrackerFile()
        self.addNewFilestoTrackerFile()

        self.makeBackup()


    def deleteOldJobs(self):

        self.readTrackerFile()

        # remove old jobs
        n_old_jobs = 0
        for job_key, job_dict in self.tracker_dict.items():
            if self.isJobOld(job_dict['created_on_date']) and job_dict['status'] != 'WACHTRIJ':
                n_old_jobs += 1
                self.deleteJob(job_key)

        if n_old_jobs > 0:
            TimedMessage(gv=gv, parent=self.parent, text=f'Removed {str(n_old_jobs)} old jobs')

        self.writeTrackerFile()


    def deleteNonExitentJobsFromTrackerFile(self):
        self.readTrackerFile()

        # find non existent jobs
        non_existent_job_keys = []
        for job_key, job_dict in self.tracker_dict.items():
            if not os.path.exists(job_dict['job_folder_global_path']):
                non_existent_job_keys.append(job_key)

        # delete non existent jobs from tracker file
        [self.tracker_dict.pop(key) for key in non_existent_job_keys]

        self.writeTrackerFile()


    def deleteNonExitentFilesFromTrackerFile(self):
        self.readTrackerFile()

        for job_dict in self.tracker_dict.values():
            temp_remove_keys = []
            # find non existent make files
            for file_key, file_dict in job_dict['make_files'].items():
                if not os.path.exists(file_dict['file_global_path']):
                    temp_remove_keys.append(file_key)
            # delete non existent make files from tracker file
            [job_dict['make_files'].pop(key) for key in temp_remove_keys]

        self.writeTrackerFile()


    def addNewJobstoTrackerFile(self):
        ''' Add a job that is on the file system to the tracker file. '''

        self.readTrackerFile()

        # find job on file system that are not in the tracker file
        job_folder_not_in_tracker_global_paths = []
        for job_folder_global_path in os.listdir(gv['JOBS_DIR_HOME']):
            if not any([job_dict['job_folder_global_path'] == os.path.join(gv['JOBS_DIR_HOME'], job_folder_global_path) for job_dict in self.tracker_dict.values()]):
                job_folder_not_in_tracker_global_paths.append(os.path.join(gv['JOBS_DIR_HOME'], job_folder_global_path))

        if len(job_folder_not_in_tracker_global_paths) > 0:

            # remove date from the job folder names
            job_names_str = ''
            job_names_no_dates = []
            for job_folder_global_path in job_folder_not_in_tracker_global_paths:
                job_names_str += os.path.basename(job_folder_global_path) + '\n'
                match = re.search(r'^\d{2}-\d{2}_(.*)$', os.path.basename(job_folder_global_path))

                if match:
                    job_names_no_dates.append(match.group(1))
                else:
                    job_names_no_dates.append(os.path.basename(job_folder_global_path))

            if len(job_folder_not_in_tracker_global_paths) <= 1:
               is_or_are = 'is'
               folder_s = 'folder'
            else:
               is_or_are = 'are'
               folder_s = 'folders'

            if YesOrNoMessageBox(parent=self.parent,
                              text=f'OH NO, SYNCHRONIZE ISSUES!\nThere {is_or_are} {len(job_folder_not_in_tracker_global_paths)} print job '\
                                  f'{folder_s} that are not in the Job Tracker.\n\nHow do you want to to sync: \n{job_names_str}',
                              yes_button_text='Add files to Job Tracker',
                             no_button_text='Remove files from File System').answer():

                file_global_path_list = []
                job_dict_list = []

                for job_name, job_folder_global_path in zip(job_names_no_dates, job_folder_not_in_tracker_global_paths):

                    file_global_path_list.append(os.listdir(job_folder_global_path))

                    job_dict = {'job_name': job_name,
                                'job_folder_global_path': job_folder_global_path,
                                'make_files': {},
                                'status': 'WACHTRIJ',
                                'created_on_date': str(datetime.now().strftime("%d-%m-%Y")),
                                'dynamic_job_name': str(datetime.now().strftime("%d-%m"))+'_'+job_name}

                    mail_item_list = [os.path.join(job_folder_global_path, file) for file in os.listdir(job_folder_global_path) if file.endswith(('.eml', '.msg'))]
                    if len(mail_item_list) > 0:
                        job_dict['sender_name'] = MailManager(gv).getSenderName(mail_item_list[0])
                        job_dict['sender_mail_adress'] = MailManager(gv).getEmailAddress(mail_item_list[0])
                        job_dict['sender_mail_receive_time'] = MailManager(gv).getSenderMailReceiveTime(mail_item_list[0])

                    job_dict_list.append(job_dict)

                from printer_qdialog import CreatePrintJobsFromFileSystemQDialog
                self.writeTrackerFile()

                CreatePrintJobsFromFileSystemQDialog(self.parent,
                                          job_names_no_dates,
                                          file_global_path_list,
                                          job_dict_list=job_dict_list).exec()

                TimedMessage(parent=self.parent, gv=gv, text=f'Added {len(job_folder_not_in_tracker_global_paths)} jobs to the Job Tracker.')

            else:
                for job_folder_global_path in job_folder_not_in_tracker_global_paths:
                    delete_item(self.parent, job_folder_global_path)
                TimedMessage(parent=self.parent, gv=gv, text=f'Deleted {len(job_folder_not_in_tracker_global_paths)} job folders from File System.')


    def addNewFilestoTrackerFile(self):
        self.readTrackerFile()

        for job_folder_name in os.listdir(gv['JOBS_DIR_HOME']):
            job_folder_global_path = os.path.join(gv['JOBS_DIR_HOME'], job_folder_name)

            job_key, job_dict = self.jobGlobalPathToTrackerJobDict(self.tracker_dict, job_folder_global_path)

            # check if jobs are incomplete and must be repaired
            if not self.IsJobDictAndFileSystemInSync(job_dict, job_folder_global_path):
                self.addMissingFilesToJobDict(job_dict, job_folder_global_path)

        self.writeTrackerFile()


    def IsJobDictAndFileSystemInSync(self, job_dict, job_folder_global_path):
        ''' Check if all files are in both the tracker and the file system. '''

        file_system_print_file_names = [file_name for file_name in os.listdir(job_folder_global_path) if file_name.lower().endswith(gv['ACCEPTED_EXTENSIONS'])]
        tracker_print_file_names = [os.path.basename(print_file_dict['file_global_path']) for print_file_dict in job_dict['make_files'].values()]

        if len(file_system_print_file_names) != len(tracker_print_file_names):
            return False
        for i in range(len(file_system_print_file_names)):
            if file_system_print_file_names[i] != tracker_print_file_names[i]:
                return False
        return True

    
    def addMissingFilesToJobDict(self, job_dict: dict, job_folder_global_path: str):
        ''' Sychronize job dict based on file system. '''

        valid_file_names = [file_name for file_name in os.listdir(job_folder_global_path) if file_name.lower().endswith(gv['ACCEPTED_EXTENSIONS'])]

        new_make_files = []
        for file in valid_file_names:
            if not any([os.path.basename(print_file_dict['file_global_path'])==file for print_file_dict in job_dict['make_files'].values()]):
                new_make_files.append(os.path.join(job_folder_global_path, file))

        # add/delete new files
        if len(new_make_files) > 0:

            if len(new_make_files)==1:
                file_str = 'File'
                is_are_str = 'is'
            else:
                file_str = 'Files'
                is_are_str = 'are'

            yes_or_no_text = f'New {file_str} detected for Job {job_dict["job_name"]}:\n'
            for file in new_make_files:
                yes_or_no_text += f'{os.path.basename(file)}\n'

            yes_or_no_text += f'\nWhat do you want with these {file_str}?'

            yes_or_no = YesOrNoMessageBox(parent=self.parent,
                                          text=yes_or_no_text,
                                          yes_button_text='Add to Job Tracker',
                                          no_button_text='Remove from File System')
            if yes_or_no.answer():

                from printer_qdialog import CreatePrintJobsFromFileSystemQDialog
                CreatePrintJobsFromFileSystemQDialog(self.parent,
                                                [job_dict['job_name']],
                                                [new_make_files],
                                                update_existing_job=True,
                                                job_dict_list=[job_dict]).exec()

            else:
                for file in new_make_files:
                    delete_item(self.parent, os.path.join(job_folder_global_path, file))
                TimedMessage(parent=self.parent, gv=gv, text=f'Removed {len(new_make_files)} {file_str} from File System')
