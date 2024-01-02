import sys
import subprocess
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
        QPushButton,
        QMenu,
        QToolButton,
        QShortcut)

from jobs_qlist_widget import JobContentQListWidget
from jobs_qlist_widget import JobsQListWidget
from global_variables import gv
from laser_job_tracker import LaserJobTracker
from src.button import JobsQPushButton
from src.directory_functions import open_folder


class LaserKlaarQPushButton(JobsQPushButton):

    def __init__(self, *args, **kwargs):
        JobsQPushButton.__init__(self, *args, **kwargs)
        self.clicked.connect(self.on_click)
 
    def on_click(self):
        job_name = self.getCurrentStaticJobName()
        # TODO: mail the peeps, print job is ready
        LaserJobTracker().updateJobStatus(job_name, 'VERWERKT')
        self.refreshAllQListWidgets()


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
        # TODO: send mail, this is afgekeurd
        LaserJobTracker().updateJobStatus(job_name, 'AFGEKEURD')
        self.refreshAllQListWidgets()

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
        job_folder_absolute_path = self.getJobFolderAbsolutePath()
        open_folder(job_folder_absolute_path)

    def deleteJob(self):
        job_name = self.getCurrentStaticJobName()
        LaserJobTracker().deleteJob(job_name)
        self.refreshAllQListWidgets()

    def getJobFolderAbsolutePath(self):
        job_name = self.getCurrentStaticJobName()
        return LaserJobTracker().getJobDict(job_name)['job_folder_global_path']




