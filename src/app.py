import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton
from PyQt5.QtGui import QKeyEvent
from PyQt5 import uic

class MainWindow(QMainWindow):

    def __init__(self, ui_global_path, *args, **kwargs):
        QMainWindow.__init__(self, *args, **kwargs)
        uic.loadUi(ui_global_path, self)

    def keyPressEvent(self, event):
        ''' Handle shortcuts on main window. '''

        # close application on 'q' press
        if isinstance(event, QKeyEvent):
            if event.key() == Qt.Key_Q:
                self.close()

