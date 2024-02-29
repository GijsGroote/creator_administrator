import json
import os
import re
from datetime import datetime

from PyQt6.QtWidgets import QDialog
from PyQt6.uic import loadUi

from src.directory_functions import delete_item
from src.job_tracker import JobTracker
from src.qmessagebox import TimedMessage, YesOrNoMessageBox, WarningQMessageBox

from global_variables import gv
from laser_validate import validate_material_info

class LaserJobTracker(JobTracker):
    """
    Before changing files on file system, change the job_log.json

    use the check_health function to check the file system health based on the job_log.json file
    """

    def __init__(self, parent):
        super().__init__(parent, gv)

        self.checkTrackerFileHealth()

        self.job_keys.append(['laserfiles'])

    def addJob(self,
               job_name: str,
               sender_name,
               job_folder_global_path: str,
               files_dict: dict,
               sender_mail_adress=None,
               sender_mail_receive_time=None,
               status='WACHTRIJ') -> dict:
        """ Add a job to the tracker. """

        with open(self.tracker_file_path, 'r' ) as tracker_file:
            tracker_dict = json.load(tracker_file)

        job_name = self.makeJobNameUnique(job_name)

        add_job_dict = {'job_name': job_name,
                        'sender_name': sender_name,
                        'job_folder_global_path': job_folder_global_path,
                        'dynamic_job_name': str(datetime.now().strftime("%d-%m"))+'_'+job_name,
                        'status': status,
                        'created_on_date': str(datetime.now().strftime("%d-%m-%Y")),
                        'laser_files': files_dict}

        if sender_mail_adress is not None:
            add_job_dict['sender_mail_adress'] = str(sender_mail_adress)
        if sender_mail_receive_time is not None:
            add_job_dict['sender_mail_receive_time'] = str(sender_mail_receive_time)

        tracker_dict[job_name] = add_job_dict

        with open(self.tracker_file_path, 'w' ) as tracker_file:
            json.dump(tracker_dict, tracker_file, indent=4)

        return add_job_dict
    
    def deleteJob(self, job_name: str):
        """ Delete a job from the job tracker. """

        with open(self.tracker_file_path, 'r' ) as tracker_file:
            tracker_dict = json.load(tracker_file)

        deleted_job_dict = tracker_dict.pop(job_name)
        delete_item(self.parent(), deleted_job_dict['job_folder_global_path'])
        
        with open(self.tracker_file_path, 'w' ) as tracker_file:
            json.dump(tracker_dict, tracker_file, indent=4)


    def updateJobStatus(self, job_name: str, new_job_status: str):
        ''' Update status of a job. '''

        with open(self.tracker_file_path, 'r' ) as tracker_file:
            tracker_dict = json.load(tracker_file)

        tracker_dict[job_name]['status'] = new_job_status

        with open(self.tracker_file_path, 'w' ) as tracker_file:
            json.dump(tracker_dict, tracker_file, indent=4)

    def markAllFilesAsDone(self, job_name: str, done: bool):
        ''' Update all laser files to done. '''
        assert job_name is not None, 'Job name is None'
        assert isinstance(done, bool), 'done is not a boolean'

        with open(self.tracker_file_path, 'r' ) as tracker_file:
            tracker_dict = json.load(tracker_file)

        for file_dict in tracker_dict[job_name]['laser_files'].values():
            file_dict['done'] = done

        with open(self.tracker_file_path, 'w' ) as tracker_file:
            json.dump(tracker_dict, tracker_file, indent=4)

    def markLaserFileAsDone(self, job_name: str, file_global_path: str, done: bool):
        ''' Update laser file to done. '''
        assert job_name is not None, 'Job name is None'
        assert isinstance(done, bool), 'done is not a boolean'

        with open(self.tracker_file_path, 'r' ) as tracker_file:
            tracker_dict = json.load(tracker_file)

        for file_dict in tracker_dict[job_name]['laser_files'].values():
            if file_dict['file_global_path']==file_global_path:
                file_dict['done'] = done

        with open(self.tracker_file_path, 'w' ) as tracker_file:
            json.dump(tracker_dict, tracker_file, indent=4)


    def getJobDict(self, job_name: str) -> dict:
        ''' Return the job dict from a job name. '''
        
        with open(self.tracker_file_path, 'r' ) as tracker_file:
            tracker_file = json.load(tracker_file)

        if job_name in tracker_file:
            return tracker_file[job_name]
        return None

    def getJobFolderGlobalPathFromJobName(self, job_name: str) -> str:
        ''' Return the job folder global path from the job name. '''
        with open(self.tracker_file_path, 'r' ) as tracker_file:
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
        with open(self.tracker_file_path, 'r' ) as tracker_file:
            tracker_dict = json.load(tracker_file)

        # remove old jobs
        n_old_jobs = 0
        for job_key, job_dict in tracker_dict.items():
            if self.isJobOld(job_dict['created_on_date']) and job_dict['status'] != 'WACHTRIJ':
                n_old_jobs += 1
                self.deleteJob(job_key)

        if n_old_jobs > 0:
            TimedMessage(gv=gv, parent=self.parent(), text=f'removed {str(n_old_jobs)} old jobs')

        # get job info from file system
        jobs_global_paths = [os.path.join(jobs_folder_global_path, job_folder) for job_folder in os.listdir(jobs_folder_global_path) 
                                   if os.path.isdir(os.path.join(jobs_folder_global_path, job_folder) )]

        # keep track of the jobs checked
        jobs_checked = {job_name: False for job_name in tracker_dict.keys()}


        ''' In the upcoming for loop, loop through jobs on file system

            1: for a job on file system, check if all data is also in the tracker file
            *: If out-of-sync -> modify tracker file (or delete all) based on files on file system and user input

            2: for a job in tracker file, check if data is also on the file system
            *: If out-of-sync -> modify tracker file (or delete all) based on files on file system and user input

        '''
        for job_global_path in jobs_global_paths:
            # actual_job_main_folder = os.path.basename(os.path.dirname(actual_job_global_path))

            job_key, job_dict = self.jobGlobalPathToTrackerJobDict(
                tracker_dict, job_global_path)

            
            if job_dict is None:
                yes_or_no = YesOrNoMessageBox(parent=self.parent(), 
                                      text=f'SYNCHRONIZE ISSUES!\nJob Tracker and jobs on File System are out of sync!\n\n'\
                                            f'what do you want to do with:\n {job_global_path}?',
                                              yes_button_text='Add to Job Tracker',
                                              no_button_text='Remove from File System')

                if yes_or_no.answer():
                    # TODO: get all info about laser files!
                    job_dict = {'job_name': 'temp_ob_name',
                                'laser_files': {},
                                'status': 'WACHTRIJ',
                                'dynamic_job_name': 'haha'}

                    # TODO: find the material details from the .dxf files first please
                    # add this file to the to tracker
                    print('TODO: add job to tracker')
                    TimedMessage(parent=self.parent(), gv=gv, text=f'Added {job_dict["job_name"]} to Tracker')
                else:
                    # remove that directory
                    delete_item(self.parent(), job_global_path)
                    TimedMessage(parent=self.parent(), gv=gv, text=f'removed folder {job_global_path}')
                    continue

            if not self.IsJobDictAndFileSystemInSync(job_dict, job_global_path):
                tracker_dict[job_key] = self.syncronizeJobDictWithFileSystem(job_dict, job_global_path)
            jobs_checked[job_dict['job_name']] = True

        for tracker_job_name, job_checked in jobs_checked.items():
            if not job_checked:
                tracker_dict.pop(tracker_job_name)

        with open(self.tracker_file_path, 'w' ) as tracker_file:
            json.dump(tracker_dict, tracker_file, indent=4)

        self.makeBackup()

    def IsJobDictAndFileSystemInSync(self, job_dict, job_folder_global_path):
        ''' Check if all files are in both the tracker and the file system. '''
        file_system_laser_file_names = [file_name for file_name in os.listdir(job_folder_global_path) if file_name.lower().endswith(gv['ACCEPTED_EXTENSIONS'])]
        tracker_laser_file_names = [os.path.basename(laser_file_dict['file_global_path']) for laser_file_dict in job_dict['laser_files'].values()]

        return file_system_laser_file_names.sort() == tracker_laser_file_names.sort()
    
    def syncronizeJobDictWithFileSystem(self, job_dict: dict, job_folder_global_path: str):
        ''' Sychronize job dict based on file system. '''
        valid_file_names = [file_name for file_name in os.listdir(job_folder_global_path) if file_name.lower().endswith(gv['ACCEPTED_EXTENSIONS'])]

        # Find files on file system, that are not in tracker
        new_files_list = []
        for file in valid_file_names:
            if not any([os.path.basename(laser_file_dict['file_global_path'])==file for laser_file_dict in job_dict['laser_files'].values()]):
                new_files_list.append(os.path.join(job_folder_global_path, file))

        # add/delete new files
        if len(new_files_list) > 0:

            if len(new_files_list)==1:
                file_str = 'File'
                is_are_str = 'is'
            else:
                file_str = 'Files'
                is_are_str = 'are'

            yes_or_no_text = f'New {file_str} detected for Job {job_dict["job_name"]}:\n'
            for file in new_files_list:
                yes_or_no_text += f'{os.path.basename(file)}\n'

            yes_or_no_text += f'\nWhat do you want with these {file_str}?'

            yes_or_no = YesOrNoMessageBox(parent=self.parent(),
                                          text=yes_or_no_text,
                                          yes_button_text='Add to Job Tracker',
                                          no_button_text='Remove from File System')
            if yes_or_no.answer():

                # TODO: get info about this and that
                file_info_dialog = LaserTrackerFileInfoQDialog(self.parent(),
                                                [job_dict['job_name']],
                                                [new_files_list],
                                                job_dict_list=[job_dict])
                if file_info_dialog.exec() == 1:
                    new_laser_file_dict = file_info_dialog.return_dict_list[0]

                    for key, value in new_laser_file_dict.items():
                       job_dict['laser_files'][key] = value
                    TimedMessage(gv=gv, parent=self.parent(), text=f'Updated laser files for job: {job_dict["job_name"]} in Job Tracker')
                else:
                    TimedMessage(parent=self.parent(), gv=gv, text='Some Error Occured, Job Tracker file and File System still not in Sync')

            else:
                for file in new_files_list:
                    delete_item(self.parent(), os.path.join(job_folder_global_path, file))
                TimedMessage(parent=self.parent(), gv=gv, text=f'Removed {len(new_files_list)} {file_str} from File System')


        # delete file from job dict if it is not on the file system
        remove_keys = []
        for key, file_dict in job_dict['laser_files'].items():
            if not os.path.basename(file_dict['file_global_path']) in valid_file_names:
                remove_keys.append(key)

        if len(remove_keys) > 0:
            if len(remove_keys)==1:
                file_str = 'File'
                is_are_str = 'is'
            else:
                file_str = 'Files'
                is_are_str = 'are'

            warning_text = f'{file_str} missing from file system for job: {job_dict["job_name"]}.\n\nThe {file_str}:\n'
            for key in remove_keys:
                warning_text += f'{key}\n'


            warning_text += f'\n{is_are_str} removed from the Job Tracker.'
            WarningQMessageBox(parent=self.parent(), gv=gv, text=warning_text)

        for key in remove_keys:
            job_dict['laser_files'].pop(key)
        
        return job_dict


    def getExistingMaterials(self) -> set:
        ''' Return all materials that exist in the jobs with a wachtrij status. '''
        with open(self.tracker_file_path, 'r' ) as tracker_file:
            tracker_dict = json.load(tracker_file)

        materials = set()
        for job_dict in tracker_dict.values():
            if job_dict['status'] == 'WACHTRIJ':
                for laser_file_dict in job_dict['laser_files'].values():
                    materials.add(laser_file_dict['material'])
                    
        return materials

    def getMaterialAndThicknessList(self) -> list:
        ''' Return all materials and thickness with status WACHTRIJ. '''

        with open(self.tracker_file_path, 'r' ) as tracker_file:
            tracker_dict = json.load(tracker_file)

        materials_and_thickness_set = set()
        for job_dict in tracker_dict.values():
            if job_dict['status'] == 'WACHTRIJ':
                for laser_file_dict in job_dict['laser_files'].values():
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
                for key, laser_file_dict in job_dict['laser_files'].items():
                    if laser_file_dict['material'] == material and laser_file_dict['thickness'] == thickness:
                        laser_file_info_list.append((key,
                                                            laser_file_dict['file_global_path'],
                                                            laser_file_dict['done']))
        return laser_file_info_list 
    
    def getLaserFilesDict(self, job_name) -> dict:
        ''' TODO '''

        with open(self.tracker_file_path, 'r' ) as tracker_file:
            tracker_dict = json.load(tracker_file)
        return tracker_dict[job_name]['laser_files']

    def fileGlobalPathToJobName(self, file_global_path: str) -> str:
        ''' Return a job name from a file. '''
        with open(self.tracker_file_path, 'r' ) as tracker_file:
            tracker_dict = json.load(tracker_file)

        job_name = None
        for job_dict in tracker_dict.values():
            for laser_file_dict in job_dict['laser_files'].values():
                if laser_file_dict['file_global_path'] == file_global_path:
                    job_name = job_dict['job_name']
        return job_name

    def isJobDone(self, job_name: str) -> bool: 
        ''' Return boolean indicating if a job is done. '''
        with open(self.tracker_file_path, 'r' ) as tracker_file:
            tracker_dict = json.load(tracker_file)

        return all(file_dict['done'] for file_dict in tracker_dict[job_name]['laser_files'].values())


    def getLaserFilesString(self, job_name: str) -> str:
        ''' Return a sting representation of all laser files. '''

        with open(self.tracker_file_path, 'r' ) as tracker_file:
            tracker_dict = json.load(tracker_file)

        return_string = ""
        for file_dict in tracker_dict[job_name]['laser_files'].values():
            return_string += f'{file_dict["file_name"]}\n'

        return return_string

    def jobNameToSenderName(self, job_name: str):
        ''' Return Sender name from job name. '''
        with open(self.tracker_file_path, 'r' ) as tracker_file:
            return json.load(tracker_file)[job_name]['sender_name']



