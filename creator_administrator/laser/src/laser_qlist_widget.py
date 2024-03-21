from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QStackedWidget, QListWidgetItem, QLabel, QTabWidget, QWidget

from src.qlist_widget import OverviewQListWidget, ContentQListWidget, JobContentQListWidget
from convert import split_material_name
from laser_job_tracker import LaserJobTracker

class LaserAllJobsOverviewQListWidget(OverviewQListWidget):

    def __init__(self, parent: QWidget, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.job_tracker = LaserJobTracker(self)

        self.widget_names ={'WACHTRIJ':
                                {'QStackedWidget': 'wachtrijQStackedWidget',
                                 'tab_widget_position': 1},
                            'VERWERKT':
                                {'QStackedWidget': 'verwerktQStackedWidget',
                                 'tab_widget_position': 3},
                            'AFGEKEURD':
                                {'QStackedWidget': 'afgekeurdQStackedWidget',
                                 'tab_widget_position': 4}}
        self.refresh()

    def refresh(self):
        ''' Initialise the list widget with jobs. '''
        self.clear()
        self.initialize(self.job_tracker.getAllStaticAndDynamicJobNames())

    def displayItem(self, item_name: str):
        ''' Display the job page and load content for the highlighted job. '''

        job_status = self.job_tracker.getJobDict(item_name)['status']

        # find QStackedWidget for job_status
        stacked_widget = self.window().findChild(
                QStackedWidget,
                self.widget_names[job_status]['QStackedWidget'])

        # load job into JobContentQListWidget
        stacked_widget.findChild(JobContentQListWidget).loadContent(item_name)

        # show jobPage in stackedWidget
        stacked_widget.setCurrentIndex(1)

        # show job_status tabWidget
        tab_widget = self.window().findChild(QTabWidget, 'jobsQTabWidget')
        tab_widget.setCurrentIndex(self.widget_names[job_status]['tab_widget_position'])

class LaserWachtrijJobsOverviewQListWidget(OverviewQListWidget):

    def __init__(self, parent: QWidget, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.refresh()

    def refresh(self):
        ''' Initialise the list widget with jobs. '''
        self.clear()
        self.initialize(LaserJobTracker(self).getStaticAndDynamicJobNamesWithStatus('WACHTRIJ'))

class LaserMaterialOverviewQListWidget(OverviewQListWidget):

    def __init__(self, parent: QWidget, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

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



class LaserVerwerktJobsOverviewQListWidget(OverviewQListWidget):

    def __init__(self, parent: QWidget, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.refresh()

    def refresh(self):
        ''' Initialise the list widget with jobs. '''
        self.clear()
        self.initialize(LaserJobTracker(self).getStaticAndDynamicJobNamesWithStatus('VERWERKT'))


class LaserAfgekeurdJobsOverviewQListWidget(OverviewQListWidget):

    def __init__(self, parent: QWidget, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.refresh()

    def refresh(self):
        ''' Initialise the list widget with jobs. '''
        self.clear()
        self.initialize(LaserJobTracker(self).getStaticAndDynamicJobNamesWithStatus('AFGEKEURD'))

class LaserJobContentQListWidget(JobContentQListWidget):

    def __init__(self, parent: QWidget, *args, **kwargs):
        super().__init__(parent, LaserJobTracker(self), *args, **kwargs)

class LaserMaterialContentQListWidget(ContentQListWidget):

    def __init__(self, parent: QWidget, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

    def loadContent(self, item_name):
        self.clear()
        self.current_item_name = item_name

        self.parent().findChild(QLabel, 'materialQLabel').setText(item_name)

        material, thickness = split_material_name(item_name)

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
