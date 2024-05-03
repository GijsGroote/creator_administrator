import os
import json
import abc
import webbrowser
import datetime
import pkg_resources

from PyQt6.QtWidgets import QDialog, QWidget, QListWidgetItem, QMessageBox

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut, QFont
from PyQt6.uic import loadUi

from src.mail_manager import MailManager
from src.job_tracker import JobTracker
from src.qmessagebox import TimedMessage, WarningQMessageBox
from src.directory_functions import copy_item


class CreateJobsQDialog(QDialog):
    ''' Create jobs from data. '''

    def __init__(self,
                 parent: QWidget,
                 gv: dict,
                 ui_global_path: str,
                 job_tracker: JobTracker,
                 *args,
                 **kwargs):

        super().__init__(parent, *args, **kwargs)


        loadUi(ui_global_path, self)

        self.gv=gv
        self.job_tracker = job_tracker
        self.threadpool = gv['THREAD_POOL']

        self.job_counter = 0
        self.make_item_counter = 0

        self.new_material_text = 'New Material'
        self.new_materials_list = []
        self.newMaterialQLabel.setHidden(True)
        self.newMaterialQLineEdit.setHidden(True)
        self.materialQComboBox.currentIndexChanged.connect(self.onMaterialComboboxChanged)

        self.skipPushButton.clicked.connect(self.skipJob)
        self.buttonBox.accepted.connect(self.collectItemInfo)

        # shortcut on Esc button
        QShortcut(QKeySequence(Qt.Key.Key_Escape), self).activated.connect(self.close)


    def loadContent(self):
        ''' Load content into the dialog. '''

        if self.make_item_counter >= len(self.temp_make_items):
            self.createJob()
            self.job_counter += 1
            self.make_item_counter = 0

            if self.job_counter >= len(self.jobs):
                # done! close dialog
                self.accept()
            else:
                self.loadJobContent()
        else:
            self.loadItemContent()

    @abc.abstractmethod
    def loadJobContent(self):
        ''' Load content of job into the dialog. '''

    @abc.abstractmethod
    def loadItemContent(self):
        ''' Load content of item into dialog. '''

    @abc.abstractmethod
    def collectItemInfo(self):
        ''' Collect user input from dialog. '''

    def skipJob(self):
        ''' Skip a job and go to the next. '''
        self.job_counter += 1
        self.make_item_counter = 0

        if self.job_counter >= len(self.jobs):
            self.accept()
        else:
            self.loadJobContent()

    def onMaterialComboboxChanged(self):
        ''' Show/hide new material option. '''
        if self.materialQComboBox.currentText() == self.new_material_text:
            self.newMaterialQLabel.setHidden(False)
            self.newMaterialQLineEdit.setHidden(False)
        else:
            self.newMaterialQLabel.setHidden(True)
            self.newMaterialQLineEdit.setHidden(True)

class CreateJobsFromMailQDialog(CreateJobsQDialog):
    ''' Create jobs from mail data. '''

    def __init__(self,
                 parent: QWidget,
                 gv: dict,
                 job_tracker: JobTracker,
                 valid_msgs,
                 *args,
                 **kwargs):


        super().__init__(parent,
                         gv,
                         os.path.join(gv['LOCAL_UI_DIR'], 'import_mail_dialog.ui'),
                         job_tracker,
                         *args,
                         **kwargs)

        self.jobs = valid_msgs
        self.mail_manager = MailManager(gv)

    def loadJobContent(self):
        ''' Load content of mail into dialog. '''

        job_msg = self.jobs[self.job_counter]

        self.temp_sender_name = self.mail_manager.getSenderName(job_msg)
        self.temp_job_name = self.job_tracker.makeJobNameUnique(self.temp_sender_name)
        self.temp_job_folder_name = str(datetime.date.today().strftime('%d-%m'))+'_'+self.temp_job_name
        self.temp_job_folder_global_path = os.path.join(os.path.join(self.gv['JOBS_DIR_HOME'], self.temp_job_folder_name))
        self.temp_make_items = []
        self.temp_make_files_dict = {}
        self.temp_store_files_dict = {}

        self.mailFromQLabel.setText(self.temp_sender_name)
        self.mailProgressQLabel.setText(f'Mail ({self.job_counter+1}/{len(self.jobs)})')
        self.subjectQLabel.setText(self.mail_manager.getMailSubject(job_msg))

        self.mailBodyLabel.setText(self.mail_manager.getMailBody(job_msg))


        # detect special printer request
        self.requested_parameters_dict = None
        for attachment in self.mail_manager.getAttachments(job_msg):
            attachment_name = self.mail_manager.getAttachmentFileName(attachment)
            if attachment_name.lower().endswith('.json'):
                requested_print_parameters_name = 'requested_print_parameters.json'
                self.mail_manager.saveAttachment(attachment,
                                         os.path.join(self.gv['TEMP_DIR_HOME'], 
                                          requested_print_parameters_name))

                try:
                    with open(os.path.join(self.gv['TEMP_DIR_HOME'], 
                                           requested_print_parameters_name), 'r') as requested_parameters_file:
                        self.requested_parameters_dict = json.load(requested_parameters_file)
                except json.decoder.JSONDecodeError as e:
                    WarningQMessageBox(self, self.gv,
                                   f'Error loading requested printer parameters for {self.temp_sender_name}\n{str(e)}')

        # store files in dict
        for attachment in self.mail_manager.getAttachments(job_msg):
            attachment_name = self.mail_manager.getAttachmentFileName(attachment)
            if attachment_name.lower().endswith(self.gv['ACCEPTED_EXTENSIONS']):
                self.temp_make_items.append(attachment)
            else:
                target_file_global_path = os.path.join(self.temp_job_folder_global_path, attachment_name)
                self.temp_store_files_dict[attachment_name] = {'attachment': attachment,
                                             'target_file_global_path': target_file_global_path}

        self.loadItemContent()


    @abc.abstractmethod
    def loadItemContent(self):
        ''' Load content of mail item into dialog. '''