class LaserTrackerFileInfoQDialog(QDialog):
    ''' Ask for file laser file details (material, thickness, amount) and create laser jobs.
    job_name: List with job names
    files_global_paths_list: nested lists with global paths for every file in the job.  

    '''

    def __init__(self, parent,
                 job_name_list: list,
                 files_global_paths_list: list,
                 *args,
                 job_dict_list=None,
                 **kwargs):
        super().__init__(parent, *args, **kwargs)

        loadUi(os.path.join(gv['REPO_DIR_HOME'], 'laser/ui/enter_job_details_dialog.ui'), self)

        assert len(job_name_list) == len(files_global_paths_list),\
            f'length of job name list: {len(job_name_list)} should'\
            f'be equal to the files_global_path_list: {len(files_global_paths_list)}'

        if job_dict_list is not None:
            assert len(job_name_list) == len(job_dict_list),\
                f'length of job name list: {len(job_name_list)} should'\
                f'be equal to the job_dict_list: {len(job_dict_list)}'
                   
        self.job_tracker = LaserJobTracker(self)
        self.job_counter = 0
        self.file_counter = 0
        self.job_name_list = job_name_list
        self.files_global_paths_list = files_global_paths_list
        self.job_dict_list = job_dict_list
        self.return_dict_list = []

        self.temp_files_global_paths = files_global_paths_list[self.job_counter]
 
        self.new_material_text = 'New Material'
        self.new_materials_list = []

        self.materialQComboBox.currentIndexChanged.connect(self.onMaterialComboboxChanged)
        self.skipPushButton.clicked.connect(self.skipJob)
        self.buttonBox.accepted.connect(self.collectFileInfo)
        self.loadJobContent()

    def loadContent(self):
        if self.file_counter >= len(self.temp_files_global_paths):
            self.storeLaserJobDict()

            if self.job_counter+1 >= len(self.job_name_list):
                self.accept()
            else:
                self.job_counter += 1
                self.file_counter= 0
                self.loadJobContent()
        else:
            self.loadFileContent()


    def loadJobContent(self):
        ''' Load content of mail into dialog. '''

        if self.job_dict_list is not None:
            print(f" so this can be foudn {self.job_dict_list[self.job_counter]}\n\n")
            print(f"but ht not {self.job_dict_list[self.job_counter]['job_folder_global_path']}")
            self.temp_job_name = self.job_dict_list[self.job_counter]['job_name']
            self.temp_job_folder_name = os.path.basename(os.path.abspath(self.job_dict_list[self.job_counter]['job_folder_global_path']))
            self.temp_job_folder_global_path = self.job_dict_list[self.job_counter]['job_folder_global_path']
        else:
            self.temp_job_name = self.job_tracker.makeJobNameUnique(self.job_name_list[self.job_counter])
            self.temp_job_folder_name = str(datetime.today().strftime('%d-%m'))+'_'+self.temp_job_name
            self.temp_job_folder_global_path = os.path.join(os.path.join(gv['JOBS_DIR_HOME'], self.temp_job_folder_name))

        self.temp_files_global_paths = self.files_global_paths_list[self.job_counter]
        self.temp_laser_cut_files_dict = {}


        print(f"tmp jb name {self.temp_job_name}")
        self.jobNameQLabel.setText(self.temp_job_name)
        self.jobProgressQLabel.setText(f'Job ({self.job_counter+1}/{len(self.job_name_list)})')


        self.loadFileContent()


    def loadFileContent(self):
        ''' Load content of attachment into dialog. '''

        file_global_path = self.temp_files_global_paths[self.file_counter]
        file_name = os.path.basename(file_global_path)
        print(f"fielname is {file_name} {file_global_path}")

        if file_name.lower().endswith(gv['ACCEPTED_EXTENSIONS']):
            self.fileProgressQLabel.setText(f'File({self.file_counter+1}/{len(self.temp_files_global_paths)})')
            self.fileNameQLabel.setText(file_name)

            # initially hide option for new material 
            self.newMaterialQLabel.setHidden(True)
            self.newMaterialQLineEdit.setHidden(True)

            self.materialQComboBox.clear()
            self.newMaterialQLineEdit.clear()
            self.thicknessQLineEdit.clear()
            self.amountQLineEdit.clear()

            materials = list(set(gv['ACCEPTED_MATERIALS']).union(self.job_tracker.getExistingMaterials()).union(self.new_materials_list))
            self.materialQComboBox.addItems(materials)
            self.materialQComboBox.addItem(self.new_material_text)

            # guess the material, thickness and amount
            for material in materials:
                if material.lower() in file_name.lower():
                    self.materialQComboBox.setCurrentIndex(self.materialQComboBox.findText(material))
            match = re.search(r"\d+\.?\d*(?=mm)", file_name)
            if match:
                self.thicknessQLineEdit.setText(match.group())

            match = re.search(r"\d+\.?\d*(?=x_)", file_name)
            if match:
                self.amountQLineEdit.setText(match.group())
            else:
                self.amountQLineEdit.setText('1')

        else:
            file_global_path = os.path.join(self.temp_job_folder_global_path, file_name)

            if self.file_counter+1 >= len(self.temp_files_global_paths):
                self.storeLaserJobDict()
                self.job_counter += 1

                if self.job_counter >= len(self.job_name_list):
                    self.loadJobContent()
            else:
                self.loadFileContent()

    def onMaterialComboboxChanged(self):
        if self.materialQComboBox.currentText() == self.new_material_text:
            self.newMaterialQLabel.setHidden(False)
            self.newMaterialQLineEdit.setHidden(False)
        else:
            self.newMaterialQLabel.setHidden(True)
            self.newMaterialQLineEdit.setHidden(True)
        
    def collectFileInfo(self):
        ''' Collect material, thickness and amount info. '''
        material = self.materialQComboBox.currentText()
        if material == self.new_material_text:
            material = self.newMaterialQLineEdit.text()
            self.new_materials_list.append(material)
            
        thickness = self.thicknessQLineEdit.text()
        amount = self.amountQLineEdit.text()
        
        if not validate_material_info(self, material, thickness, amount):
            return

        source_file_global_path = self.temp_files_global_paths[self.file_counter]

        original_file_name = os.path.basename(source_file_global_path)
        if material in original_file_name and\
            thickness in original_file_name and\
            amount in original_file_name:
            file_name = original_file_name
        else:
            file_name = material+'_'+thickness+'mm_'+amount+'x_'+original_file_name
        
        target_file_global_path = os.path.join(self.temp_job_folder_global_path, file_name)

        self.temp_laser_cut_files_dict[self.temp_job_name + '_' + file_name] = {
                            'file_name': file_name,
                            'file_global_path': target_file_global_path,
                            'material': material,
                            'thickness': thickness,
                            'amount': amount,
                            'done': False}

        self.file_counter += 1
        self.loadContent()

    def skipJob(self):
        ''' Skip job and go to the next. '''
        if self.job_counter+1 >= len(self.job_name_list):
            self.accept() 
        else:
            self.job_counter += 1
            self.file_counter = 0
            self.loadJobContent()

    def storeLaserJobDict(self):
        """ Store laser job dict. """
        self.return_dict_list.append(self.temp_laser_cut_files_dict)

