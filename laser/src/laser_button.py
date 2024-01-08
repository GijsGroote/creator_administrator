import glob
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
        QMenu,
        QMessageBox,
        QShortcut)

from global_variables import gv
from laser_job_tracker import LaserJobTracker
from src.button import JobsQPushButton
from src.directory_functions import open_folder

from src.mail_manager import MailManager

from src.qmessagebox import TimedQMessageBox


class LaserKlaarQPushButton(JobsQPushButton):

    def __init__(self, *args, **kwargs):
        JobsQPushButton.__init__(self, *args, **kwargs)
        self.clicked.connect(self.on_click)
 
    def on_click(self):
        job_name = self.getCurrentStaticJobName()
        
        job_folder_global_path = LaserJobTracker().jobNameToJobFolderGlobalPath(job_name)

        LaserJobTracker().updateJobStatus(job_name, 'VERWERKT')
        self.refreshAllQListWidgets()

        # send response mail
        mail_manager = MailManager(gv)
        msg_file_global_path = mail_manager.getMailGlobalPathFromFolder(job_folder_global_path)

        if msg_file_global_path is not None:
            mail_manager.replyToEmailFromFileUsingTemplate(
                        msg_file_global_path,
                        "FINISHED_MAIL_TEMPLATE",
                        {},
                        popup_reply=False)

            TimedQMessageBox(
                    text=f"Pickup mail send for: {job_name}",
                    parent=self)
        else:
            TimedQMessageBox(
                    text=f"No .msg file in job, no Pickup mail was sent for job: {self.temp_job_name}",
                    parent=self, icon=QMessageBox.Warning)
            
class MateriaalKlaarQPushButton(JobsQPushButton):

    def __init__(self, *args, **kwargs):
        JobsQPushButton.__init__(self, *args, **kwargs)
        self.clicked.connect(self.on_click)
 
    def on_click(self):
        job_name = self.getCurrentStaticJobName()
        # TODO: this is some special stuff right here
        # LaserJobTracker.updateJobStatus(job_name, '

        print(f'Materiaal klaarlaser klaar {job_name}')


class AfgekeurdQPushButton(JobsQPushButton):

    def __init__(self, *args, **kwargs):
        JobsQPushButton.__init__(self, *args, **kwargs)
        self.clicked.connect(self.on_click)

    def on_click(self):
        job_name = self.getCurrentStaticJobName()
        LaserJobTracker().updateJobStatus(job_name, 'AFGEKEURD')
        self.refreshAllQListWidgets()

        mail_manager = MailManager(gv)
        job_folder_global_path = LaserJobTracker().jobNameToJobFolderGlobalPath(job_name)

        mail_manager.replyToEmailFromFileUsingTemplate(
                mail_manager.getMailGlobalPathFromFolder(job_folder_global_path),
                'DECLINED_MAIL_TEMPLATE',
                {},
                popup_reply=True)

        TimedQMessageBox(
                    text=f"Pickup mail send for {job_name}",
                    parent=self)

class OverigQPushButton(JobsQPushButton):

    def __init__(self, *args, **kwargs):
        JobsQPushButton.__init__(self, *args, **kwargs)
        self.clicked.connect(self.on_click)
 
        # shortcut on Esc button
        # QShortcut(QKeySequence(Qt.Key_Escape), self).activated.connect(self.on_click)


    def on_click(self):
        job_name = self.getCurrentStaticJobName()
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
            print('wachtrijOptionsQPushButton')

        elif self.object_name == 'wachtrijMateriaalOptionsQPushButton':
            print('wachtrijMateriaalOptionsQPushButton')

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
        job_name = self.getCurrentStaticJobName()
        LaserJobTracker().updateJobStatus(job_name, new_status)
        self.refreshAllQListWidgets()

    def openInFileExplorer(self):
        job_folder_global_path = self.getJobFolderGlobalPath()
        open_folder(job_folder_global_path)

    def deleteJob(self):
        job_name = self.getCurrentStaticJobName()
        LaserJobTracker().deleteJob(job_name)
        self.refreshAllQListWidgets()

    def getJobFolderGlobalPath(self):
        job_name = self.getCurrentStaticJobName()
        return LaserJobTracker().getJobDict(job_name)['job_folder_global_path']
