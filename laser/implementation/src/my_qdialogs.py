
import os
from PyQt5 import uic
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QDialog, QMessageBox

from global_variables import gv


class SelectFileQDialog(QDialog):
    """ Select file dialog. """
    def __init__(self, parent=None):
        super().__init__(parent)
        # Load the dialog's GUI
        loadUi(os.path.join(gv['REPO_DIR_HOME'], 'laser/implementation/ui/select_file_dialog.ui'), self)

        self.PasswordQLineEdit.textChanged.connect(self.check_password)
        self.buttonBox.accepted.connect(self.validate)


    def validate(self):
        if self.PasswordQLineEdit.text() != gv['PASSWORD']:
            dlg = QMessageBox(self)
            dlg.setText('Password Incorrect')
            button = dlg.exec()
            return

        if self.selectFolderButton.folder_global_path is None:
            dlg = QMessageBox(self)
            dlg.setText('Select a Folder')
            button = dlg.exec()
            return

        if len(self.ProjectNameQLineEdit.text()) == 0:
            dlg = QMessageBox(self)
            dlg.setText('Provide a Project Name')
            button = dlg.exec()
            return

        self.accept()


    def check_password(self):
        if self.PasswordQLineEdit.text() == gv['PASSWORD']:
            self.PasswordQLineEdit.setStyleSheet("background-color: rgba(0, 255, 0, 0.4);")
        else:
            self.PasswordQLineEdit.setStyleSheet("background-color: rgba(255, 0, 0, 0.4);")


