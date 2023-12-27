import os

from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton, QTabWidget

from PyQt5 import uic

class JobsQTabsWidget(QTabWidget):

    def __init__(self, *args, **kwargs):
        QTabWidget.__init__(self, *args, **kwargs)
        jobsw = os.path.abspath('pmma-laser/implementation/functions/jobsTabsWindow.ui')

        uic.loadUi(jobsw, self)
        # self.setStyleSheet('background-color: orange')

#         button = QPushButton('New Button', self)
#         button.show()

#         self.addTab(button, 'wachtrij')
        # self.addTab('nog een wachtrij')


