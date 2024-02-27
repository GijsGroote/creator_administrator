import sys
import os
from functools import partial
from PyQt6 import QtWidgets
from PyQt6 import QtCore
from requests.exceptions import ConnectionError
import time

import traceback 
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from global_variables import gv
from src.app import MainWindow
from src.qmessagebox import InfoQMessageBox, WarningQMessageBox, ErrorQMessageBox, TimedMessage
from src.worker import Worker
from src.loading_dialog import LoadingQDialog
from src.mail_manager import MailManager
from unidecode import unidecode
from laser_job_tracker import LaserJobTracker
from laser_settings_dialog import LaserSettingsQDialog
from laser_qdialog import (
        LaserImportFromMailQDialog, LaserFilesSelectQDialog,
        LaserFolderSelectQDialog, LaserFileInfoQDialog)
from src.threaded_mail_manager import ThreadedMailManager

# ensure that win32com is imported after creating an executable with pyinstaller
# from win32com import client

class LaserMainWindow(MainWindow):
    def __init__(self, *args, **kwargs):
        ui_global_path = os.path.join(gv['LOCAL_UI_DIR'], 'laser_main_window.ui')
        super().__init__(ui_global_path, gv, *args, **kwargs)

        self.valid_msgs = []
        self.threadpool = gv['THREAD_POOL']

        # call job tracker twice to enforce healthy job log
        self.job_tracker = LaserJobTracker(parent_widget=self)
        self.job_tracker.checkHealth()

        self.refreshAllWidgets()


        # menu bar actions
        self.importFromMailAction.triggered.connect(self.handleNewValidMails)
        self.selectFilesAction.triggered.connect(self.openSelectFilesDialog)
        self.selectFoldersAction.triggered.connect(self.openSelectFolderDialog)


        self.menuSettings.setToolTipsVisible(True)
        self.editSettingsAction.triggered.connect(self.openEditSettingsDialog)
        self.checkHealthAction.triggered.connect(self.checkHealth)


        # Delete this and showTimedMessage as well
        # QShortcut(QKeySequence("Ctrl+H"), self).activated.connect(self.showTimedMessage)

    # def showTimedMessage(self):
    #     print(f"shwo times messages boyo")

    #     TimedMessage(gv, self, text='Laser job {self.temp_job_name} created')
        

    def handleNewValidMails(self):
        ''' Handle the new mails in the inbox. '''
        
        self.threaded_mail_manager = ThreadedMailManager(self, gv, dialog=LaserImportFromMailQDialog)
        # getValidmails gets mail and triggers openImportFromMailDialog
        self.threaded_mail_manager.getValidMailsFromInbox()
        


    def openSelectFilesDialog(self):
        ''' Open dialog to select multiple files. ''' 
        dialog = LaserFilesSelectQDialog(self)

        if dialog.exec() == 1:
            files_global_paths = dialog.selectFilesButton.files_global_paths
            job_name = dialog.projectNameQLineEdit.text()

            if len(files_global_paths) > 0:
                LaserFileInfoQDialog(self, [job_name], [files_global_paths]).exec()
            
        self.refreshAllWidgets()

    def openSelectFolderDialog(self):
        ''' Open dialog to select folder with multiple subfolders. ''' 
        dialog = LaserFolderSelectQDialog(self)

        if dialog.exec() == 1:
            folder_global_path = dialog.selectFolderButton.folder_global_path
            project_name = dialog.projectNameQLineEdit.text()
            folders_global_paths_list = []
            jobs_names_list = []
            for subfolder in os.listdir(folder_global_path):
                subfolder_global_path = os.path.join(folder_global_path, subfolder)

                if os.path.isdir(subfolder_global_path):
                    files_in_subfolder_global_paths = []
                    subfolder_contains_laser_file = False

                    try:
                        for item in os.listdir(subfolder_global_path):
                            item_global_path = os.path.join(subfolder_global_path, item)
                            if os.path.isdir(item_global_path):
                                WarningQMessageBox(gv, self, text=f'{subfolder_global_path} contains a folder '\
                                    f'{item_global_path} which is skipped' )
                                    
                                continue

                            if item_global_path.endswith(gv['ACCEPTED_EXTENSIONS']):
                                files_in_subfolder_global_paths.append(item_global_path)
                                subfolder_contains_laser_file = True

                        if subfolder_contains_laser_file:
                            folders_global_paths_list.append(files_in_subfolder_global_paths)
                            jobs_names_list.append(project_name+'_'+os.path.basename(subfolder))
                        else:
                            WarningQMessageBox(gv, self, text=f'No laser file found in {subfolder_global_path}'\
                                    f' skip this subfolder')
                    except Exception as exc:
                        ErrorQMessageBox(self, text=f'An Error Occured: {str(exc)}')
            
            if len(jobs_names_list) > 0:
                LaserFileInfoQDialog(self, jobs_names_list, folders_global_paths_list).exec()

        self.refreshAllWidgets()

    def openEditSettingsDialog(self):
        ''' Open dialog to edit the settings. '''
        LaserSettingsQDialog(self, gv).exec()

    def checkHealth(self):
        ''' Check health with tracker file. '''
        LaserJobTracker(self).checkHealth()
        self.refreshAllWidgets()
        TimedMessage(gv=gv, parent=self, text='System Healthy ;)')

    def refreshAllWidgets(self):
        ''' Refresh the widgets. '''
        # refresh all laser job tabs
        qlist_widgets = self.findChildren(QListWidget)
        for list_widget in qlist_widgets:
            list_widget.refresh()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    laser_window = LaserMainWindow()
    laser_window.show()
    app.exec()
