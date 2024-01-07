import os
from typing import List
import re
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
        QShortcut,
        QListWidget, QPushButton,
        QWidget, QListWidgetItem, QStackedWidget,
        QVBoxLayout, QTabWidget
)

from global_variables import gv
from src.directory_functions import open_file, open_folder


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
        current_item = self.currentItem()
        if current_item is not None:
            self.displayJob(current_item.data(1))

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


        # shortcut for the Enter button
        QShortcut(QKeySequence(Qt.Key_Return), self).activated.connect(self.jobFileEnterPressed)
        

    def jobFileEnterPressed(self):

        current_item = self.currentItem()
        
        if current_item is not None:
            self.jobFileClicked(current_item)

    def jobFileClicked(self, clicked_file):
        open_file(gv, os.path.join(clicked_file.data(1), clicked_file.text()))

    def loadJob(self, job_name):
        self.clear()
        self.current_job_name = job_name

        job_dict = LaserJobTracker().getJobDict(job_name)

        for file in os.listdir(job_dict['job_folder_global_path']):

            item = QListWidgetItem()
            item.setText(file)
            item.setData(1, job_dict['job_folder_global_path']) # save unique job name
            self.addItem(item)

        self.itemClicked.connect(self.jobFileClicked)

    def refresh(self):
        pass

class MaterialQListWidget(QListWidget):

    def __init__(self, *args, **kwargs):
        QListWidget.__init__(self, *args, **kwargs)

        self.initialize(LaserJobTracker().getMaterialAndThicknessList())

        # shortcut on Enter button
        QShortcut(QKeySequence(Qt.Key_Return), self).activated.connect(self.materialEnterPressed)

    def refresh(self):
        ''' Refresh displayed jobs. '''
        self.clear()
        self.initialize(LaserJobTracker().getMaterialAndThicknessList())

    def initialize(self, material_thickness_list: list):

        for material_name in material_thickness_list:
            item = QListWidgetItem()
            item.setText(material_name)
            self.addItem(item)

        self.itemClicked.connect(self.materialClicked)

    def materialEnterPressed(self):
        current_item = self.currentItem()
        if current_item is not None:
            self.displayMaterial(current_item.text())

    def materialClicked(self, clicked_material):
        ''' Display the content of the material clicked. '''
        self.display(clicked_material.data(1)) # get the unique job name

    def displayMaterial(self, material_name: str):
        ''' Display the material page and load content for the highlighted material. '''


        stacked_widget = self.window().findChild(
                QStackedWidget,
                'wachtrijMateriaalQStackedWidget')

        stacked_widget.findChild(MaterialContentQListWidget).loadMaterial(material_name)

        # show materialPage in stackedWidget 
        stacked_widget.setCurrentIndex(1)


class MaterialContentQListWidget(QListWidget):

    def __init__(self, *args, **kwargs):
        QListWidget.__init__(self, *args, **kwargs)

        # shortcut for the Enter button
        QShortcut(QKeySequence(Qt.Key_Return), self).activated.connect(self.jobFileEnterPressed)

    def jobFileEnterPressed(self):

        current_item = self.currentItem()
        
        if current_item is not None:
            self.materialFileClicked(current_item)

    def materialFileClicked(self, clicked_file):
        open_file(gv, os.path.join(clicked_file.data(1), clicked_file.text()))

    def loadMaterial(self, material_name):
        self.clear()
        self.current_material_name = material_name


        match = re.search(r'(.+)_(\d+)mm', material_name)
        if match:
            material = match.group(1)
            thickness = match.group(2)


        dxfs_names_and_global_paths = LaserJobTracker().getDXFsAndPaths(material, thickness)

        for (dxf_name, dxf_global_path) in dxfs_names_and_global_paths:

            item = QListWidgetItem()
            item.setText(dxf_name)
            item.setData(1, dxf_global_path) # save unique job name
            self.addItem(item)

        self.itemClicked.connect(self.materialFileClicked)

    def refresh(self):
        pass
