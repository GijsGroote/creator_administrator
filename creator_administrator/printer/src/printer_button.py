from functools import partial
import os

from PyQt6.QtWidgets import QWidget

from src.button import JobsQPushButton, OptionsQPushButton
from src.directory_functions import delete_directory_content, copy_item
from src.qmessagebox import TimedMessage, WarningQMessageBox, YesOrNoMessageBox 
from src.threaded_mail_manager import ThreadedMailManager
from src.qdialog import SelectOptionsQDialog

from global_variables import gv
from printer_job_tracker import PrintJobTracker
from convert import gcode_files_to_max_print_time, get_date_from_dynamic_job_name



class GeslicedQPushButton(JobsQPushButton):

    def __init__(self, *args, parent: QWidget, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.clicked.connect(self.on_click)

    def on_click(self):
        ''' Update Job status to GESLICED. '''

        job_name = self.getCurrentItemName()
        job_tracker = PrintJobTracker(self)


        job_dict =  job_tracker.getJobDict(job_name)

        gcode_files = [gcode_file for
                       gcode_file in os.listdir(job_dict['job_folder_global_path'])
                       if gcode_file.lower().endswith('.gcode')]

        if len(gcode_files) == 0:
            WarningQMessageBox(self, gv, 'warning! no .gcode files detected, slice .stl files first')

        else:
            job_tracker.updateJobKey('status', job_name, 'GESLICED')

            # Rename GCODE 
            for gcode_file in gcode_files:
                try:
                    os.rename(os.path.join(job_dict['job_folder_global_path'], gcode_file),
                              os.path.join(job_dict['job_folder_global_path'],
                                   job_dict['job_name']+ '_' + gcode_file))
                except Exception:
                    pass # simply do not rename then
        
        job_tracker.updateJobKey('dynamic_job_name', job_name,
                  get_date_from_dynamic_job_name(job_dict['dynamic_job_name'])+
                  gcode_files_to_max_print_time(gcode_files)+job_name)

        self.window().refreshAllWidgets()
        self.parent().parent().setCurrentIndex(0)

class PrintAangezetQPushButton(JobsQPushButton):

    def __init__(self, *args, parent: QWidget, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.clicked.connect(self.on_click)

    def on_click(self):
        ''' Update Job status to AAN_HET_PRINTEN. '''

        job_name = self.getCurrentItemName()
        job_tracker = PrintJobTracker(self)

        job_folder_global_path = job_tracker.getJobValue('job_folder_global_path', job_name)
        gcode_files_name_and_global_path = []

        for job_file in os.listdir(job_folder_global_path):
            if job_file.endswith('.gcode'):
                gcode_files_name_and_global_path.append((job_file, os.path.join(job_folder_global_path, job_file)))


        if len(gcode_files_name_and_global_path) <= 1:
            job_tracker.updateJobKey('status', job_name, 'AAN_HET_PRINTEN')
            self.window().refreshAllWidgets()
            self.parent().parent().setCurrentIndex(0)

        elif len(gcode_files_name_and_global_path) > 1:

            if YesOrNoMessageBox(self, text="Is the entire print job printing/printed?").answer(): 
                job_tracker.updateJobKey('status', job_name, 'AAN_HET_PRINTEN')
                self.window().refreshAllWidgets()
                self.parent().parent().setCurrentIndex(0)

            else:
                dialog = SelectOptionsQDialog(self, gv, gcode_files_name_and_global_path, question='Select which .gcode files should be printed later')

                if dialog.exec() == 1:
                    selected_gcode_global_path = []
                    for item in dialog.optionsQListWidget.selectedItems():
                        selected_gcode_global_path.append(item.data(1))

                    if len(selected_gcode_global_path) == len(gcode_files_name_and_global_path):
                        # all gcode should be printed later, do nothing
                        return
                    else:
                        # split the print job
                        pass





class PrintKlaarQPushButton(JobsQPushButton):
    ''' TODO. '''

    def __init__(self, *args, parent=None, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.threadpool = gv["THREAD_POOL"]
        self.clicked.connect(self.on_click)
 
    def on_click(self):
        ''' Update Job status to VERWERKT. '''

        job_name = self.getCurrentItemName()
        job_tracker = PrintJobTracker(self)
        
        job_folder_global_path = job_tracker.getJobValue('job_folder_global_path', job_name)
        job_tracker.updateJobKey('status', job_name, 'VERWERKT')
        job_tracker.markFilesAsDone(job_name=job_name, file_global_path=None, done=True, all_files_done=True)

        sender_name = job_tracker.getJobValue('sender_name', job_name)
        self.window().refreshAllWidgets()
        self.parent().parent().setCurrentIndex(0)

        if not any([file.endswith(('.msg', '.eml')) for file in os.listdir(job_folder_global_path)]): # pylint: disable=use-a-generator
            WarningQMessageBox(parent=self, gv=gv, text='No Job finished mail send because: No mail file found')
        else:
            ThreadedMailManager(parent=self, gv=gv).startMailWorker(
                    sender_name=sender_name,
                    mail_type='FINISHED',
                    mail_item=job_folder_global_path)


class PrintAfgekeurdQPushButton(JobsQPushButton):

    def __init__(self, parent: QWidget, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.clicked.connect(self.on_click)
        self.threadpool = gv['THREAD_POOL']

    def on_click(self):
        ''' Update Job status to AFGEKEURD. '''

        job_name = self.getCurrentItemName()
        job_tracker = PrintJobTracker(self)
        job_tracker.updateJobKey('status', job_name, 'AFGEKEURD')
        self.window().refreshAllWidgets()
        self.parent().parent().setCurrentIndex(0)

        job_folder_global_path = job_tracker.getJobValue('job_folder_global_path', job_name)

        if not any([file.endswith(('.msg', '.eml')) for file in os.listdir(job_folder_global_path)]): # pylint: disable=use-a-generator
                    WarningQMessageBox(gv=gv, parent=self, text='No Afgekeurd mail send because: No mail file found')
        else:
            sender_name = job_tracker.getJobValue('sender_name', job_name)

            ThreadedMailManager(parent=self, gv=gv).startDeclinedMailWorker(
                success_message=f'Job declined mail send to {sender_name}',
                error_message=f'No job declined mail send to {sender_name}',
                mail_item=job_folder_global_path)
        
class PrintOptionsQPushButton(OptionsQPushButton):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, gv, PrintJobTracker(self), *args, **kwargs)

    def initialize(self):
        ''' Initialize button. '''
        self.object_name = self.objectName()

        mail_menu = None

        self.menu.addAction('Open in File Explorer', self.openInFileExplorer)
        self.menu.addAction('Delete Job', self.deleteJob)

        if self.object_name == 'wachtrijOptionsQPushButton':
            mail_menu = self.menu.addMenu('Send Mail')
            self.menu.addAction('Move to Verwerkt', self.moveJobToVerwerkt)

        elif self.object_name == 'geslicedOptionsQPushButton':
            self.menu.addAction('Move to Wachtrij', self.moveJobToWachtrij)

        elif self.object_name == 'printenOptionsQPushButton':
            self.menu.addAction('Move to Wachtrij', self.moveJobToWachtrij)
            self.menu.addAction('Move to Gesliced', self.moveJobToGesliced)

        elif self.object_name == 'verwerktOptionsQPushButton':
            self.menu.addAction('Move to Wachtrij', self.moveJobToWachtrij)
            self.menu.addAction('Move to Afgekeurd', self.moveJobToAfgekeurd)
            mail_menu = self.menu.addMenu('Send Mail')

        elif self.object_name == 'afgekeurdOptionsQPushButton':
            self.menu.addAction('Move to Wachtrij', self.moveJobToWachtrij)
            self.menu.addAction('Move to Verwerkt', self.moveJobToVerwerkt)
            mail_menu = self.menu.addMenu('Send Mail')

        else:
            raise ValueError(f'could not identify {self.object_name}')

        if mail_menu is not None:
            mail_menu.addAction('Send job Received mail', partial(self.sendMail, 'RECEIVED'))
            mail_menu.addAction('Send job Finished mail', partial(self.sendMail, 'FINISHED'))
            mail_menu.addAction('Send job Declined Mail', partial(self.sendMail, 'DECLINED'))

        self.setMenu(self.menu)

    def moveJobToGesliced(self):
        self.moveJobTo('GESLICED')

    def copyMakeFilesTo(self):
        '''Copy the make files from a job to the todo folder. '''
    
        target_folder_global_path = gv['TODO_DIR_HOME']
        if gv['EMPTY_TODO_DIR_BEFORE_EXPORT']:
            delete_directory_content(self.parent, gv, target_folder_global_path)

        job_name = self.getCurrentItemName()
        print_file_dict =  self.job_tracker.getJobValue('make_files', job_name)
                   
        for file_key, file_dict in print_file_dict.items():
            source_item_global_path = file_dict['file_global_path']
            target_item_global_path = os.path.join(target_folder_global_path, file_key)
            copy_item(source_item_global_path, target_item_global_path)

        TimedMessage(parent=self, gv=gv, text='Copied Files to TODO folder')

    def sendMail(self, mail_type: str):
        ''' Send a mail. '''
        job_name = self.getCurrentItemName()

        job_dict = PrintJobTracker(parent=self).getJobDict(job_name)

        if job_dict is None:
            WarningQMessageBox(parent=self, gv=gv, text='No mail send because: Job Name could not be found')
            return

        if not any([file.endswith(('.msg', '.eml')) for file in os.listdir(job_dict['job_folder_global_path'])]): # pylint: disable=use-a-generator
            WarningQMessageBox(parent=self, gv=gv, text='No Job finished mail send because: No mail file found')
            return

        ThreadedMailManager(parent=self, gv=gv).startMailWorker(
                sender_name=job_dict['sender_name'],
                mail_type=mail_type,
                mail_item=job_dict['job_folder_global_path'])
