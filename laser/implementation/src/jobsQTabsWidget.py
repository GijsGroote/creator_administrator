import os

from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton, QTabWidget

from PyQt5 import uic

from global_variables import gv

class JobsQTabsWidget(QTabWidget):

    def __init__(self, *args, **kwargs):
        QTabWidget.__init__(self, *args, **kwargs)

#         uic.loadUi(os.path.join(gv['REPO_DIR_HOME'], 'pmma-laser/implementation/ui/jobsTabsWindow.ui')

        jobs = os.listdir('/home/gijs/.laserhok_workflow/jobs/')


        
        self.addTab(QPushButton(jobs[0], self), 'All')
        self.addTab(QPushButton(jobs[1], self), 'Wachtrij')
        self.addTab(QPushButton('New Button', self) , 'Wachtrij Materiaal')
        self.addTab(QPushButton('another new button', self), 'Afgekeurd')
        self.addTab(QPushButton('another new button', self), 'Verwerkt')

