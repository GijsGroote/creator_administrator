import glob
import os
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from global_variables import gv
from src.worker import Worker

from laser_job_tracker import LaserJobTracker
from src.button import JobsQPushButton
from src.directory_functions import open_folder

from src.directory_functions import delete, delete_directory_content

from convert import split_material_name
from src.mail_manager import MailManager
from src.qdialog import SelectOptionsQDialog


from src.directory_functions import copy_item
from src.qmessagebox import TimedMessage, JobFinishedMessageBox, YesOrNoMessageBox, ErrorQMessageBox, WarningQMessageBox
from laser_qlist_widget import MaterialContentQListWidget
from requests.exceptions import ConnectionError
from src.threaded_mail_manager import ThreadedMailManager


class LaserKlaarQPushButton(JobsQPushButton):

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.threadpool = gv["THREAD_POOL"]
        self.clicked.connect(self.on_click)
 
    def on_click(self):
        job_name = self.getCurrentItemName()
        job_tracker = LaserJobTracker(self)
        
        job_folder_global_path = job_tracker.getJobFolderGlobalPathFromJobName(job_name)
        job_tracker.updateJobStatus(job_name, 'VERWERKT')
        sender_name = job_tracker.jobNameToSenderName(job_name)
        self.refreshAllQListWidgets()

        if not any([file.endswith(('.msg', '.eml')) for file in os.listdir(job_folder_global_path)]):
            WarningQMessageBox(gv=gv, parent=self, text=f'No Job finished mail send because: No mail file found')
        else:
            ThreadedMailManager(parent_widget=self, gv=gv).startFinishedMailWorker(
                success_message=f'Job finished mail send to {sender_name}',
                error_message=f'No job finished mail send to {sender_name}',
                job_folder_global_path=job_folder_global_path,
                template_content={})

class MateriaalKlaarQPushButton(JobsQPushButton):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.clicked.connect(self.on_click)
        self.job_tracker = LaserJobTracker(self)
 
    def on_click(self):
        material_name = self.getCurrentItemName()
        material, thickness = split_material_name(material_name)

        dxfs_names_and_global_paths = self.job_tracker.getDXFsAndPaths(material, thickness)
        dialog = SelectOptionsQDialog(self, dxfs_names_and_global_paths)

        if dialog.exec() == 1:
            files_names = []
            files_global_paths = []
            for item in dialog.optionsQListWidget.selectedItems():
                files_names.append(item.text())
                files_global_paths.append(item.data(1))
        else:
            return

        for file_global_path in files_global_paths:
            # find job_name
            job_name = self.job_tracker.fileGlobalPathToJobName(file_global_path)

            # material done, mark it done
            self.job_tracker.markFileIsDone(job_name, file_global_path)

            # if all is done, display message
            if self.job_tracker.isJobDone(job_name):
                # hey this material is done!

                self.job_tracker.updateJobStatus(job_name, 'VERWERKT')
                sender_name = self.job_tracker.jobNameToSenderName(job_name)
                job_folder_global_path = self.job_tracker.getJobFolderGlobalPathFromJobName(job_name)               
            
                if not any([file.endswith(('.msg', '.eml')) for file in os.listdir(job_folder_global_path)]):
                    WarningQMessageBox(gv=gv, parent=self, text=f'No Job finished mail send because: No mail file found')
                else:
                    ThreadedMailManager(parent_widget=self, gv=gv).startFinishedMailWorker(
                            success_message=f"Job finished mail send to {sender_name}",
                            error_message=f'No job finished mail send to {sender_name}',
                            job_folder_global_path=job_folder_global_path,
                            template_content={})

        self.refreshAllQListWidgets()

class AfgekeurdQPushButton(JobsQPushButton):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.clicked.connect(self.on_click)
        self.threadpool = gv['THREAD_POOL']

    def on_click(self):
        job_name = self.getCurrentItemName()
        job_tracker = LaserJobTracker(self)
        job_tracker.updateJobStatus(job_name, 'AFGEKEURD')
        self.refreshAllQListWidgets()

        job_folder_global_path = job_tracker.getJobFolderGlobalPathFromJobName(job_name)

        
        if not any([file.endswith(('.msg', '.eml')) for file in os.listdir(job_folder_global_path)]):
                    WarningQMessageBox(gv=gv, parent=self, text=f'No Afgekeurd mail send because: No mail file found')
        else:
            sender_name = job_tracker.jobNameToSenderName(job_name)

            ThreadedMailManager(parent_widget=self, gv=gv).startDeclinedMailWorker(
                success_message=f'Job declined mail send to {sender_name}',
                error_message=f'No job declined mail send to {sender_name}',
                job_folder_global_path=job_folder_global_path,
                template_content={})
        
