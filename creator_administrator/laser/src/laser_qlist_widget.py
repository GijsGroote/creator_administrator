import os

# from PyQt6.QtCore import *
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QStackedWidget, QListWidgetItem, QLabel, QListWidget, QTabWidget

from src.qlist_widget import OverviewQListWidget, ContentQListWidget
from convert import split_material_name
from laser_job_tracker import LaserJobTracker

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


    def getItemNames(self) -> list[tuple]:
        ''' Return a list of tuples containing:
                first the short unique job name
                second the informative dynamic job name '''

        job_tracker = LaserJobTracker(self)
        if self.object_name == 'allJobsQListWidget':
            return job_tracker.getAllStaticAndDynamicJobNames()
        if self.object_name == 'wachtrijJobsQListWidget':
            return job_tracker.getStaticAndDynamicJobNamesWithStatus('WACHTRIJ')
        if self.object_name == 'verwerktJobsQListWidget':
            return job_tracker.getStaticAndDynamicJobNamesWithStatus('VERWERKT')
        if self.object_name == 'afgekeurdJobsQListWidget':
            return job_tracker.getStaticAndDynamicJobNamesWithStatus('AFGEKEURD')

        raise ValueError(f'could not find jobs for {self.objectName()}')


    def displayItem(self, job_name: str):
        ''' Display the job page and load content for the highlighted job. '''

        job_status = LaserJobTracker(self).getJobDict(job_name)['status']

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

    def loadContent(self, job_name):
        self.clear()
        self.current_item_name = job_name

        job_dict = LaserJobTracker(self).getJobDict(job_name)

        if job_dict is not None:
            self.parent().findChild(QLabel).setText(job_dict['dynamic_job_name'])

            for file in os.listdir(job_dict['job_folder_global_path']):

                item = QListWidgetItem()
                item.setData(1, os.path.join(
                    job_dict['job_folder_global_path'], file))

                # check if it is a laser file, indicate if it is done with an emoticon
                for laser_file_dict in [val for key,val in job_dict['laser_files'].items() if file in key]:
                    # ☑️✅✔️❎
                    if laser_file_dict['done']:
                        file ='✅ '+file
                    else:
                        file ='❎ '+file

                item.setText(file)
                item.setFont(QFont('Cantarell', 14))
                self.addItem(item)


class MaterialOverviewQListWidget(OverviewQListWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.initialize(self.getItemNames())

        self.itemDoubleClicked.connect(self.itemIsDoubleClicked)


    def getItemNames(self) -> list:
        ''' Return the materials and thickness in a list. '''
        return LaserJobTracker(self).getMaterialAndThicknessList()


    def displayItem(self, material_name: str):
        ''' Display the material page and load content for the highlighted material. '''


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
        self.current_item_name = material_name

        self.parent().findChild(QLabel, 'materialQLabel').setText(material_name)

        material, thickness = split_material_name(material_name)

        laser_file_info_list = LaserJobTracker(
                self).getLaserFilesWithMaterialThicknessInfo(material, thickness)

        for (dxf_name, dxf_global_path, done) in laser_file_info_list:
            item = QListWidgetItem()
            item.setData(1, dxf_global_path)

            # Indicate if done with emotico
            if done:
                item.setText('✅ '+dxf_name)
            else:
                item.setText('❎ '+dxf_name)

            item.setFont(QFont('Cantarell', 14))
            self.addItem(item)

