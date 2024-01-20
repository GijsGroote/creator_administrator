import sys
import os
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from requests.exceptions import ConnectionError
import time

import traceback 



from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from global_variables import gv
from src.app import MainWindow
from laser_qdialog import (
        LaserImportFromMailQDialog, LaserFilesSelectQDialog,
        LaserFolderSelectQDialog, LaserFileInfoQDialog)
from src.qmessagebox import TimedMessage, WarningQMessageBox, ErrorQMessageBox
from src.worker import Worker
from src.loading_dialog import LoadingQDialog
from unidecode import unidecode
from laser_job_tracker import LaserJobTracker

from src.mail_manager import MailManager

class LaserMainWindow(MainWindow):
    def __init__(self, *args, **kwargs):
        ui_global_path = os.path.join(gv['UI_DIR_HOME'], 'laser_main_window.ui')
        super().__init__(ui_global_path, *args, **kwargs)

        self.valid_msgs = []
        self.threadpool = gv['THREAD_POOL']

        self.job_tracker = LaserJobTracker(self)
        self.job_tracker.checkHealth(self)

        # menu bar actions
        self.importFromMailQAction.triggered.connect(self.importFromMailAction)
        self.selectFilesQAction.triggered.connect(self.selectFilesAction)
        self.selectFoldersQAction.triggered.connect(self.selectFoldersAction)


    def importFromMailAction(self):

        self.loading_dialog = LoadingQDialog(self, gv)
        self.loading_dialog.show()

        # create workers
        get_mail_worker = Worker(self.getNewValidMails)
        get_mail_worker.signals.finished.connect(self.loading_dialog.accept)
        get_mail_worker.signals.result.connect(self.openImportFromMailDialog)
        self.valid_msgs = self.threadpool.start(get_mail_worker)

    def openImportFromMailDialog(self, data):
        ''' open import from mail dialog. '''

        valid_msgs, status = data

        if len(status) != 0:
            for status_str in status:
                WarningQMessageBox(self, text=status_str)

        if len(valid_msgs) == 0:
            TimedMessage(self, text='No new valid job request in mail inbox')
        else:

            dialog = LaserImportFromMailQDialog(self, valid_msgs)
            dialog.exec_()


            # refresh all laser job tabs
            qlist_widgets = self.findChildren(QListWidget)
            for list_widget in qlist_widgets:
                list_widget.refresh()

    def selectFilesAction(self):
        ''' Open dialog to select multiple files. ''' 
        dialog = LaserFilesSelectQDialog(self)

        if dialog.exec_() == QDialog.Accepted:
            files_global_paths = dialog.selectFilesButton.files_global_paths
            job_name = dialog.projectNameQLineEdit.text()

            LaserFileInfoQDialog(self, [job_name], [files_global_paths]).exec_()
            
        # refresh all laser job tabs
        qlist_widgets = self.findChildren(QListWidget)
        for list_widget in qlist_widgets:
            list_widget.refresh()

    def selectFoldersAction(self):
        ''' Open dialog to select folder with multiple subfolders. ''' 
        dialog = LaserFolderSelectQDialog(self)

        if dialog.exec_() == QDialog.Accepted:
            folder_global_path = dialog.selectFolderButton.folder_global_path
            project_name = dialog.projectNameQLineEdit.text()
            folders_global_paths_list = []
            jobs_names_list = []

            for subfolder in os.listdir(folder_global_path):
                subfolder_global_path = os.path.join(folder_global_path, subfolder)

                if os.path.isdir(subfolder_global_path):
                    files_in_subfolder_global_paths = []
                    subfolder_contains_laser_file = False
                    for item in os.listdir(subfolder_global_path):
                        item_global_path = os.path.join(subfolder_global_path, item)
                        if os.path.isdir(item_global_path):
                            WarningQMessageBox(self, text=f'{subfolder_global_path} contains a folder '\
                                f'{item_global_path} which is skipped' )
                                
                            continue

                        if item_global_path.endswith(gv['ACCEPTED_EXTENSIONS']):
                            files_in_subfolder_global_paths.append(item_global_path)
                            subfolder_contains_laser_file = True

                    if subfolder_contains_laser_file:
                        folders_global_paths_list.append(files_in_subfolder_global_paths)
                        jobs_names_list.append(project_name+'_'+os.path.basename(subfolder))
                    else:
                        WarningQMessageBox(self, text=f'No laser file found in {subfolder_global_path}'\
                                f'skip this subfolder')

            LaserFileInfoQDialog(self, jobs_names_list, folders_global_paths_list).exec_()
        # refresh all laser job tabs
        qlist_widgets = self.findChildren(QListWidget)
        for list_widget in qlist_widgets:
            list_widget.refresh()


    def getNewValidMails(self):
        ''' Return new valid mails. '''

        try:
            return MailManager(gv).getNewValidMails()

        except ConnectionError as e:
            
            print('Error?')
            # ErrorQMessageBox(self,
            #         text=f'Error getting mails becuase: {str(e)}')
            return
        except Exception as e:
            print(f'Error: {str(e)}')
            traceback.print_exc() 

            # ErrorQMessageBox(self,
            #         text=f'Error: {str(e)}')
            return
        
    
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    laser_window = LaserMainWindow()
    laser_window.show()
    app.exec_()
