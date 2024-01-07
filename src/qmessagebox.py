from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class TimedQMessageBox(QMessageBox):

    def __init__(self, text='setthis', parent=None, icon=QMessageBox.Information, *args, **kwargs):
        QMessageBox.__init__(self, *args, **kwargs)

        self.setText(text)
        self.timeout = 10
        self.timer = QTimer(self)
        self.timer.setInterval(1000*self.timeout)
        self.timer.start()
        self.timer.timeout.connect(self.accept)

        self.setIcon(icon)

        # self.show() # needed to move to top right
        # self.moveToTopRightCorner(parent)
        self.setIcon(QMessageBox.Question)
        self.exec_()

    def moveToTopRightCorner(self, parent):
        parent_geometry = parent.geometry()
        parent_right_x = parent_geometry.x() + parent_geometry.width()
        parent_top_y = parent_geometry.y()
        margin = 0

        self.move(parent_right_x-self.geometry().width()-30-margin, parent_top_y+38+margin)
