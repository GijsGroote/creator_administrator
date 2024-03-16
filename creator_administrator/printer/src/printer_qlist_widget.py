from PyQt6.QtWidgets import QStackedWidget, QTabWidget, QWidget

from src.qlist_widget import OverviewQListWidget, JobContentQListWidget
from printer_job_tracker import PrintJobTracker 

class PrintAllJobsOverviewQListWidget(OverviewQListWidget):

    def __init__(self, parent: QWidget, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.job_tracker = PrintJobTracker(self)

        self.widget_names ={'WACHTRIJ':
                                {'QStackedWidget': 'wachtrijQStackedWidget',
                                 'tab_widget_position': 1},
                            'GESLICED':
                                {'QStackedWidget': 'geslicedQStackedWidget',
                                 'tab_widget_position': 2},
                            'AAN_HET_PRINTEN':
                                {'QStackedWidget': 'printenQStackedWidget',
                                 'tab_widget_position': 3},
                            'VERWERKT':
                                {'QStackedWidget': 'printenQStackedWidget',
                                 'tab_widget_position': 4},
                            'AFGEKEURD':
                                {'QStackedWidget': 'afgekeurdQStackedWidget',
                                 'tab_widget_position': 5}}
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

class PrintWachtrijJobsOverviewQListWidget(OverviewQListWidget):

    def __init__(self, parent: QWidget, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.refresh()

    def refresh(self):
        ''' Initialise the list widget with jobs. '''
        self.clear()
        self.initialize(PrintJobTracker(self).getStaticAndDynamicJobNamesWithStatus('WACHTRIJ'))


class PrintGeslicedJobsOverviewQListWidget(OverviewQListWidget):

    def __init__(self, parent: QWidget, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.refresh()

    def refresh(self):
        ''' Initialise the list widget with jobs. '''
        self.clear()
        self.initialize(PrintJobTracker(self).getStaticAndDynamicJobNamesWithStatus('GESLICED'))



class PrintPrintenJobsOverviewQListWidget(OverviewQListWidget):

    def __init__(self, parent: QWidget, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.refresh()

    def refresh(self):
        ''' Initialise the list widget with jobs. '''
        self.clear()
        self.initialize(PrintJobTracker(self).getStaticAndDynamicJobNamesWithStatus('AAN_HET_PRINTEN'))


class PrintVerwerktJobsOverviewQListWidget(OverviewQListWidget):

    def __init__(self, parent: QWidget, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.refresh()

    def refresh(self):
        ''' Initialise the list widget with jobs. '''
        self.clear()
        self.initialize(PrintJobTracker(self).getStaticAndDynamicJobNamesWithStatus('VERWERKT'))


class PrintAfgekeurdJobsOverviewQListWidget(OverviewQListWidget):

    def __init__(self, parent: QWidget, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.refresh()

    def refresh(self):
        ''' Initialise the list widget with jobs. '''
        self.clear()
        self.initialize(PrintJobTracker(self).getStaticAndDynamicJobNamesWithStatus('AFGEKEURD'))

class PrintJobContentQListWidget(JobContentQListWidget):

    def __init__(self, parent: QWidget, *args, **kwargs):
        super().__init__(parent, PrintJobTracker(self), *args, **kwargs)

