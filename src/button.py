from os.path import expanduser

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
        QPushButton, QFileDialog, QStackedWidget,
        QShortcut)

from jobs_qlist_widget import JobContentQListWidget, JobsQListWidget




class JobsQPushButton(QPushButton):
    ''' Parent class for all buttons that update job status
            such as laser klaar, gesliced. '''


    def __init__(self, *args, **kwargs):
        QPushButton.__init__(self, *args, **kwargs)


    def refreshAllQListWidgets(self):

        self.parent().parent().setCurrentIndex(0)        # show list of jobs in tabs

        # for qstacked_widget in qstacked_widgets:
            # qstacked_widget.setCurrentIndex(0)

        qlist_widgets = self.window().findChildren(JobsQListWidget)
        # refresh all QListWidgets that contain jobs
        for list_widget in qlist_widgets:
            list_widget.refresh()


    def getCurrentStaticJobName(self) -> str:
        return self.parent().findChild(JobContentQListWidget).current_job_name


class BackQPushButton(QPushButton):

    def __init__(self, *args, **kwargs):
        QPushButton.__init__(self, *args, **kwargs)
        self.clicked.connect(self.on_click)
 
        # shortcut on Esc button
        QShortcut(QKeySequence(Qt.Key_Escape), self).activated.connect(self.on_click)

    def on_click(self):
        self.parent().parent().setCurrentIndex(0) 

class SelectFolderQPushButton(QPushButton):

    def __init__(self, parent=None):
        QPushButton.__init__(self, parent)
        self.folder_global_path = None
        self.clicked.connect(self.on_click)

    def on_click(self):
        self.folder_global_path = QFileDialog.getExistingDirectory(self,
            'Select Folder',
            expanduser('~'),
            QFileDialog.ShowDirsOnly)

        folder_name_short = self.folder_global_path

        max_char_length = 50

        if len(folder_name_short) > max_char_length:
            folder_name_short = '../'+folder_name_short[-max_char_length+3:]

        self.setText(folder_name_short)

