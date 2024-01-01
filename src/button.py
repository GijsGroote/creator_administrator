from os.path import expanduser

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
        QPushButton, QFileDialog,
        QShortcut,

        )

class BackQPushButton(QPushButton):

    def __init__(self, *args, **kwargs):
        QPushButton.__init__(self, *args, **kwargs)
        self.clicked.connect(self.on_click)
 
        # shortcut on Esc button
        QShortcut(QKeySequence(Qt.Key_Escape), self).activated.connect(self.on_click)


    def on_click(self):
        print('clicked on back button')
        self.parent().parent().setCurrentIndex(0) 

class SelectFolderQPushButton(QPushButton):

    def __init__(self, parent=None):
        QPushButton.__init__(self, parent)
        self.folder_global_path = None
        self.clicked.connect(self.on_click)

    def on_click(self):
        self.folder_global_path = QFileDialog.getExistingDirectory(self,
            'Select Folder',
            expanduser('~'),
            QFileDialog.ShowDirsOnly)

        folder_name_short = self.folder_global_path

        max_char_length = 50

        if len(folder_name_short) > max_char_length:
            folder_name_short = '../'+folder_name_short[-max_char_length+3:]

        self.setText(folder_name_short)

