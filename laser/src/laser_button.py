import glob
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import *


from global_variables import gv
from laser_job_tracker import LaserJobTracker
from src.button import JobsQPushButton
from src.directory_functions import open_folder


from convert import split_material_name
from src.mail_manager import MailManager
from src.qdialog import SelectOptionsQDialog


from src.qmessagebox import TimedQMessageBox


class LaserKlaarQPushButton(JobsQPushButton):

    def __init__(self, *args, **kwargs):
        JobsQPushButton.__init__(self, *args, **kwargs)
        self.clicked.connect(self.on_click)
 
    def on_click(self):
        job_name = self.getCurrentItemName()
        
        job_folder_global_path = LaserJobTracker().getJobFolderGlobalPathFromJobName(job_name)

        LaserJobTracker().updateJobStatus(job_name, 'VERWERKT')
        self.refreshAllQListWidgets()

        # send response mail
        self.sendFinishedMail(gv, job_name, job_folder_global_path)

            
class MateriaalKlaarQPushButton(JobsQPushButton):

    def __init__(self, *args, **kwargs):
        JobsQPushButton.__init__(self, *args, **kwargs)
        self.clicked.connect(self.on_click)
 
    def on_click(self):
        material_name = self.getCurrentItemName()
        material, thickness = split_material_name(material_name)

        job_tracker = LaserJobTracker()

        # todo: not all is always done
        dxfs_names_and_global_paths = job_tracker.getDXFsAndPaths(material, thickness)

        dialog = SelectOptionsQDialog(self, dxfs_names_and_global_paths)
        if dialog.exec_() == QDialog.Accepted:

            files_names = []
            files_global_paths = []
            for item in dialog.selectedItems():
                files_names.append(item.text())
                files_global_paths.append(item.data(1))

            print(f"fucking irritatn")

        for file_global_path in files_global_paths:
            # find job_name
            job_name = job_tracker.fileGlobalPathToJobName(file_global_path)

            # material done, mark it done
            job_tracker.markFileIsDone(job_name, file_global_path)

            # if all is done, display message
            if job_tracker.isJobDone(job_name):
                # hey this material is done!

                job_tracker.updateJobStatus(job_name, 'VERWERKT')
                job_folder_global_path = job_tracker.getJobFolderGlobalPathFromJobName(job_name)
                self.sendFinishedMail(gv, job_name, job_folder_global_path)

        self.refreshAllQListWidgets()


class AfgekeurdQPushButton(JobsQPushButton):

    def __init__(self, *args, **kwargs):
        JobsQPushButton.__init__(self, *args, **kwargs)
        self.clicked.connect(self.on_click)

    def on_click(self):
        job_name = self.getCurrentItemName()
        job_tracker = LaserJobTracker()
        job_tracker.updateJobStatus(job_name, 'AFGEKEURD')
        self.refreshAllQListWidgets()

        job_folder_global_path = job_tracker.getJobFolderGlobalPathFromJobName(job_name)
        self.sendDeclinedMail(gv, job_name, job_folder_global_path)

class OverigQPushButton(JobsQPushButton):

    def __init__(self, *args, **kwargs):
        JobsQPushButton.__init__(self, *args, **kwargs)
        self.clicked.connect(self.on_click)


    def on_click(self):
        job_name = self.getCurrentItemName()
        print(f'De overig knop is gedrukt {job_name}')


class OptionsQPushButton(JobsQPushButton):

    def __init__(self, *args, **kwargs):
        JobsQPushButton.__init__(self, *args, **kwargs)

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
            pass

        elif self.object_name == 'wachtrijMateriaalOptionsQPushButton':
            pass

        elif self.object_name == 'verwerktOptionsQPushButton':
            self.menu.addAction('Move to Wachtrij', self.moveJobToWachtrij)
            self.menu.addAction('Move to Afgekeurd', self.moveJobToAfgekeurd)

        elif self.object_name == 'afgekeurdOptionsQPushButton':
            self.menu.addAction('Move to Wachtrij', self.moveJobToWachtrij)
            self.menu.addAction('Move to Verwerkt', self.moveJobToVerwerkt)


        else:
            raise ValueError(f'could not identify {self.object_name}')

        self.setMenu(self.menu)

    def moveJobToWachtrij(self):
        self.moveJobTo('WACHTRIJ')

    def moveJobToAfgekeurd(self):
        self.moveJobTo('AFGEKEURD')

    def moveJobToVerwerkt(self):
        self.moveJobTo('VERWERKT')

    def moveJobTo(self, new_status):
        job_name = self.getCurrentItemName()
        LaserJobTracker().updateJobStatus(job_name, new_status)
        self.refreshAllQListWidgets()

    def openInFileExplorer(self):
        job_folder_global_path = self.getJobFolderGlobalPath()
        open_folder(job_folder_global_path)

    def deleteJob(self):
        job_name = self.getCurrentItemName()
        LaserJobTracker().deleteJob(job_name)
        self.refreshAllQListWidgets()

    def getJobFolderGlobalPath(self):
        job_name = self.getCurrentItemName()
        return LaserJobTracker().getJobDict(job_name)['job_folder_global_path']
