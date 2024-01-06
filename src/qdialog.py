import os
from functools import partial
from PyQt5 import uic
from PyQt5.QtWidgets import (QDialog, QMessageBox,
                             QDialogButtonBox, QShortcut)

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.uic import loadUi

from global_variables import gv


class ImportFromMailQDialog(QDialog):
    """ Import from mail dialog. """
    def __init__(self, parent, ui_global_path, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        loadUi(ui_global_path, self)

        # shortcut on Esc button
        QShortcut(QKeySequence(Qt.Key_Escape), self).activated.connect(self.closeDialog)


    def closeDialog(self):
        ''' Close the dialog, press cancel. '''
        self.close()


class SelectFileQDialog(QDialog):
    """ Select file dialog. """
    def __init__(self, parent, ui_global_path, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        loadUi(ui_global_path, self)
        self.PasswordQLineEdit.textChanged.connect(partial(self.check_password, gv=gv))

        # shortcut on Esc button
        QShortcut(QKeySequence(Qt.Key_Escape), self).activated.connect(self.closeDialog)

    def check_password(self, gv: dict):
        if self.PasswordQLineEdit.text() == gv['PASSWORD']:
            self.PasswordQLineEdit.setStyleSheet("background-color: rgba(0, 255, 0, 0.4);")
        else:
            self.PasswordQLineEdit.setStyleSheet("background-color: rgba(255, 0, 0, 0.4);")

    def closeDialog(self):
        ''' Close the dialog, press cancel. '''
        self.close()
