import sys
import os
from PyQt5 import QtWidgets


from PyQt5.QtWidgets import QListWidget, QDialog
from global_variables import gv
from src.app import MainWindow
from select_file import create_laser_jobs
from laser_qdialog import LaserImportFromMailQDialog, LaserSelectFileQDialog

from src.mail_manager import MailManager

class LaserMainWindow(MainWindow):
    def __init__(self, *args, **kwargs):
        ui_global_path = os.path.join(gv['UI_DIR_HOME'], 'laser_main_window.ui')
        MainWindow.__init__(self, ui_global_path, *args, **kwargs)


        # menu bar actions
        self.ActionImportFromMail.triggered.connect(self.onActionImportFromMail)
        self.ActionSelectFile.triggered.connect(self.onActionSelectFileclicked)

    def onActionImportFromMail(self):

        valid_msgs = self.getNewValidMails()

        if len(valid_msgs) == 0:
            print(f"ha no valid mails, no pupup")
        else:

            dialog = LaserImportFromMailQDialog(self, valid_msgs)

            if dialog.exec_() == QDialog.Accepted:
                pass
                # folder_global_path = dialog.selectFolderButton.folder_global_path
                # project_name = dialog.ProjectNameQLineEdit.text()
                # create_laser_jobs(folder_global_path, project_name)

                # refresh all laser job tabs
                qlist_widgets = self.findChildren(QListWidget)
                for list_widget in qlist_widgets:
                    list_widget.refresh()


    def onActionSelectFileclicked(self):
        dialog = LaserSelectFileQDialog(self)

        if dialog.exec_() == QDialog.Accepted:
            folder_global_path = dialog.selectFolderButton.folder_global_path
            project_name = dialog.ProjectNameQLineEdit.text()
            create_laser_jobs(folder_global_path, project_name)

            # refresh all laser job tabs
            qlist_widgets = self.findChildren(QListWidget)
            for list_widget in qlist_widgets:
                list_widget.refresh()

    def getNewValidMails(self):
        ''' Return new valid mails. '''

        print('searching for new mail...')
        self.mail_manager = MailManager(gv)
        # read unread mails and convert to the email format and mark them as read
        msgs = self.mail_manager.getNewEmails()

        valid_msgs = [msg for msg in msgs if self.mail_manager.isMailAValidJobRequest(msg)]

        if len(msgs) > len(valid_msgs):
            print(f'{len(msgs)-len(valid_msgs)} invalid messages detected, respond to them manually.')

        return valid_msgs

    
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    laser_window = LaserMainWindow()
    laser_window.show()
    app.exec_()
