import sys
import os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QListWidget, QLabel, QListWidgetItem

from global_variables import gv
from src.app import MainWindow
from select_file import create_laser_jobs
from laser_qdialog import LaserSelectFileQDialog

class AllJobsQListWidget(QListWidget):

    def __init__(self, *args, **kwargs):
        QListWidget.__init__(self, *args, **kwargs)

        self.addItems(os.listdir(gv['JOBS_DIR_HOME']))


