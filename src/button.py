import os

from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5 import QtWebEngineWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from src.mail_manager import MailManager


from src.qlist_widget import ContentQListWidget
from laser_qlist_widget import JobContentQListWidget, OverviewQListWidget

from src.qmessagebox import TimedMessage

class JobsQPushButton(QPushButton):
    ''' Parent class for all buttons that update job status
            such as laser klaar, gesliced. '''


    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # self.parent = parent

        # jobPage_2 annoyingly is not a child of QStackedWidget
        # self.threadpool = QThreadPool()


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

    def sendFinishedMail(self, gv: dict, job_name: str, job_folder_global_path: str):
        ''' send please come pick up your job mail. '''
        mail_manager = MailManager(gv, self.parent())
        msg_file_global_path = mail_manager.getMailGlobalPathFromFolder(job_folder_global_path)

        if msg_file_global_path is not None:
            # send finished mail on a seperate thread
            mail_manager.replyToEmailFromFileUsingTemplate(
                    msg_file_path=msg_file_global_path,
                    template_file_name="FINISHED_MAIL_TEMPLATE",
                    template_content={},
                    popup_reply=False)
            
            TimedMessage(self, f"Job Finished mail was sent to {job_name}")

        else:
            TimedMessage(self, f"No .msg file detected, no Pickup mail was sent to {job_name}")

        # mail_manager = MailManager(gv)
        # msg_file_global_path = mail_manager.getMailGlobalPathFromFolder(job_folder_global_path)

        # if msg_file_global_path is not None:
        #     # send finished mail on a seperate thread
        #     send_mail_worker = Worker(mail_manager.replyToEmailFromFileUsingTemplate,
        #             msg_file_path=msg_file_global_path,
        #             template_file_name="FINISHED_MAIL_TEMPLATE",
        #             template_content={},
        #             popup_reply=False)

        #     self.threadpool.start(send_mail_worker)

        # else:
        #     TimedQMessageBox(
        #             text=f"No .msg file detected, no Pickup mail was sent to {job_name}",
        #             parent=self, icon=QMessageBox.Warning)

    def sendDeclinedMail(self, gv: dict, job_name: str, job_folder_global_path: str):
        ''' popup the Declined mail. '''
        mail_manager = MailManager(gv, self)

        mail_manager.replyToEmailFromFileUsingTemplate(
                mail_manager.getMailGlobalPathFromFolder(job_folder_global_path),
                'DECLINED_MAIL_TEMPLATE',
                {},
                popup_reply=True)


class BackQPushButton(QPushButton):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.clicked.connect(self.on_click)
 
        # shortcut on Esc button
        QShortcut(QKeySequence(Qt.Key_Escape), self).activated.connect(self.on_click)

    def on_click(self):
        self.parent().parent().setCurrentIndex(0) 

class SelectFilesQPushButton(QPushButton):
    ''' Select multiple files from file system. '''

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.files_global_paths = []
        self.clicked.connect(self.on_click)


    def on_click(self):
      # Get list of selected file paths
        files_paths, _ = QFileDialog.getOpenFileNames(
            self,
            'Select Files',
            os.path.expanduser('~'),
            'All Files (*)')
        self.files_global_paths.extend(files_paths)

        selected_files_str = 'Selected Files:\n'
        for file_global_path in self.files_global_paths:
            selected_files_str += f'{os.path.basename(file_global_path)}, '
        selected_files_str = selected_files_str[:-2]

        if len(self.files_global_paths) > 0:
            self.parent().filesGlobalPathsQLabel.setText(selected_files_str)
            self.parent().filesGlobalPathsQLabel.show()


class SelectFolderQPushButton(QPushButton):
    ''' Select a folder from file system. '''

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
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

