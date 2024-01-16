import sys
import os
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from requests.exceptions import ConnectionError


from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from global_variables import gv
from src.app import MainWindow
from laser_qdialog import (
        LaserImportFromMailQDialog, LaserFilesSelectQDialog,
        LaserFolderSelectQDialog, LaserFileInfoQDialog)
from src.qmessagebox import TimedQMessageBox

from src.worker import Worker
from src.loading_dialog import LoadingQDialog

from src.mail_manager import MailManager

class LaserMainWindow(MainWindow):
    def __init__(self, *args, **kwargs):
        ui_global_path = os.path.join(gv['UI_DIR_HOME'], 'laser_main_window.ui')
        super().__init__(ui_global_path, *args, **kwargs)


        # self.loading_dialog.show()
        # self.loading_dialog.hide()

        self.threadpool = gv['THREAD_POOL']
        # print(f' this threadpool is of type {type(self.threadpool)}')

        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_P), self).activated.connect(self.disp_message_worker)


        self.valid_msgs = []

        # menu bar actions
        self.importFromMailQAction.triggered.connect(self.importFromMailAction)
        self.selectFilesQAction.triggered.connect(self.selectFilesAction)
        self.selectFoldersQAction.triggered.connect(self.selectFoldersAction)


    def disp_message_worker(self):

        message_worker = Worker(self.disp_message_box)
        self.threadpool.start(message_worker)
        print(f"this shoudl be prented immeat")

    def disp_message_box(self):
        print(f"haahhaha")  
        TimedQMessageBox(text='hjo ther')


    def importFromMailAction(self):

        # self.valid_msgs = self.getNewValidMails()
        # self.openImportFromMailDialog()


        # TODO: the error function should handle how upon error the message if displayed to the user.

        self.loading_dialog = LoadingQDialog(self, gv)
        self.loading_dialog.show()

        # create workers
        get_mail_worker = Worker(self.getNewValidMails)
        get_mail_worker.signals.finished.connect(self.loading_dialog.accept)
        get_mail_worker.signals.result.connect(self.openImportFromMailDialog)
        self.valid_msgs = self.threadpool.start(get_mail_worker)

        # self.threadpool.start(self.loading_widget_worker)

    def openImportFromMailDialog(self):
        ''' open import from mail dialog. '''

        if len(self.valid_msgs) == 0:
            TimedQMessageBox(text='No new mails', parent=self)
        else:

            dialog = LaserImportFromMailQDialog(self, self.valid_msgs)
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
                            TimedQMessageBox(text=f'{subfolder_global_path} contains a folder '\
                                f'{item_global_path} which is skipped' ,
                                parent=self, icon=QMessageBox.Warning)
                            continue

                        if item_global_path.endswith(gv['ACCEPTED_EXTENSIONS']):
                            files_in_subfolder_global_paths.append(item_global_path)
                            subfolder_contains_laser_file = True

                    if subfolder_contains_laser_file:
                        folders_global_paths_list.append(files_in_subfolder_global_paths)
                        jobs_names_list.append(project_name+'_'+os.path.basename(subfolder))
                    else:
                        TimedQMessageBox(text=f'No laser file found in {subfolder_global_path}'\
                                f'skip this subfolder' ,
                                parent=self, icon=QMessageBox.Warning)

            LaserFileInfoQDialog(self, jobs_names_list, folders_global_paths_list).exec_()
        # refresh all laser job tabs
        qlist_widgets = self.findChildren(QListWidget)
        for list_widget in qlist_widgets:
            list_widget.refresh()


    def getNewValidMails(self):
        ''' Return new valid mails. '''

        try:
            self.mail_manager = MailManager(gv)
            msgs = self.mail_manager.getNewEmails()

        except ConnectionError as e:
            TimedQMessageBox(
                    text=f'Error getting mails becuase: {str(e)}',
                    parent=self, icon=QMessageBox.Critical)
            return
        except Exception as e:
            TimedQMessageBox(
                    text=f'Error: {str(e)}',
                    parent=self, icon=QMessageBox.Critical)
            return

        valid_msgs = [msg for msg in msgs if self.mail_manager.isMailAValidJobRequest(msg)]

        if len(msgs) > len(valid_msgs):
            it_or_them = 'it' if len(msgs) - len(valid_msgs) == 1 else 'them'
            TimedQMessageBox(
                    text=f'{len(msgs)-len(valid_msgs)} invalid messages '\
                    f'detected, respond to {it_or_them} manually.',
                    parent=self, icon=QMessageBox.Warning)

        self.valid_msgs = valid_msgs
    
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    laser_window = LaserMainWindow()
    laser_window.show()
    app.exec_()
