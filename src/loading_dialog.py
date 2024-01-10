# from PyQt5 import Qt
import os
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from src.app import get_main_window

class LoadingQDialog(QDialog):

    def __init__(self, parent, gv: dict, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.CustomizeWindowHint)


        self.setStyleSheet("background-color: rgba(0, 255, 0, 0.4);")
        layout = QVBoxLayout()

        self.label = QLabel('Loading...', self)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)



    def centerOnMainWindow(self):
        main_window = get_main_window(self)
        if main_window is not None:
            self.setGeometry(main_window.frameGeometry())
            # self.setGeometry(main_geometry.x() + main_geometry.width()//2 - self.width(),
            #                  main_geometry.y() + main_geometry.height()//2 - self.height(),
            #             480, 480)
