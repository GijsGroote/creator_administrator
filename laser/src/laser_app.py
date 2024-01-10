import sys
import os
from PyQt5 import QtWidgets
from PyQt5 import QtCore


from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from global_variables import gv
from src.app import MainWindow
from src.app import get_thread_pool
from laser_qdialog import LaserImportFromMailQDialog, LaserSelectFileQDialog
from src.qmessagebox import TimedQMessageBox

from src.worker import Worker
from src.loading_dialog import LoadingQDialog

from src.mail_manager import MailManager

class LaserMainWindow(MainWindow):
    def __init__(self, *args, **kwargs):
        ui_global_path = os.path.join(gv['UI_DIR_HOME'], 'laser_main_window.ui')
        super().__init__(ui_global_path, *args, **kwargs)

        print(f"just after laserMainwindows")
        # self.loading_dialog.show()
        # self.loading_dialog.hide()

        # self.threadpool = get_thread_pool(self)
        # print(f' this threadpool is of type {type(self.threadpool)}')

        self.valid_msgs = []

        # menu bar actions
        self.ActionImportFromMail.triggered.connect(self.onActionImportFromMail)
        self.ActionSelectFile.triggered.connect(self.onActionSelectFileclicked)


    def onActionImportFromMail(self):


        self.loading_dialog = LoadingQDialog(self, gv)
        self.loading_dialog.show()

        # create workers
        self.get_mail_worker = Worker(self.getNewValidMails)
        self.get_mail_worker.signals.finished.connect(self.loading_dialog.accept)
        self.get_mail_worker.signals.result.connect(self.openImportFromMailDialog)



        # self.threadpool.start(self.loading_widget_worker)
        self.valid_msgs = self.threadpool.start(self.get_mail_worker)

        print('done?')

    def openImportFromMailDialog(self, valid_msgs: list):
        ''' open import from mail dialog. '''

        if len(valid_msgs) == 0:
            TimedQMessageBox(text='No new mails', parent=self)
        else:

            dialog = LaserImportFromMailQDialog(self, valid_msgs)

            if dialog.exec_() == QDialog.Accepted:
                pass

            # refresh all laser job tabs
            qlist_widgets = self.findChildren(QListWidget)
            for list_widget in qlist_widgets:
                list_widget.refresh()


    def onActionSelectFileclicked(self):
        dialog = LaserSelectFileQDialog(self)

        if dialog.exec_() == QDialog.Accepted:
            folder_global_path = dialog.selectFolderButton.folder_global_path
            project_name = dialog.ProjectNameQLineEdit.text()
            # TODO: open dialog to collect material, thickness and amount per dxf
            # create_laser_jobs(folder_global_path, project_name)

        # refresh all laser job tabs
        qlist_widgets = self.findChildren(QListWidget)
        for list_widget in qlist_widgets:
            list_widget.refresh()

    def getNewValidMails(self):
        ''' Return new valid mails. '''
        print(f"getting mails")

        self.mail_manager = MailManager(gv)
        # read unread mails and convert to the email format and mark them as read
        msgs = self.mail_manager.getNewEmails()

        valid_msgs = [msg for msg in msgs if self.mail_manager.isMailAValidJobRequest(msg)]

        if len(msgs) > len(valid_msgs):
            it_or_them = 'it' if len(msgs) - len(valid_msgs) == 1 else 'them'
            TimedQMessageBox(
                    text=f'{len(msgs)-len(valid_msgs)} invalid messages '\
                    f'detected, respond to {it_or_them} manually.',
                    parent=self, icon=QMessageBox.Warning)

        print(f"yeah sending back mails now")

        return valid_msgs

    
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    laser_window = LaserMainWindow()
    laser_window.show()
    app.exec_()
