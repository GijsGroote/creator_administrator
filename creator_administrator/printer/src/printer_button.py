import os
from functools import partial

from PyQt6.QtGui import QShortcut, QKeySequence 
from PyQt6.QtWidgets import QMenu

from src.button import JobsQPushButton
from src.directory_functions import open_folder
from src.directory_functions import delete_directory_content
from src.qdialog import SelectOptionsQDialog
from src.directory_functions import copy_item
from src.qmessagebox import TimedMessage, WarningQMessageBox, InfoQMessageBox
from src.threaded_mail_manager import ThreadedMailManager

from global_variables import gv
from printer_job_tracker import PrintJobTracker

class PrintKlaarQPushButton(JobsQPushButton):

    def __init__(self, *args, parent=None, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.threadpool = gv["THREAD_POOL"]
        self.clicked.connect(self.on_click)
 
    def on_click(self):
        job_name = self.getCurrentItemName()
        job_tracker = PrintJobTracker(self)
        
        job_folder_global_path = job_tracker.getJobFolderGlobalPathFromJobName(job_name)
        job_tracker.updateJobStatus(job_name, 'VERWERKT')
        job_tracker.markAllFilesAsDone(job_name=job_name, done=True)

        sender_name = job_tracker.jobNameToSenderName(job_name)
        self.refreshAllQListWidgets()

        if not any([file.endswith(('.msg', '.eml')) for file in os.listdir(job_folder_global_path)]):
            WarningQMessageBox(gv=gv, parent=self, text='No Job finished mail send because: No mail file found')
        else:
            ThreadedMailManager(parent=self, gv=gv).startMailWorker(
                    sender_name=sender_name,
                    mail_type='FINISHED',
                    mail_item=job_folder_global_path)


class AfgekeurdQPushButton(JobsQPushButton):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.clicked.connect(self.on_click)
        self.threadpool = gv['THREAD_POOL']

    def on_click(self):
        job_name = self.getCurrentItemName()
        job_tracker = PrintJobTracker(self)
        job_tracker.updateJobStatus(job_name, 'AFGEKEURD')
        self.refreshAllQListWidgets()

        job_folder_global_path = job_tracker.getJobFolderGlobalPathFromJobName(job_name)

        
        if not any([file.endswith(('.msg', '.eml')) for file in os.listdir(job_folder_global_path)]):
                    WarningQMessageBox(gv=gv, parent=self, text='No Afgekeurd mail send because: No mail file found')
        else:
            sender_name = job_tracker.jobNameToSenderName(job_name)

            ThreadedMailManager(parent=self, gv=gv).startDeclinedMailWorker(
                success_message=f'Job declined mail send to {sender_name}',
                error_message=f'No job declined mail send to {sender_name}',
                mail_item=job_folder_global_path)
        
class OptionsQPushButton(JobsQPushButton):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.menu = QMenu()

        self.object_name = self.objectName()


        copy_todo_action = self.menu.addAction('Copy Files to TODO folder', self.copyPrintFilesTo)
        copy_todo_action.setToolTip('Shortcut: Ctrl+T')
        
        QShortcut(QKeySequence('Ctrl+T'), self).activated.connect(self.copyPrintFilesTo)
        self.menu.setToolTipsVisible(True)

        if gv['DARK_THEME']:
            self.menu.setStyleSheet("""QToolTip { 
                           background-color: black; 
                           color: white; 
                           border: black solid 1px
                           }""")


        # initialize  
        self.objectNameChanged.connect(self.storeObjectNameInit)

    def storeObjectNameInit(self):
        ''' store the object name and initialize. '''
        self.object_name = self.objectName()

        mail_menu = None


        if self.object_name == 'wachtrijOptionsQPushButton':
            self.menu.addAction('Open in File Explorer', self.openInFileExplorer)
            mail_menu = self.menu.addMenu('Send Mail')
            self.menu.addAction('Delete Job', self.deleteJob)

        elif self.object_name == 'geslicedOptionsQPushButton':
            pass

        elif self.object_name == 'printenOptionsQPushButton':
            pass

        elif self.object_name == 'verwerktOptionsQPushButton':
            self.menu.addAction('Move to Wachtrij', self.moveJobToWachtrij)
            self.menu.addAction('Move to Afgekeurd', self.moveJobToAfgekeurd)
            mail_menu = self.menu.addMenu('Send Mail')
            self.menu.addAction('Open in File Explorer', self.openInFileExplorer)
            self.menu.addAction('Delete Job', self.deleteJob)

        elif self.object_name == 'afgekeurdOptionsQPushButton':
            self.menu.addAction('Move to Wachtrij', self.moveJobToWachtrij)
            self.menu.addAction('Move to Verwerkt', self.moveJobToVerwerkt)
            mail_menu = self.menu.addMenu('Send Mail')
            self.menu.addAction('Open in File Explorer', self.openInFileExplorer)
            self.menu.addAction('Delete Job', self.deleteJob)

        else:
            raise ValueError(f'could not identify {self.object_name}')

        if mail_menu is not None:
            mail_menu.addAction('Send job Received mail', partial(self.sendMail, 'RECEIVED'))
            mail_menu.addAction('Send job Finished mail', partial(self.sendMail, 'FINISHED'))
            mail_menu.addAction('Send job Declined Mail', partial(self.sendMail, 'DECLINED'))

        self.setMenu(self.menu)

    def moveJobToWachtrij(self):
        # Mark all print files as not done
        job_name = self.getCurrentItemName()
        PrintJobTracker(self).markAllFilesAsDone(job_name=job_name,
                                                 done=False)
        self.moveJobTo('WACHTRIJ')
        self.refreshAllQListWidgets()

    def moveJobToAfgekeurd(self):
        self.moveJobTo('AFGEKEURD')
        self.refreshAllQListWidgets()

    def moveJobToVerwerkt(self):
        self.moveJobTo('VERWERKT')
        self.refreshAllQListWidgets()

    def moveJobTo(self, new_status):
        job_name = self.getCurrentItemName()
        PrintJobTracker(self).updateJobStatus(job_name, new_status)
        self.refreshAllQListWidgets()

    def openInFileExplorer(self):
        job_folder_global_path = PrintJobTracker(self).getJobDict(
                self.getCurrentItemName())['job_folder_global_path']
        open_folder(job_folder_global_path)

    def deleteJob(self):
        job_name = self.getCurrentItemName()
        PrintJobTracker(self).deleteJob(job_name)
        self.refreshAllQListWidgets()

    def copyPrintFilesTo(self):
        '''Copy the print files from a job to a specified folder. '''

        target_folder_global_path = gv['TODO_DIR_HOME']
        if gv['EMPTY_TODO_DIR_BEFORE_EXPORT']:
            delete_directory_content(self.parent, target_folder_global_path)

        if self.parent().parent().objectName() == 'wachtrijMateriaalQStackedWidget':
            material_name = self.getCurrentItemName()
            material, thickness = split_material_name(material_name)
            print_files_info_list = PrintJobTracker(
                    self).getPrintFilesWithMaterialThicknessInfo(material, thickness)

            for file_name, file_global_path, _ in print_files_info_list:
                copy_item(file_global_path, os.path.join(target_folder_global_path, file_name))
        else:
            job_name = self.getCurrentItemName()
            print_file_dict =  PrintJobTracker(self).getPrintFilesDict(job_name)
                       
            for file_key, file_dict in print_file_dict.items():
                source_item_global_path = file_dict['file_global_path']
                target_item_global_path = os.path.join(target_folder_global_path, file_key)
                copy_item(source_item_global_path, target_item_global_path)

        TimedMessage(gv=gv, parent=self, text='Copied Files to TODO folder')


    # def sendReceivedMail(self, job_name: str)
    #     ''' Send a Received mail. '''
    #     self.sendMail(job_name, 'RECEIVED')

    def sendUnclearMail(self):
        ''' Send a Received mail. '''
        self.sendMail('UNCLEAR')

    # def sendDeclinedMail(self, job_name: str)
    #     ''' Send a Received mail. '''
    #     self.sendMail(job_name, 'DECLINED')

    # def sendFinishedMail(self, job_name: str)
    #     ''' Send a Received mail. '''
    #     self.sendMail(job_name, 'FINISHED')

    def sendMail(self, mail_type: str):
        ''' Send a mail. '''
        job_name = self.getCurrentItemName()


        job_dict = PrintJobTracker(parent=self).getJobDict(job_name)

        if job_dict is None:
            WarningQMessageBox(gv=gv, parent=self, text='No mail send because: Job Name could not be found')
            return

        if not any([file.endswith(('.msg', '.eml')) for file in os.listdir(job_dict['job_folder_global_path'])]):
            WarningQMessageBox(gv=gv, parent=self, text='No Job finished mail send because: No mail file found')
            return

        ThreadedMailManager(parent=self, gv=gv).startMailWorker(
                sender_name=job_dict['sender_name'],
                mail_type=mail_type,
                mail_item=job_dict['job_folder_global_path'])

