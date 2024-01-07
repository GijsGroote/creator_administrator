import os
import re
from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets, uic
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from typing import Tuple
import datetime
from src.qdialog import ImportFromMailQDialog, SelectFileQDialog
from src.mail_manager import MailManager
from PyQt5.QtCore import QTimer


class TimedQMessageBox(QMessageBox):

    def __init__(self, parent=None, text='setthis', *args, **kwargs):
        QMessageBox.__init__(self, *args, **kwargs)

        self.setText(text)

        self.setStandardButtons(QMessageBox.NoButton)
        self.timeout = 3
        self.timer = QTimer(self)
        self.timer.setInterval(1000*self.timeout)
        self.timer.start()
        self.timer.timeout.connect(self.accept)



        self.show() # needed to move to top right
        self.moveToTopRightCorner(parent)
        # self.exec_()
        self.setIcon(QMessageBox.Question)
        self.setDefaultButton(QMessageBox.Retry)

        print(f"ha")
        # self.exec_()



    def moveToTopRightCorner(self, parent):

        parent_geometry = parent.geometry()
        parent_right_x = parent_geometry.x() + parent_geometry.width()
        parent_top_y = parent_geometry.y()
        margin = 0

        self.move(parent_right_x-self.geometry().width()-30-margin, parent_top_y+38+margin)

