# from PyQt5 import Qt
import os
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QDialog
from PyQt6.QtCore import Qt
from PyQt6.uic import loadUi

class LoadingQDialog(QDialog):

    def __init__(self, parent, gv: dict, *args, text=None, **kwargs):
        super().__init__(parent, *args, **kwargs)

        loadUi(os.path.join(gv['REPO_DIR_HOME'], 'ui/loading_dialog.ui'), self)
        if text is not None:
            self.label.setText(text)
            self.label.setFont(QFont('Cantarell', 14))
            
        

        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.CustomizeWindowHint)

        self.show()
        parent_geometry = parent.frameGeometry()
        self.setFixedSize(3*parent_geometry.width()//4, 3*parent_geometry.height()//4)

        self.move(parent.width()//2 - self.width()//2, parent.height()//2 - self.height()//2)
        self.setStyleSheet(f'background-color: {gv["GOOD_COLOR_RGBA"]};')
