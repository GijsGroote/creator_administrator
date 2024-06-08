import json
import os
from datetime import datetime

from PyQt6.QtWidgets import QWidget

from src.job_tracker import JobTracker

from laser.src.global_variables import gv

class LaserJobTracker(JobTracker):
    '''
    Before changing files on file system, change the job_log.json

    use the check_health function to check the file system health based on the job_log.json file
    '''

    def __init__(self, parent: QWidget):
        super().__init__(parent, gv)

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
        ''' Add a job to the tracker. '''

        self.readTrackerFile()

        if job_dict is not None: 

            # update existing job
            assert job_name is not None, 'updating a job dict, job_name cannot be None'
            assert job_name in self.tracker_dict, f'could not find {job_name} in tracker_dict'
            add_job_dict = job_dict

        else:

            # create new job
            job_name = self.makeJobNameUnique(job_name)

            add_job_dict = {'job_name': job_name,
                            'sender_name': sender_name,
                            'job_folder_global_path': job_folder_global_path,
                            'dynamic_job_name': str(datetime.now().strftime("%d-%m"))+'_'+job_name,
                            'status': status,
                            'created_on_date': str(datetime.now().strftime("%d-%m-%Y")),
                            'make_files': make_files}

            if sender_mail_adress is not None:
                add_job_dict['sender_mail_adress'] = str(sender_mail_adress)
            if sender_mail_receive_time is not None:
                add_job_dict['sender_mail_receive_time'] = str(sender_mail_receive_time)

        self.tracker_dict[job_name] = add_job_dict

        self.writeTrackerFile()

    def getExistingMaterials(self) -> set:
        ''' Return all materials that exist in the jobs with a wachtrij status. '''
        with open(self.tracker_file_path, 'r' ) as tracker_file:
            tracker_dict = json.load(tracker_file)

        materials = set()
        for job_dict in tracker_dict.values():
            if job_dict['status'] == 'WACHTRIJ':
                for laser_file_dict in job_dict['make_files'].values():
                    materials.add(laser_file_dict['material'])
                    
        return materials

    def getMaterialAndThicknessList(self) -> list:
        ''' Return all materials and thickness with status WACHTRIJ. '''

        with open(self.tracker_file_path, 'r' ) as tracker_file:
            tracker_dict = json.load(tracker_file)

        materials_and_thickness_set = set()
        for job_dict in tracker_dict.values():
            if job_dict['status'] == 'WACHTRIJ':
                for laser_file_dict in job_dict['make_files'].values():
                    if not laser_file_dict['done']:
                        materials_and_thickness_set.add(
                                laser_file_dict['material']+'_'+laser_file_dict['thickness']+'mm')
                    
        return list(materials_and_thickness_set)

    def getLaserFilesWithMaterialThicknessInfo(self, material: str, thickness: str) -> list:
        ''' Return all names, global paths and indication if they are done
        of material with thickness and status WACHTRIJ. '''

        with open(self.tracker_file_path, 'r' ) as tracker_file:
            tracker_dict = json.load(tracker_file)

        laser_file_info_list = []
        for job_dict in tracker_dict.values():
            if job_dict['status'] == 'WACHTRIJ':
                for key, laser_file_dict in job_dict['make_files'].items():
                    if laser_file_dict['material'] == material and laser_file_dict['thickness'] == thickness:
                        laser_file_info_list.append((key,
                                                    laser_file_dict['file_global_path'],
                                                    laser_file_dict['done']))
        return laser_file_info_list 


    def checkHealth(self):
        ''' Synchonize job tracker and files on file system. '''

        self.system_healthy = True

        self.checkTrackerFileHealth()

        # create jobs_folder if it does not yet exist 
        if not os.path.exists(gv['JOBS_DIR_HOME']):
            os.mkdir(gv['JOBS_DIR_HOME'])

        self.deleteOldJobs()

        self.deleteNonExitentJobsFromTrackerFile()
        self.deleteNonExitentFilesFromTrackerFile()

        # import here, importing at begin of file creates a circular import error
        # pylint: disable=import-outside-toplevel
        from laser_qdialog import CreateLaserJobsFromFileSystemQDialog

        self.addNewJobstoTrackerFile(CreateLaserJobsFromFileSystemQDialog)
        self.addNewFilestoTrackerFile(CreateLaserJobsFromFileSystemQDialog)

        self.makeBackup()
