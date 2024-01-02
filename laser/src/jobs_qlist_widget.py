import os
from typing import List
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
        QShortcut,
        QListWidget, QPushButton,
        QWidget, QListWidgetItem, QStackedWidget,
        QVBoxLayout, QTabWidget
)

from laser_job_tracker import LaserJobTracker

class JobsQListWidget(QListWidget):

    def __init__(self, *args, **kwargs):
        QListWidget.__init__(self, *args, **kwargs)

        self.object_name = None

        self.widget_names ={'WACHTRIJ': 
                                {'QStackedWidget': 'wachtrijQStackedWidget',
                                 'tab_widget_position': 1},
                            'VERWERKT': 
                                {'QStackedWidget': 'verwerktQStackedWidget',
                                 'tab_widget_position': 3},
                            'AFGEKEURD': 
                                {'QStackedWidget': 'afgekeurdQStackedWidget',
                                 'tab_widget_position': 4}}

        
        # initialize  
        self.objectNameChanged.connect(self.storeObjectNameInit)

        # shortcut on Enter button
        QShortcut(QKeySequence(Qt.Key_Return), self).activated.connect(self.jobEnterPressed)

    def storeObjectNameInit(self):
        ''' store the object name and initialize. '''
        self.object_name = self.objectName()
        self.initialize(self.getJobNames())

    def getJobNames(self) -> List[tuple]:
        ''' Return a list of tuples containing:
                first the short unique job name
                second the informative dynamic job name '''

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
        self.displayJob(self.currentItem().data(1))

    def jobClicked(self, clicked_job):
        ''' Display the content of the job clicked. '''
        self.displayJob(clicked_job.data(1)) # get the unique job name

    def displayJob(self, job_name: str):
        ''' Display the job page and load content for the highlighted job. '''

        job_status = LaserJobTracker().getJobDict(job_name)['status']

        # find QStackedWidget for job_status
        stacked_widget = self.window().findChild(
                QStackedWidget,
                self.widget_names[job_status]['QStackedWidget'])

        # load job into JobContentQListWidget
        stacked_widget.findChild(JobContentQListWidget).loadJob(job_name)

        # show jobPage in stackedWidget 
        stacked_widget.setCurrentIndex(1)

        # show job_status tabWidget
        tab_widget = self.window().findChild(QTabWidget, 'jobsQTabWidget')
        tab_widget.setCurrentIndex(self.widget_names[job_status]['tab_widget_position'])


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
