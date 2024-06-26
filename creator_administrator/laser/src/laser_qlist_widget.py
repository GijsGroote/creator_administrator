from functools import partial

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QStackedWidget, QListWidgetItem, QLabel, QTabWidget, QWidget, QDialog

from src.qlist_widget import OverviewQListWidget, ContentQListWidget, JobContentQListWidget

from global_variables import gv
from convert import split_material_name
from laser_job_tracker import LaserJobTracker

class LaserAllJobsOverviewQListWidget(OverviewQListWidget):

    def __init__(self, parent: QWidget, *args, **kwargs):
        super().__init__(parent, gv, LaserJobTracker(self), *args, **kwargs)

        self.refresh()

    def refresh(self):
        ''' Initialise the list widget with jobs. '''
        self.clear()
        self.initialize(self.job_tracker.getStaticAndDynamicJobNames())

    def refreshWithMatch(self, match_str: str):
        ''' Initialise with all jobs that match match_str. '''
        self.clear()
        self.initialize(self.job_tracker.getStaticAndDynamicJobNames(filter_jobs_on='match', filter_str=match_str))

    def displayItem(self, item_name: str):
        ''' Display the job page and load content for the highlighted job. '''

        job_status = self.job_tracker.getJobDict(item_name)['status']

        main_window = self.parent().window()

        # A dialog with this list in it embedded should set self.main_window
        if isinstance(main_window, QDialog):
            main_window = self.main_window
            self.window().close() # close dialog

        # find QStackedWidget for job_status
        stacked_widget = main_window.findChild(
                QStackedWidget,
                gv['TAB_QSTACK_POSITIONS'][job_status]['QStackedWidget'])

        # load job into JobContentQListWidget
        stacked_widget.findChild(JobContentQListWidget).loadContent(item_name)

        # show jobPage in stackedWidget
        stacked_widget.setCurrentIndex(1)

        # show job_status tabWidget
        tab_widget = main_window.findChild(QTabWidget, 'jobsQTabWidget')
        tab_widget.setCurrentIndex(gv['TAB_QSTACK_POSITIONS'][job_status]['tab_widget_position'])

class LaserWachtrijJobsOverviewQListWidget(OverviewQListWidget):

    def __init__(self, parent: QWidget, *args, **kwargs):
        super().__init__(parent, gv, LaserJobTracker(self), *args, **kwargs)

        self.refresh()

    def refresh(self):
        ''' Initialise the list widget with jobs. '''
        self.clear()
        self.initialize(LaserJobTracker(self).getStaticAndDynamicJobNames(
            filter_jobs_on='status', filter_str='WACHTRIJ'))

class LaserMaterialOverviewQListWidget(OverviewQListWidget):

    def __init__(self, parent: QWidget, *args, **kwargs):
        super().__init__(parent, gv, LaserJobTracker(self), *args, **kwargs)

        self.initialize(self.getItemNames())


    def getItemNames(self) -> list:
        ''' Return the materials and thickness in a list. '''
        return LaserJobTracker(self).getMaterialAndThicknessList()


    def displayItem(self, material_name: str):
        ''' Display the material page and load content for the highlighted material. '''

        stacked_widget = self.window().findChild(
                QStackedWidget,
                'wachtrijMateriaalQStackedWidget')

        stacked_widget.findChild(ContentQListWidget).loadContent(material_name)
        # show materialPage in stackedWidget
        stacked_widget.setCurrentIndex(1)

    def refresh(self):
        ''' Initialise the material list widget. '''
        self.clear()
        self.initialize(self.getItemNames())



class LaserVerwerktJobsOverviewQListWidget(OverviewQListWidget):

    def __init__(self, parent: QWidget, *args, **kwargs):
        super().__init__(parent, gv, LaserJobTracker(self), *args, **kwargs)

        self.refresh()

    def refresh(self):
        ''' Initialise the list widget with jobs. '''
        self.clear()
        self.initialize(LaserJobTracker(self).getStaticAndDynamicJobNames(
            filter_jobs_on='status', filter_str='VERWERKT'))


class LaserAfgekeurdJobsOverviewQListWidget(OverviewQListWidget):

    def __init__(self, parent: QWidget, *args, **kwargs):
        super().__init__(parent, gv, LaserJobTracker(self), *args, **kwargs)

        self.refresh()

    def refresh(self):
        ''' Initialise the list widget with jobs. '''
        self.clear()
        self.initialize(LaserJobTracker(self).getStaticAndDynamicJobNames(
            filter_jobs_on='status', filter_str='AFGEKEURD'))

class LaserJobContentQListWidget(JobContentQListWidget):

    def __init__(self, parent: QWidget, *args, **kwargs):
        super().__init__(parent, gv, LaserJobTracker(self), *args, **kwargs)

        self.gv = gv

class LaserMaterialContentQListWidget(ContentQListWidget):

    def __init__(self, parent: QWidget, *args, **kwargs):
        super().__init__(parent, gv, LaserJobTracker(self), *args, **kwargs)

    def loadContent(self, item_name):
        self.clear()
        self.current_item_name = item_name

        self.parent().findChild(QLabel, 'materialQLabel').setText(item_name)

        material, thickness = split_material_name(item_name)

        laser_file_info_list = LaserJobTracker(
                self).getLaserFilesWithMaterialThicknessInfo(material, thickness)

        for (dxf_name, dxf_global_path, done) in laser_file_info_list:

            if not done:
                item = QListWidgetItem()
                item.setData(1, dxf_global_path)
                item.setFont(QFont('Cantarell', 14))

                # Indicate if done with emotico
                item.setText('❌ '+dxf_name)
                self.addItem(item)
