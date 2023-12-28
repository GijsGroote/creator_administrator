
import os
from os.path import expanduser
from PyQt5.QtWidgets import QPushButton, QFileDialog

class SelectFolderButton(QPushButton):

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

