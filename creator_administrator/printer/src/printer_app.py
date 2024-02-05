import sys
import os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog

from global_variables import gv
from src.app import MainWindow
# from select_file import create_laser_jobs
# from laser_qdialog import LaserSelectFileQDialog

class PrinterMainWindow(MainWindow):

    def __init__(self, *args, **kwargs):
        print(gv['UI_DIR_HOME'])
        ui_global_path = os.path.join(gv['UI_DIR_HOME'], 'printer_main_window.ui')
        MainWindow.__init__(self, ui_global_path, *args, **kwargs)

        # menu bar actions
        self.ActionImportFromMail.triggered.connect(self.onActionImportFromMail)
        self.ActionSelectFile.triggered.connect(self.onActionSelectFileclicked)

    def onActionImportFromMail(self):
        print('please import mail now')

    # def onActionSelectFileclicked(self):
    #     # dialog = PrinterSelectFileQDialog(self)

    #     if dialog.exec_() == QDialog.Accepted:
    #         folder_global_path = dialog.selectFolderButton.folder_global_path
    #         project_name = dialog.projectNameQLineEdit.text()
    #         print(f'the folder is {folder_global_path} and pj {project_name}')
    #         create_laser_jobs(folder_global_path, project_name)
    

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    printer_window = PrinterMainWindow()
    printer_window.show()
    app.exec_()
