
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
        QPushButton, QFileDialog,
        QShortcut)

from jobs_qlist_widget import JobContentQListWidget

class LaserKlaarQPushButton(QPushButton):

    def __init__(self, *args, **kwargs):
        QPushButton.__init__(self, *args, **kwargs)
        self.clicked.connect(self.on_click)
 
    def on_click(self):
        job_name = self.parent().findChild(JobContentQListWidget).current_job_name

        print(f'laser klaar {job_name}')

class MateriaalKlaarQPushButton(QPushButton):

    def __init__(self, *args, **kwargs):
        QPushButton.__init__(self, *args, **kwargs)
        self.clicked.connect(self.on_click)
 
    def on_click(self):
        job_name = self.parent().findChild(JobContentQListWidget).current_job_name

        print(f'Materiaal klaarlaser klaar {job_name}')


class AfgekeurdQPushButton(QPushButton):

    def __init__(self, *args, **kwargs):
        QPushButton.__init__(self, *args, **kwargs)
        self.clicked.connect(self.on_click)


    def on_click(self):
        job_name = self.parent().findChild(JobContentQListWidget).current_job_name

        print(f'laser afgekeurddd {job_name}')

class OverigQPushButton(QPushButton):

    def __init__(self, *args, **kwargs):
        QPushButton.__init__(self, *args, **kwargs)
        self.clicked.connect(self.on_click)
 
        # shortcut on Esc button
        QShortcut(QKeySequence(Qt.Key_Escape), self).activated.connect(self.on_click)


    def on_click(self):
        job_name = self.parent().findChild(JobContentQListWidget).current_job_name
        print(f'De overig knop is gedrukt {job_name}')

