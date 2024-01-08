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

from src.directory_functions import open_file, open_folder


from laser_job_tracker import LaserJobTracker
from src.qlist_widget import OverviewQListWidget, ContentQListWidget

class JobsOverviewQListWidget(OverviewQListWidget):

    def __init__(self, *args, **kwargs):
        OverviewQListWidget.__init__(self, *args, **kwargs)

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

        # shortcut on Enter key
        QShortcut(QKeySequence(Qt.Key_Return), self).activated.connect(self.itemEnterPressed)

    def getItemNames(self) -> List[tuple]:
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


    def displayItem(self, job_name: str):
        ''' Display the job page and load content for the highlighted job. '''

        job_status = LaserJobTracker().getJobDict(job_name)['status']

        # find QStackedWidget for job_status
        stacked_widget = self.window().findChild(
                QStackedWidget,
                self.widget_names[job_status]['QStackedWidget'])

        # load job into JobContentQListWidget
        stacked_widget.findChild(JobContentQListWidget).loadContent(job_name)

        # show jobPage in stackedWidget 
        stacked_widget.setCurrentIndex(1)

        # show job_status tabWidget
        tab_widget = self.window().findChild(QTabWidget, 'jobsQTabWidget')
        tab_widget.setCurrentIndex(self.widget_names[job_status]['tab_widget_position'])


class JobContentQListWidget(ContentQListWidget):

    def __init__(self, *args, **kwargs):
        ContentQListWidget.__init__(self, *args, **kwargs)

        # shortcut for the Enter button
        # QShortcut(QKeySequence(Qt.Key_Return), self).activated.connect(self.jobFileEnterPressed)        


    def loadContent(self, job_name):
        self.clear()
        self.current_item_name = job_name

        job_dict = LaserJobTracker().getJobDict(job_name)

        for file in os.listdir(job_dict['job_folder_global_path']):

            item = QListWidgetItem()
            item.setText(file)
            item.setData(1, os.path.join(
                job_dict['job_folder_global_path'], file))
            self.addItem(item)

        self.itemClicked.connect(self.fileClicked)

class MaterialOverviewQListWidget(OverviewQListWidget):

    def __init__(self, *args, **kwargs):
        QListWidget.__init__(self, *args, **kwargs)

        self.initialize(self.getItemNames())

        # shortcut on Enter key
        QShortcut(QKeySequence(Qt.Key_Return), self).activated.connect(self.itemEnterPressed)
    
    def getItemNames(self):
        ''' Return the materials and thickness in a list. '''
        return LaserJobTracker().getMaterialAndThicknessList()

    def displayItem(self, material_name: str):
        ''' Display the material page and load content for the highlighted material. '''

        print(f"display item yo {material_name}")   

        stacked_widget = self.window().findChild(
                QStackedWidget,
                'wachtrijMateriaalQStackedWidget')

        stacked_widget.findChild(MaterialContentQListWidget).loadContent(material_name)

        # show materialPage in stackedWidget 
        stacked_widget.setCurrentIndex(1)


class MaterialContentQListWidget(ContentQListWidget):

    def __init__(self, *args, **kwargs):
        ContentQListWidget.__init__(self, *args, **kwargs)


    def loadContent(self, material_name):
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
                item.setData(1, dxf_global_path)
                self.addItem(item)

            self.itemClicked.connect(self.fileClicked)