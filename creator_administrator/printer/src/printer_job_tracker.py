import os
from datetime import datetime

from PyQt6.QtWidgets import QWidget

from global_variables import gv

from src.job_tracker import JobTracker


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
        """ Synchonize job tracker and files on file system. """

        self.checkTrackerFileHealth()

        # create jobs_folder if it does not yet exist 
        if not os.path.exists(gv['JOBS_DIR_HOME']):
            os.mkdir(gv['JOBS_DIR_HOME'])

        self.deleteOldJobs()

        self.deleteNonExitentJobsFromTrackerFile()
        self.deleteNonExitentFilesFromTrackerFile()

        # import here, importing at begin of file creates a circular import error
        from printer_qdialog import CreatePrintJobsFromFileSystemQDialog

        self.addNewJobstoTrackerFile(CreatePrintJobsFromFileSystemQDialog)
        self.addNewFilestoTrackerFile(CreatePrintJobsFromFileSystemQDialog)

        self.makeBackup()



    
