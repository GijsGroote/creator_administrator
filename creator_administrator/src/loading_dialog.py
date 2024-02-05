# from PyQt5 import Qt
import os
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6 import uic

class LoadingQDialog(QDialog):

    def __init__(self, parent, gv: dict, text=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        uic.loadUi(os.path.join(gv['REPO_DIR_HOME'], 'ui/loading_dialog.ui'), self)
        if text is not None:
            self.label.setText(text)

        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.CustomizeWindowHint)

        self.show()
        parent_geometry = parent.frameGeometry()
        self.setFixedSize(3*parent_geometry.width()//4, 3*parent_geometry.height()//4)

        self.move(parent.width()//2 - self.width()//2, parent.height()//2 - self.height()//2)
        self.setStyleSheet("background-color: rgba(0, 255, 0, 0.4);")
