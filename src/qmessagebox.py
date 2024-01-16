from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from src.worker import Worker

class TimedQMessageBox(QMessageBox):

    def __init__(self, parent=None, text='setthis', icon=QMessageBox.Information, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.setText(text)
        self.timeout = 5
        self.timer = QTimer(self)
        self.timer.setInterval(1000*self.timeout)
        self.timer.start()
        self.timer.timeout.connect(self.accept)

        self.setIcon(icon)

        # self.show() # needed to move to top right
        self.exec_()


        # message_worker = Worker(self.exec_)

        # parent.threadpool.start(message_worker)


    def moveToTopRightCorner(self, parent):
        parent_geometry = parent.geometry()
        parent_right_x = parent_geometry.x() + parent_geometry.width()
        parent_top_y = parent_geometry.y()
        margin = 0

        self.move(parent_right_x-self.geometry().width()-30-margin, parent_top_y+38+margin)

class JobFinishedMessageBox(QMessageBox):

    def __init__(self, parent, text='setthis', icon=QMessageBox.Information, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.setText(text)
        self.addButton(QMessageBox.Ok)
        self.setIcon(icon)
        self.exec_()

class YesOrNoMessageBox(QMessageBox):

    def __init__(self, parent, text='setthis', icon=QMessageBox.Question, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.setText(text)
        self.addButton(QMessageBox.No)
        self.addButton(QMessageBox.Yes)
        self.setDefaultButton(QMessageBox.Yes)
        self.setIcon(icon)

