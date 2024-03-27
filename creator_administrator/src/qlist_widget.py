import os
import abc

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut, QFont
from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QLabel, QWidget

from src.directory_functions import open_file
from src.job_tracker import JobTracker

class OverviewQListWidget(QListWidget):
    ''' Overview of multiple items in a list. '''

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # shortcut on the Enter key
        QShortcut(QKeySequence(Qt.Key.Key_Return), self).activated.connect(self.itemEnterPressed)

        self.itemDoubleClicked.connect(self.itemIsDoubleClicked)


    # Some child classes overwrite this function
    def displayItem(self, item_name: str):
        ''' Display the job content page. '''

        self.parent().parent().setCurrentIndex(1)
        # find the JobContentQListWidget by searching for QListWidget (search for JobContentQListWidget returns None)
        self.parent().parent().currentWidget().findChild(QListWidget).loadContent(item_name)

    def initialize(self, item_names: list):
        ''' Initialize with list of items. '''
        self.addNoItemsLabel()

        if len(item_names) == 0:
            self.parent().no_items_label.show()
        else:
            self.parent().no_items_label.hide()
            
        for item_name in item_names:

            item = QListWidgetItem()
            if isinstance(item_name, tuple):
                (item_data, item_name) = item_name
            else:
                item_data = item_name

            item.setData(1, item_data)
            item.setText(item_name)
            self.addItem(item)
            item.setFont(QFont('Cantarell', 14))

    def addNoItemsLabel(self):
        ''' Add no_items_label if it is not yet present. '''
        if not hasattr(self.parent(), 'no_items_label'):
            self.parent().no_items_label = QLabel(text='No Jobs to Display',
                                    parent=self.parent())
            self.parent().no_items_label.setGeometry(
                (self.parent().geometry().width()-self.parent().no_items_label.geometry().width())//2, 
                (self.parent().geometry().height()-self.parent().no_items_label.geometry().width())//2,
                300, 20) 

    def itemEnterPressed(self):
        ''' Handle press on current item. '''
        current_item = self.currentItem()
        if current_item is not None:
            self.displayItem(current_item.data(1))

    # itemDoubleClicked already defined, call it itemIsDoubleClicked
    def itemIsDoubleClicked(self, clicked_item):
        ''' Display the content of the item clicked. '''
        self.displayItem(clicked_item.data(1))

    @abc.abstractmethod
    def refresh(self):
        ''' Initialise the list widget with jobs. '''

class ContentQListWidget(QListWidget):
    ''' Content . '''

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.current_item_name = None

        # shortcut for the Enter button
        QShortcut(QKeySequence(Qt.Key.Key_Return), self).activated.connect(self.itemEnterPressed)
        self.itemDoubleClicked.connect(self.fileDoubleClicked)

    def refresh(self):
        if self.current_item_name is not None:
            self.clear()
            self.loadContent(self.current_item_name)

    def itemEnterPressed(self):
        current_file = self.currentItem()
        
        if current_file is not None:
            self.fileDoubleClicked(current_file)

    def fileDoubleClicked(self, clicked_file):
        ''' Double click on a file (or item) to open it. '''
        open_file(clicked_file.data(1))

    @abc.abstractmethod
    def loadContent(self, item_name):
        ''' load the content. '''

class JobContentQListWidget(ContentQListWidget):

    def __init__(self, parent: QWidget, job_tracker: JobTracker, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.job_tracker = job_tracker

    def loadContent(self, item_name):
        self.clear()
        self.current_item_name = item_name


        job_dict = self.job_tracker.getJobDict(item_name)

        if job_dict is not None:
            self.parent().findChild(QLabel).setText(job_dict['dynamic_job_name'])

            for file in os.listdir(job_dict['job_folder_global_path']):

                item = QListWidgetItem()
                item.setData(1, os.path.join(
                    job_dict['job_folder_global_path'], file))

                # check if it is a laser file, indicate if it is done with an emoticon
                for laser_file_dict in [val for key,val in job_dict['make_files'].items() if file in key]:
                    # ☑️✅✔️❎
                    if laser_file_dict['done']:
                        file ='✅ '+file
                    else:
                        file ='❎ '+file

                item.setText(file)
                item.setFont(QFont('Cantarell', 14))
                self.addItem(item)


class OptionsQListWidget(QListWidget):
    ''' Content . '''

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

    # Do nothing for options QlistWidget refresh (but is should be callable)
    def refresh(self):
        pass
