
import os
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
        QPushButton, QFileDialog, QStackedWidget,
        QShortcut)
from src.mail_manager import MailManager


from src.qlist_widget import ContentQListWidget
from laser_qlist_widget import JobContentQListWidget, OverviewQListWidget

from src.qmessagebox import TimedQMessageBox

class JobsQPushButton(QPushButton):
    ''' Parent class for all buttons that update job status
            such as laser klaar, gesliced. '''


    def __init__(self, *args, **kwargs):
        QPushButton.__init__(self, *args, **kwargs)


    def refreshAllQListWidgets(self):

        self.parent().parent().setCurrentIndex(0)        # show list of jobs in tabs

        # for qstacked_widget in qstacked_widgets:
            # qstacked_widget.setCurrentIndex(0)

        qlist_widgets = self.window().findChildren(OverviewQListWidget)
        # refresh all QListWidgets that contain jobs
        for list_widget in qlist_widgets:
            list_widget.refresh()


    def getCurrentItemName(self) -> str:
        content_qlist_widget = self.parent().findChild(ContentQListWidget)

        if content_qlist_widget is not None:
            return content_qlist_widget.current_item_name

    def sendFinishedMail(self, gv: dict, job_name: str, job_folder_global_path: str) -> str:
        ''' send please come pick up your job mail. '''

        mail_manager = MailManager(gv)
        msg_file_global_path = mail_manager.getMailGlobalPathFromFolder(job_folder_global_path)

        if msg_file_global_path is not None:
            mail_manager.replyToEmailFromFileUsingTemplate(
                        msg_file_global_path,
                        "FINISHED_MAIL_TEMPLATE",
                        {},
                        popup_reply=False)

            TimedQMessageBox(text=f"Job finished mail send to {job_name}",
                            parent=self)
        else:
            TimedQMessageBox(
                    text=f"No .msg file detected, no Pickup mail was sent to {job_name}",
                    parent=self, icon=QMessageBox.Warning)

    def sendDeclinedMail(self, gv: dict, job_name: str, job_folder_global_path: str):
        ''' popup the Declined mail. '''
        mail_manager = MailManager(gv)

        mail_manager.replyToEmailFromFileUsingTemplate(
                mail_manager.getMailGlobalPathFromFolder(job_folder_global_path),
                'DECLINED_MAIL_TEMPLATE',
                {},
                popup_reply=True)


class BackQPushButton(QPushButton):

    def __init__(self, *args, **kwargs):
        QPushButton.__init__(self, *args, **kwargs)
        self.clicked.connect(self.on_click)

 
        # shortcut on Esc button
        QShortcut(QKeySequence(Qt.Key_Escape), self).activated.connect(self.on_click)

    def on_click(self):
        self.parent().parent().setCurrentIndex(0) 

class SelectFolderQPushButton(QPushButton):

    def __init__(self, parent=None):
        QPushButton.__init__(self, parent)
        self.folder_global_path = None
        self.clicked.connect(self.on_click)

    def on_click(self):
        self.folder_global_path = QFileDialog.getExistingDirectory(self,
            'Select Folder',
            os.path.expanduser('~'),
            QFileDialog.ShowDirsOnly)

        folder_name_short = self.folder_global_path

        max_char_length = 50

        if len(folder_name_short) > max_char_length:
            folder_name_short = '../'+folder_name_short[-max_char_length+3:]

        self.setText(folder_name_short)

