import sys
import os

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QListWidget

from global_variables import gv

from src.app import MainWindow
from src.qmessagebox import WarningQMessageBox, TimedMessage
from src.threaded_mail_manager import ThreadedMailManager
from src.qdialog import FilesSelectQDialog, FolderSelectQDialog

from laser_job_tracker import LaserJobTracker
from laser_settings_dialog import LaserSettingsQDialog
from laser_qdialog import CreateLaserJobsFromFileSystemQDialog, CreateLaserJobsFromMailQDialog

# ensure that win32com is imported after creating an executable with pyinstaller
# from win32com import client

class LaserMainWindow(MainWindow):
    def __init__(self, *args, **kwargs):
        ui_global_path = os.path.join(gv['LOCAL_UI_DIR'], 'laser_main_window.ui')
        super().__init__(ui_global_path, gv, *args, **kwargs)

        self.valid_msgs = []
        self.threadpool = gv['THREAD_POOL']

        # call job tracker twice to enforce healthy job log
        self.job_tracker = LaserJobTracker(parent=self)
        self.job_tracker.checkHealth()

        self.refreshAllWidgets()


        # menu bar actions
        self.importFromMailAction.triggered.connect(self.handleNewValidMails)
        self.selectFilesAction.triggered.connect(self.openSelectFilesDialog)
        self.selectFoldersAction.triggered.connect(self.openSelectFolderDialog)


        self.menuSettings.setToolTipsVisible(True)
        self.editSettingsAction.triggered.connect(self.openEditSettingsDialog)
        self.checkHealthAction.triggered.connect(self.checkHealth)


    def handleNewValidMails(self):
        ''' Handle the new mails in the inbox. '''
        self.threaded_mail_manager = ThreadedMailManager(self, gv, dialog=CreateLaserJobsFromMailQDialog)
        # getValidmails gets mail and triggers openImportFromMailDialog
        self.threaded_mail_manager.getValidMailsFromInbox()



    def openSelectFilesDialog(self):
        ''' Open dialog to select multiple files. '''
        dialog = FilesSelectQDialog(self, gv)

        if dialog.exec() == 1:
            files_global_paths = dialog.selectFilesButton.files_global_paths
            job_name = dialog.projectNameQLineEdit.text()

            if len(files_global_paths) > 0:
                CreateLaserJobsFromFileSystemQDialog(self, [job_name], [files_global_paths]).exec()

        self.refreshAllWidgets()

    def openSelectFolderDialog(self):
        ''' Open dialog to select folder with multiple subfolders. '''
        dialog = FolderSelectQDialog(self, gv)

        if dialog.exec() == 1:
            folder_global_path = dialog.selectFolderButton.folder_global_path
            project_name = dialog.projectNameQLineEdit.text()
            files_global_paths_list = []
            job_name_list = []

            if not os.path.exists(folder_global_path):
                WarningQMessageBox(gv, self, text='<Folder> does not exist')
                return

            for subfolder in os.listdir(folder_global_path):
                subfolder_global_path = os.path.join(folder_global_path, subfolder)

                if os.path.isdir(subfolder_global_path):
                    files_in_subfolder_global_paths = []
                    subfolder_contains_laser_file = False

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
                        files_global_paths_list.append(files_in_subfolder_global_paths)
                        job_name_list.append(project_name+'_'+os.path.basename(subfolder))
                    else:
                        WarningQMessageBox(gv, self, text=f'No laser file found in {subfolder_global_path}'\
                                f' skip this subfolder')

            if len(job_name_list) > 0:
                CreateLaserJobsFromFileSystemQDialog(self,
                                       job_name_list=job_name_list,
                                       files_global_paths_list=files_global_paths_list).exec()

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
        qlist_widgets = self.findChildren(QListWidget)
        for list_widget in qlist_widgets:
            list_widget.refresh()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    laser_window = LaserMainWindow()
    laser_window.show()
    app.exec()