class CreateJobsFromFileSystemQDialog(CreateJobsQDialog):
    ''' Create jobs from file system data. '''

    def __init__(self,
                 parent: QWidget,
                 gv: dict,
                 job_tracker: JobTracker,
                 job_name_list,
                 files_global_paths_list,
                 *args,
                 update_existing_job=False,
                 job_dict_list=None,
                 **kwargs):


        assert len(job_name_list) == len(files_global_paths_list),\
            f'job_name_list and files_global_paths_list are not equal length {len(job_name_list)} and {len(files_global_paths_list)}'

        if update_existing_job:

            assert job_dict_list is not None, 'job_dict_list is None'
            assert len(job_dict_list) == len(job_name_list),\
                f'job_dict_list and job_name_list are not equal length {len(job_dict_list)} and {len(job_name_list)}'


        self.jobs = job_name_list
        self.files_global_paths_list = files_global_paths_list
        self.update_existing_job = update_existing_job
        self.job_dict_list = job_dict_list

        super().__init__(parent,
                         gv,
                         os.path.join(gv['LOCAL_UI_DIR'], 'enter_job_details_dialog.ui'),
                         job_tracker,
                         *args,
                         **kwargs)



    def loadJobContent(self):
        ''' Load content into dialog. '''

        if self.update_existing_job:

            self.temp_job_name = self.jobs[self.job_counter]
            self.temp_job_dict = self.job_dict_list[self.job_counter]

            self.temp_make_files_dict = self.temp_job_dict['make_files']
            self.temp_job_folder_name = os.path.basename(self.temp_job_dict['job_folder_global_path'])
            self.temp_job_folder_global_path = self.temp_job_dict['job_folder_global_path']

        else:
            self.temp_job_name = self.job_tracker.makeJobNameUnique(self.jobs[self.job_counter])
            self.temp_job_dict = None
            self.temp_make_files_dict = {}

            self.temp_job_folder_name = str(datetime.date.today().strftime('%d-%m'))+'_'+self.temp_job_name
            self.temp_job_folder_global_path = os.path.join(os.path.join(self.gv['JOBS_DIR_HOME'], self.temp_job_folder_name))

        temp_make_items = []
        self.temp_store_files_dict = {}


        for file_global_path in self.files_global_paths_list[self.job_counter]:
            if file_global_path.lower().endswith(self.gv['ACCEPTED_EXTENSIONS']):
                temp_make_items.append(file_global_path)
            else:
                store_file_name = os.path.basename(file_global_path)
                target_file_global_path = os.path.join(self.temp_job_folder_global_path, store_file_name)
                self.temp_store_files_dict[store_file_name] = {'source_file_global_path': file_global_path,
                                             'target_file_global_path': target_file_global_path}
                
        
        self.temp_make_items = temp_make_items

        self.jobNameQLabel.setText(self.temp_job_name)
        self.jobProgressQLabel.setText(f'Job ({self.job_counter+1}/{len(self.jobs)})')

        self.loadItemContent()

    @abc.abstractmethod
    def loadItemContent(self):
        ''' Load content of mail item into dialog. '''

    def createJob(self):
        ''' Create a job. '''

        if self.update_existing_job:

            # temp_job_dict given? then a job exist on FS and only the tracker should be updated
            self.temp_job_dict['make_files'] = self.temp_make_files_dict
            self.job_tracker.addJob(self.temp_job_dict['job_name'], None, None,  job_dict=self.temp_job_dict)

            # Rename files to name in tracker file
            for file_name in os.listdir(self.temp_job_dict['job_folder_global_path']):
                if file_name.lower().endswith(self.gv['ACCEPTED_EXTENSIONS']):
                    for file_dict in self.temp_make_files_dict.values():
                        if file_dict['file_name'].endswith(file_name):
                            os.rename(os.path.join(
                            self.temp_job_dict['job_folder_global_path'], file_name), file_dict['file_global_path'])


            TimedMessage(self, self.gv, text=f'Updated job: {self.temp_job_name}')
        else:
            self.job_tracker.addJob(self.temp_job_name,
                                    self.temp_job_folder_global_path,
                                    self.temp_make_files_dict)

            if not os.path.exists(self.temp_job_folder_global_path):
                os.mkdir(self.temp_job_folder_global_path)

            for item_dict in self.temp_store_files_dict.values():
                copy_item(item_dict['source_file_global_path'], item_dict['target_file_global_path'])

            TimedMessage(self, self.gv, text=f'Created job: {self.temp_job_name}')

        self.parent().refreshAllWidgets()

