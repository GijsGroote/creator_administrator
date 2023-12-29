import os

from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton, QTabWidget

from PyQt5 import uic

from global_variables import gv

from tab_widget import JobsQTabWidget

class LaserJobsQTabWidget(JobsQTabWidget):

    def __init__(self, parent=None):
        ui_global_path = os.path.join(gv['REPO_DIR_HOME'], 'laser/ui/jobs_tabs_window.ui')
        super().__init__(parent, ui_global_path)


        jobs = os.listdir('/home/gijs/.laserhok_workflow/jobs/')


        
        self.addTab(QPushButton(jobs[0], self), 'All')
        self.addTab(QPushButton(jobs[1], self), 'Wachtrij')
        self.addTab(QPushButton('New Button', self) , 'Wachtrij Materiaal')
        self.addTab(QPushButton('another new button', self), 'Afgekeurd')
        self.addTab(QPushButton('another new button', self), 'Verwerkt')

