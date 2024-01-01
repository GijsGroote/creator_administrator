import os
from typing import List
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
        QShortcut,
        QListWidget, QPushButton,
        QWidget, QListWidgetItem, QStackedWidget,
        QVBoxLayout)

from global_variables import gv
from laser_job_tracker import LaserJobTracker


class JobsQListWidget(QListWidget):

    def __init__(self, *args, **kwargs):
        QListWidget.__init__(self, *args, **kwargs)

        self.object_name = None
        
        # initialize  
        self.objectNameChanged.connect(self.storeObjectNameInit)


        # shortcut on Esc button
        QShortcut(QKeySequence(Qt.Key_Return), self).activated.connect(self.jobEnterPressed)

    
    def storeObjectNameInit(self):
        ''' store the object name and initialize. '''
        self.object_name = self.objectName()
        self.initialize(self.getJobNames())
        
    def getJobNames(self) -> List[tuple]:
        job_tracker = LaserJobTracker()
        if self.object_name == 'allJobsQListWidget':
            return job_tracker.getAllStaticAndDynamicJobNames()
        elif self.object_name == 'wachtrijJobsQListWidget':
            return job_tracker.getStaticAndDynamicJobNamesWithStatus('WACHTRIJ')
        elif self.object_name == 'wachtrijMateriaalJobsQListWidget':
            return job_tracker.getStaticAndDynamicJobNamesWithStatus('TODO') # TODO: this special boyy
        elif self.object_name == 'verwerktJobsQListWidget':
            return job_tracker.getStaticAndDynamicJobNamesWithStatus('VERWERKT')
        elif self.object_name == 'afgekeurdJobsQListWidget':
            return job_tracker.getStaticAndDynamicJobNamesWithStatus('AFGEKEURD')
        else:
            raise ValueError(f'could not find jobs for {self.objectName()}')

    def refresh(self):
        ''' Refresh displayed jobs. '''
        self.clear()
        self.initialize(self.getJobNames())



    def initialize(self, job_names: list):

        for (static_job_name, dynamic_job_name) in job_names:

            item = QListWidgetItem()
            item.setText(dynamic_job_name)
            item.setData(1, static_job_name) # save unique job name
            self.addItem(item)

        self.itemClicked.connect(self.jobClicked)

    def jobEnterPressed(self):
        self.displayJob(self.currentItem().text())

    def jobClicked(self, clicked_job):
        ''' Display the content of the job clicked. '''
        self.displayJob(clicked_job.data(1)) # get the unique job name

    def displayJob(self, job_item_text):
        ''' Display the job page and load content for the highlighted job. '''
        stacked_widget_name = self.object_name.split('JobsQListW')[0]+'QStackedWidget'
        stacked_widget = self.window().findChild(QStackedWidget, stacked_widget_name)

        # load job into JobContentQListWidget
        stacked_widget.findChild(JobContentQListWidget).loadJob(job_item_text)

        # show jobPage in stackedWidget 
        stacked_widget.setCurrentIndex(1)


class JobContentQListWidget(QListWidget):

    def __init__(self, *args, **kwargs):
        QListWidget.__init__(self, *args, **kwargs)
        self.current_job_name = None

        
    def loadJob(self, job_name):

        self.clear()
        self.current_job_name = job_name

        # TODO: make this come form the tracker mostly.
        job_dict = LaserJobTracker().getJobDict(job_name)

        for file in os.listdir(job_dict['job_folder_global_path']):

            item = QListWidgetItem()
            item_widget = QWidget()
            line_push_button = QPushButton(file)
            line_push_button.setObjectName(file)
            line_push_button.clicked.connect(self.fileClicked)
            item_layout = QVBoxLayout()
            item_layout.addWidget(line_push_button)
            item_widget.setLayout(item_layout)
            item.setSizeHint(item_widget.sizeHint())
            self.addItem(item)
            self.setItemWidget(item, item_widget)

    def fileClicked(self):
        print('a file was clicked hree thus now')

    def refresh(self):
        pass
