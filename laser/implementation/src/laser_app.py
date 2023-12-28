import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton
from PyQt5.QtGui import QKeyEvent
# from dialog import Ui_Dialog
from PyQt5 import uic
from PyQt5.uic import loadUi
from global_variables import gv

from myWidgets import JumpButton
from jobsQTabsWidget import JobsQTabsWidget

from app import MainWindow
from select_file import SelectFile

from select_file import SelectFileQDialog

class LaserMainWindow(MainWindow):

    def __init__(self, *args, **kwargs):
        MainWindow.__init__(self, *args, **kwargs)

        # menu bar actions
        self.ActionImportFromMail.triggered.connect(self.onActionImportFromMail)
        self.ActionSelectFile.triggered.connect(self.onActionSelectFileclicked)

    def onActionImportFromMail(self):
        print('please import mail now')

    def onActionSelectFileclicked(self):
        dlg = SelectFileQDialog(self)
        dlg.exec()

        print('please select a file now')


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    laser_window = LaserMainWindow()
    laser_window.show()
    app.exec_()
