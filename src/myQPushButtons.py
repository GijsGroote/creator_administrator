
import os
from os.path import expanduser
from PyQt5.QtWidgets import QPushButton, QFileDialog

class SelectFolderButton(QPushButton):

    def __init__(self, parent=None):
        QPushButton.__init__(self, parent)
        self.clicked.connect(self.on_click)

    def on_click(self):

        folder_name = QFileDialog.getExistingDirectory(self,
            'Select Folder',
            expanduser('~'),
            QFileDialog.ShowDirsOnly)

        max_char_length = 20

        if 3 >= len(folder_name) < max_char_length:
            folder_name = '../'+folder_name[-max_char_length+3:]
        self.setText(folder_name)

