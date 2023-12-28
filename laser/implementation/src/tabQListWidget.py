import os

from PyQt5.QtWidgets import QListWidget
from PyQt5 import uic

class AllJobsQListWidget(QListWidget):

    def __init__(self, *args, **kwargs):
        QListWidget.__init__(self, *args, **kwargs)

        self.addItem("sparrow")
        self.addItem("robin")
        self.addItem("crow")
        self.addItem("raven")
        self.addItem("woodpecker")
        self.addItem("hummingbird")



