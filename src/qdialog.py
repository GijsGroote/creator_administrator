import os
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.uic import loadUi
from global_variables import gv


class SelectFileQDialog(QDialog):
    """ Select file dialog. """
    def __init__(self, parent, ui_global_path):
        super().__init__(parent)

        loadUi(ui_global_path, self)

        self.PasswordQLineEdit.textChanged.connect(self.check_password)

    def check_password(self):
        if self.PasswordQLineEdit.text() == gv['PASSWORD']:
            self.PasswordQLineEdit.setStyleSheet("background-color: rgba(0, 255, 0, 0.4);")
        else:
            self.PasswordQLineEdit.setStyleSheet("background-color: rgba(255, 0, 0, 0.4);")