class OptionsQPushButton(JobsQPushButton):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.menu = QMenu()

        self.object_name = self.objectName()
        self.menu.addAction('Open in File Explorer', self.openInFileExplorer)
        self.menu.addAction('Delete Job', self.deleteJob)

        # initialize  
        self.objectNameChanged.connect(self.storeObjectNameInit)

    def storeObjectNameInit(self):
        ''' store the object name and initialize. '''
        self.object_name = self.objectName()

        if self.object_name == 'allJobsOptionsQPushButton':
            self.menu.addAction('Move to Wachtrij', self.moveJobToWachtrij)
                        
        elif self.object_name == 'wachtrijOptionsQPushButton':
            self.menu.addAction('Copy Files to ..', self.copyLaserFilesTo)

        elif self.object_name == 'wachtrijMateriaalOptionsQPushButton':
            self.menu.addAction('Copy Files to ..', self.copyMaterialWachtrijFilesTo)

        elif self.object_name == 'verwerktOptionsQPushButton':
            self.menu.addAction('Copy Laser Files to TODO folder', self.copyLaserFilesTo)
            self.menu.addAction('Move to Wachtrij', self.moveJobToWachtrij)
            self.menu.addAction('Move to Afgekeurd', self.moveJobToAfgekeurd)

        elif self.object_name == 'afgekeurdOptionsQPushButton':
            self.menu.addAction('Copy Laser Files to TODO folder', self.copyLaserFilesTo)
            self.menu.addAction('Move to Wachtrij', self.moveJobToWachtrij)
            self.menu.addAction('Move to Verwerkt', self.moveJobToVerwerkt)

        else:
            raise ValueError(f'could not identify {self.object_name}')

        self.setMenu(self.menu)

    def moveJobToWachtrij(self):
        # TODO: moving a job to wachtrij also includes putting the laser files on not done (to display in material queue)
        self.moveJobTo('WACHTRIJ')
        self.refreshAllQListWidgets()

    def moveJobToAfgekeurd(self):
        self.moveJobTo('AFGEKEURD')
        self.refreshAllQListWidgets()

    def moveJobToVerwerkt(self):
        self.moveJobTo('VERWERKT')
        self.refreshAllQListWidgets()

    def moveJobTo(self, new_status):
        job_name = self.getCurrentItemName()
        LaserJobTracker(self).updateJobStatus(job_name, new_status)
        self.refreshAllQListWidgets()

    def openInFileExplorer(self):
        job_folder_global_path = self.getJobFolderGlobalPath()
        open_folder(job_folder_global_path)

    def deleteJob(self):
        job_name = self.getCurrentItemName()
        LaserJobTracker(self).deleteJob(job_name)
        self.refreshAllQListWidgets()

    def getJobFolderGlobalPath(self):
        job_name = self.getCurrentItemName()
        return LaserJobTracker(self).getJobDict(job_name)['job_folder_global_path']
    
    def copyLaserFilesTo(self):
        '''Copy the laser files from a job to a specified folder. '''

        job_name = self.getCurrentItemName()
        laser_file_dict =  LaserJobTracker(self).getLaserFilesDict(job_name)
        target_folder_global_path = gv['TODO_DIR_HOME']

        delete_directory_content(target_folder_global_path)
                   
        for file_key, file_dict in laser_file_dict.items():
            source_item_global_path = file_dict['file_global_path']
            target_item_global_path = os.path.join(target_folder_global_path, file_key)
            copy_item(source_item_global_path, target_item_global_path)

        # open_folder(target_folder_global_path)

    def copyMaterialWachtrijFilesTo(self):
        ''' Copy the dxf files in wachtrij to a specified folder. '''

        material_name = self.getCurrentItemName()
        material, thickness = split_material_name(material_name)
        dxfs_names_and_global_paths = LaserJobTracker(self).getDXFsAndPaths(material, thickness)
        target_folder_global_path = gv['TODO_DIR_HOME']

        delete_directory_content(target_folder_global_path)

        for file_name, file_global_path in dxfs_names_and_global_paths:
            copy_item(file_global_path, os.path.join(target_folder_global_path, file_name))

        # open_folder(target_folder_global_path)
