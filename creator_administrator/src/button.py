import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QShortcut, QKeySequence 
from PyQt6.QtWidgets import QPushButton, QFileDialog
from src.mail_manager import MailManager
from src.qlist_widget import ContentQListWidget
from src.qmessagebox import TimedMessage

from qlist_widget import OverviewQListWidget


class JobsQPushButton(QPushButton):
    ''' Parent class for all buttons that update job status
            such as laser klaar, gesliced. '''

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)


    def refreshAllQListWidgets(self):

        self.parent().parent().setCurrentIndex(0)    # show list of jobs in tabs
        print(f"this should be tabs {self.parent().parent().objectName()}")

        print(f"well well well , could you refresh//")

        qlist_widgets = self.parent().window().findChildren(OverviewQListWidget)
        print(f"the widgets  {self.window().objectName()} found with windws {qlist_widgets}")

        qlist_widgets = self.parent().parent().parent().findChildren(OverviewQListWidget)
        print(f"the widget found {self.parent().parent().parent().objectName()} as {qlist_widgets}")
        # qlist_widgets = self.parent().parent().parent().findChildren(JobsOverviewQListWidget)

        # refresh all QListWidgets that contain jobs
        for list_widget in qlist_widgets:   
            print(f"refresh widet {list_widget.objectName} referesehd")
            list_widget.refresh()


    def getCurrentItemName(self) -> str:
        content_qlist_widget = self.parent().findChild(ContentQListWidget)

        if content_qlist_widget is not None:
            return content_qlist_widget.current_item_name

    def sendFinishedMail(self, gv: dict, job_name: str, job_folder_global_path: str):
        ''' send please come pick up your job mail. '''
        mail_manager = MailManager(gv)
        msg_file_global_path = mail_manager.getMailGlobalPathFromFolder(job_folder_global_path)

        if msg_file_global_path is not None:
            # send finished mail on a seperate thread
            mail_manager.replyToEmailFromFileUsingTemplate(
                    msg_file_path=msg_file_global_path,
                    template_file_name="FINISHED_MAIL_TEMPLATE",
                    template_content={},
                    popup_reply=False)
            
            TimedMessage(gv, parent=self, text=f"Job Finished mail was sent to {job_name}")

        else:
            TimedMessage(gv, parent=self, text=f"No .msg file detected, no Pickup mail was sent to {job_name}")

    
class BackQPushButton(QPushButton):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.clicked.connect(self.on_click)
 
        # shortcut on Esc button
        QShortcut(QKeySequence(Qt.Key.Key_Escape), self).activated.connect(self.on_click)

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

        self.files_global_paths = list(dict.fromkeys(self.files_global_paths + files_paths))

        selected_files_str = 'Selected Files:'

        for file_global_path in self.files_global_paths:
            selected_files_str += f'\n{os.path.basename(file_global_path)}'

        self.setText(selected_files_str)

class SelectFileQPushButton(QPushButton):
    ''' Select a single file from file system. '''

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.clicked.connect(self.on_click)

        self.start_dir_global_path = os.path.expanduser('~')     
        self.file_global_path = None

    def setStartingDirectory(self, start_dir_global_path: str):
        ''' Set the starting directory. '''
        assert os.path.exists(start_dir_global_path), f"{start_dir_global_path} does not exist"
        assert os.path.isdir(start_dir_global_path), f"{start_dir_global_path} is not a directory"
        self.start_dir_global_path = start_dir_global_path


    def on_click(self):
      # Get list of selected file paths

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            'Select File',
            self.start_dir_global_path,
            'All Files (*)')

        self.setText(str(file_path))# TODO: shorten this path
        self.file_global_path = file_path



class SelectFolderQPushButton(QPushButton):
    ''' Select a folder from file system. '''

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.folder_global_path = None
        self.clicked.connect(self.on_click)
        self.start_dir_global_path = os.path.expanduser('~')  

    def setStartingDirectory(self, start_dir_global_path: str):
        ''' Set the starting directory. '''
        assert os.path.exists(start_dir_global_path), f"{start_dir_global_path} does not exist"
        assert os.path.isdir(start_dir_global_path), f"{start_dir_global_path} is not a directory"
        self.start_dir_global_path = start_dir_global_path

    def on_click(self):
        self.folder_global_path = QFileDialog.getExistingDirectory(self,
            'Select Folder',
            self.start_dir_global_path,
            QFileDialog.Option.ShowDirsOnly)

        folder_name_short = self.folder_global_path

        max_char_length = 50

        if len(folder_name_short) > max_char_length:
            folder_name_short = '../'+folder_name_short[-max_char_length+3:]

        self.setText(folder_name_short)

