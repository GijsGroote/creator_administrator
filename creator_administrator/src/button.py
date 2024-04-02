import os
import abc

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtWidgets import QPushButton, QFileDialog, QMenu, QWidget

from src.directory_functions import open_folder
from src.qlist_widget import ContentQListWidget
from src.job_tracker import JobTracker


class JobsQPushButton(QPushButton):
    ''' Parent class for all buttons that update job status
            such as laser klaar, gesliced. '''

    def __init__(self, parent: QWidget, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

    def getCurrentItemName(self) -> str:
        content_qlist_widget = self.parent().findChild(ContentQListWidget)
        if content_qlist_widget is None:
            raise ValueError('ContentQListWidget is None which should be impossible')

        return content_qlist_widget.current_item_name


class OptionsQPushButton(JobsQPushButton):

    def __init__(self, parent: QWidget, gv: dict, job_tracker: JobTracker, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.job_tracker = job_tracker

        self.menu = QMenu()


        copy_todo_action = self.menu.addAction('Copy Files to TODO folder', self.copyMakeFilesTo)
        copy_todo_action.setToolTip('Shortcut: Ctrl+T')

        QShortcut(QKeySequence('Ctrl+T'), self).activated.connect(self.copyMakeFilesTo)
        self.menu.setToolTipsVisible(True)

        if gv['DARK_THEME']:
            self.menu.setStyleSheet('''QToolTip {
                           background-color: black;
                           color: white;
                           border: black solid 1px
                           }''')

        # This is a trick because self.objectName() is not known for few milisecs
        self.objectNameChanged.connect(self.initialize)

    @abc.abstractmethod
    def initialize(self):
        ''' Initialize button. '''

    def moveJobToWachtrij(self):
        job_name = self.getCurrentItemName()
        self.job_tracker.markFilesAsDone(job_name=job_name, file_global_path=None, done=False, all_files_done=True)
        self.moveJobTo('WACHTRIJ')
        self.window().refreshAllWidgets()
        self.parent().parent().setCurrentIndex(0)

    def moveJobToAfgekeurd(self):
        self.moveJobTo('AFGEKEURD')

    def moveJobToVerwerkt(self):
        self.moveJobTo('VERWERKT')

    def moveJobTo(self, new_status):
        job_name = self.getCurrentItemName()
        self.job_tracker.updateJobKey('status', job_name, new_status)
        self.window().refreshAllWidgets()
        self.parent().parent().setCurrentIndex(0)

    def openInFileExplorer(self):
        job_folder_global_path = self.job_tracker.getJobDict(
                self.getCurrentItemName())['job_folder_global_path']
        open_folder(job_folder_global_path)

    def deleteJob(self):
        job_name = self.getCurrentItemName()
        self.job_tracker.deleteJob(job_name)

        self.window().refreshAllWidgets()

        # show list of jobs in tabs
        self.parent().parent().setCurrentIndex(0)


    @abc.abstractmethod
    def copyMakeFilesTo(self):
        '''Copy the make files from a job to the todo folder. '''


class BackQPushButton(QPushButton):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.clicked.connect(self.on_click)

        # shortcut on Esc button
        QShortcut(QKeySequence(Qt.Key.Key_Escape), self).activated.connect(self.on_click)

    def on_click(self):
        self.parent().parent().setCurrentIndex(0)


class SelectFilesQPushButton(QPushButton):
    ''' Select multiple files from file system. '''

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.files_global_paths = []
        self.clicked.connect(self.on_click)


    def on_click(self):
      # Get list of selected file paths
        files_paths, _ = QFileDialog.getOpenFileNames(
            self,
            'Select Files',
            os.path.expanduser('~'),
            'All Files (*)')

        self.files_global_paths = list(dict.fromkeys(self.files_global_paths + files_paths))

        selected_files_str = 'Selected Files:'

        for file_global_path in self.files_global_paths:
            selected_files_str += f'\n{os.path.basename(file_global_path)}'

        self.setText(selected_files_str)

class SelectFileQPushButton(QPushButton):
    ''' Select a single file from file system. '''

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.clicked.connect(self.on_click)

        self.start_dir_global_path = os.path.expanduser('~')
        self.file_global_path = None

    def setStartingDirectory(self, start_dir_global_path: str):
        ''' Set the starting directory. '''
        assert os.path.exists(start_dir_global_path), f"{start_dir_global_path} does not exist"
        assert os.path.isdir(start_dir_global_path), f"{start_dir_global_path} is not a directory"
        self.start_dir_global_path = start_dir_global_path


    def on_click(self):
      # Get list of selected file paths

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            'Select File',
            self.start_dir_global_path,
            'All Files (*)')

        self.setText(str(file_path))# TODO: shorten this path
        self.file_global_path = file_path


class SelectFolderQPushButton(QPushButton):
    ''' Select a folder from file system. '''

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.folder_global_path = None
        self.clicked.connect(self.on_click)
        self.start_dir_global_path = os.path.expanduser('~')

    def setStartingDirectory(self, start_dir_global_path: str):
        ''' Set the starting directory. '''
        assert os.path.exists(start_dir_global_path), f"{start_dir_global_path} does not exist"
        assert os.path.isdir(start_dir_global_path), f"{start_dir_global_path} is not a directory"
        self.start_dir_global_path = start_dir_global_path

    def on_click(self):
        self.folder_global_path = QFileDialog.getExistingDirectory(self,
            'Select Folder',
            self.start_dir_global_path,
            QFileDialog.Option.ShowDirsOnly)

        folder_name_short = self.folder_global_path

        max_char_length = 50

        if len(folder_name_short) > max_char_length:
            folder_name_short = '../'+folder_name_short[-max_char_length+3:]

        self.setText(folder_name_short)

