import os

from PyQt5.QtWidgets import QApplication, QWidget, QDialog, QMainWindow, QPushButton, QTabWidget
from PyQt5.uic import loadUi

from global_variables import gv

from src.jobsqtabwidget import JobsQTabWidget

class LaserJobsQTabWidget(QTabWidget):

    def __init__(self, *args, **kwargs):
        ui_global_path = os.path.join(gv['REPO_DIR_HOME'], 'laser/ui/jobs_tabs_window.ui')
        QTabWidget.__init__(self, *args, **kwargs)



        # loadUi(ui_global_path, self.allJobsTab)


        childeren = self.findChildren(QWidget)
        print('children of LaserJobsQWidget')
        for child in childeren:
            print(child)


        # childeren = parent.findChildren(QWidget)
        # print('children of parent')
        # for child in childeren:
        #     print(child)

        # self.allJobsTab.setTabText('set online')
        # self.wachtrijTab.setTabText('set online')
        # self.wachtrijMateriaalTab.setTabText('set online')
        # self.verwerktTab.setTabText('set online')
        # self.afgekeurdTab.setTabText('set online')

        
        # jobs = os.listdir(gv['JOBS_DIR_HOME'])
        # for job in jobs:
        #     self.addTab(QPushButton(job, self), 'All')


    def refreshJobs(self):
        ''' Refresh jobs in tab. '''


