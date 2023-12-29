import os
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox

from global_variables import gv
from src.qdialog import SelectFileQDialog

class LaserSelectFileQDialog(SelectFileQDialog):
    """ Select file dialog. """
    def __init__(self, parent=None):
        ui_global_path = os.path.join(gv['REPO_DIR_HOME'], 'laser/ui/select_file_dialog.ui')
        super().__init__(parent, ui_global_path)

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