class SelectQDialog(QDialog):
    ''' Select file dialog. '''
    def __init__(self, parent, gv: dict, ui_global_path: str, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.gv=gv

        loadUi(ui_global_path, self)

        # shortcut on Esc button
        QShortcut(QKeySequence(Qt.Key.Key_Escape), self).activated.connect(self.close)


class SearchJobDialog(QDialog):
    ''' Search all existing jobs in a dialog. '''
    def __init__(self, parent: QWidget, ui_global_path: str, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        loadUi(ui_global_path, self)

        self.searchLineEdit.textChanged.connect(self.refreshSearch)
        QShortcut(QKeySequence(Qt.Key.Key_Escape), self).activated.connect(self.close)

        self.listWidget.main_window = parent.window()

        QShortcut(QKeySequence(Qt.Key.Key_Down), self).activated.connect(self.toNextRow)
        QShortcut(QKeySequence(Qt.Key.Key_Up), self).activated.connect(self.toPreviousRow)
        QShortcut(QKeySequence('Ctrl+n'), self).activated.connect(self.toNextRow)
        QShortcut(QKeySequence('Ctrl+p'), self).activated.connect(self.toPreviousRow)

    def refreshSearch(self):
        ''' Add the matching jobs to the qlistwidget. '''
        self.listWidget.refreshWithMatch(self.searchLineEdit.text())

    def toNextRow(self):
        widget = self.listWidget

        if widget.currentRow() == widget.count()-1:
            widget.setCurrentRow(0)
        else:
            widget.setCurrentRow(widget.currentRow()+1)

    def toPreviousRow(self):
        widget = self.listWidget

        if widget.currentRow() == 0:
            widget.setCurrentRow(widget.count()-1)
        else:
            widget.setCurrentRow(widget.currentRow()-1)


class FilesSelectQDialog(SelectQDialog):
    ''' Select files dialog. '''
    def __init__(self, parent: QWidget, gv: dict, *args, **kwargs):
        ui_global_path = os.path.join(gv['GLOBAL_UI_DIR'], 'select_files_dialog.ui')
        super().__init__(parent, gv, ui_global_path, *args, **kwargs)

        self.buttonBox.accepted.connect(self.validate)

    def validate(self):

        if len(self.selectFilesButton.files_global_paths) == 0:
            dlg = QMessageBox(self)
            dlg.setText('Select Files')
            dlg.exec()
            return

        contains_accepted_extension = False
        for file_global_path in self.selectFilesButton.files_global_paths:
            if file_global_path.lower().endswith(self.gv['ACCEPTED_EXTENSIONS']):
                contains_accepted_extension = True

        if not contains_accepted_extension:
            dlg = QMessageBox(self)
            dlg.setText(f'Selected files should contain one or more files with extension {self.gv["ACCEPTED_EXTENSIONS"]}')
            dlg.exec()
            return

        if len(self.projectNameQLineEdit.text()) == 0:
            dlg = QMessageBox(self)
            dlg.setText('Provide a Job Name')
            dlg.exec()
            return

        self.accept()


class FolderSelectQDialog(SelectQDialog):
    ''' Select folder dialog. '''
    def __init__(self, parent: QWidget, gv: dict, *args, **kwargs):
        ui_global_path = os.path.join(gv['GLOBAL_UI_DIR'], 'select_folders_dialog.ui')
        super().__init__(parent, gv, ui_global_path, *args, **kwargs)

        self.buttonBox.accepted.connect(self.validate)

    def validate(self):

        if self.selectFolderButton.folder_global_path is None:
            dlg = QMessageBox(self)
            dlg.setText('Select a Folder')
            dlg.exec()
            return

        if len(self.projectNameQLineEdit.text()) == 0:
            dlg = QMessageBox(self)
            dlg.setText('Provide a Project Name')
            dlg.exec()
            return

        self.accept()

class SelectOptionsQDialog(QDialog):
    ''' Select one of the options. '''

    def __init__(self, parent: QWidget, gv: dict, options: list, *args, question='Select Options',  **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.gv = gv

        assert len(options) > 0, f'options should contain at least one option, it contains {len(option)}'

        loadUi(os.path.join(self.gv['GLOBAL_UI_DIR'], 'select_options_dialog.ui'), self)
        self.label.setText(question)

        # shortcuts on arrow keys
        QShortcut(QKeySequence(Qt.Key.Key_Up), self).activated.connect(self.toPreviousRow)
        QShortcut(QKeySequence(Qt.Key.Key_Down), self).activated.connect(self.toNextRow)

        # shortcuts on VIM motions
        QShortcut(QKeySequence('k'), self).activated.connect(self.toPreviousRow)
        QShortcut(QKeySequence('j'), self).activated.connect(self.toNextRow)
        QShortcut(QKeySequence('Ctrl+p'), self).activated.connect(self.toPreviousRow)
        QShortcut(QKeySequence('Ctrol+n'), self).activated.connect(self.toNextRow)

        for option_tuple in options:
            item = QListWidgetItem()
            item.setFont(QFont('Cantarell', 14))
            if isinstance(option_tuple, str):
                item.setText(option_tuple)

            elif len(option_tuple) == 2:
                option, option_data = option_tuple
                item.setText(option)
                item.setData(1, option_data)

            elif len(options[0]) == 3:
                option, option_data, option_bool = option_tuple
                if option_bool:
                    item.setText('✅ '+option)
                else:
                    item.setText('❎ '+option)
                item.setData(1, option_data)

            else: 
                raise ValueError(f'tuples in options list should be of length 2 or 3 not {len(options[0])}') 

            self.optionsQListWidget.addItem(item)


    def toNextRow(self):
        opt_ql_widget = self.optionsQListWidget

        if opt_ql_widget.currentRow() == opt_ql_widget.count()-1:
            opt_ql_widget.setCurrentRow(0)
        else:
            opt_ql_widget.setCurrentRow(opt_ql_widget.currentRow()+1)

    def toPreviousRow(self):
        opt_ql_widget = self.optionsQListWidget

        if opt_ql_widget.currentRow() == 0:
            opt_ql_widget.setCurrentRow(opt_ql_widget.count()-1)
        else:
            opt_ql_widget.setCurrentRow(opt_ql_widget.currentRow()-1)


class AboutDialog(QDialog):
    ''' Display information about creator administrator. '''

    def __init__(self, parent: QWidget, gv: dict, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        loadUi(os.path.join(gv['GLOBAL_UI_DIR'], 'about_widget.ui') , self)

        self.versionLabel.setText(pkg_resources.get_distribution('creator_administrator').version)
        self.githubSiteLabel.mousePressEvent = self.openGithubInBrowser

        if gv['DARK_THEME']:
            self.githubSiteLabel.setStyleSheet("QLabel { color : aqua; }");
        else:
            self.githubSiteLabel.setStyleSheet("QLabel { color : blue; }");


        # shortcut on Esc button
        QShortcut(QKeySequence(Qt.Key.Key_Escape), self).activated.connect(self.close)

    def openGithubInBrowser(self, _):
        ''' Open Github in browser. '''
        webbrowser.open('https://github.com/GijsGroote/creator_administrator/')


class QuestionsQDialog(QDialog):
    ''' Anser a simple question. '''

    def __init__(self, parent: QWidget, gv: dict, question: str, *args, validate_answer_function=None, unvalid_answer_str=None, **kwargs):

        super().__init__(parent, *args, **kwargs)

        loadUi(os.path.join(gv['GLOBAL_UI_DIR'], 'text_input_dialog.ui'), self)

        self.answer = None
        self.validate_answer_function = validate_answer_function
        self.unvalid_answer_str = unvalid_answer_str
        self.gv = gv
        self.questionLabel.setText(question)
        self.buttonBox.accepted.connect(self.validate)

    def validate(self):

        answer = self.answerLineEdit.text()

        if answer == '':
            dlg = QMessageBox(self)
            dlg.setText('Enter Answer')
            dlg.exec()
            return

        if self.validate_answer_function is not None and not self.validate_answer_function(answer):
            assert self.unvalid_answer_str is not None, 'unvalid_answer_str is None'
            dlg = QMessageBox(self)
            dlg.setText(self.unvalid_answer_str)
            dlg.exec()
            return

        self.answer = str(answer)
        self.accept()


