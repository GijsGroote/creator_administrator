import os
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
        if self.make_item_counter+1 >= len(self.jobs):
            self.accept()
        else:
            self.job_counter += 1
            self.make_item_counter = 0
            self.loadContent()

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

        self.temp_make_items = self.mail_manager.getAttachments(job_msg)
        self.temp_sender_name = self.mail_manager.getSenderName(job_msg)

        self.temp_make_files_dict = {}
        self.temp_store_files_dict = {}

        self.mailFromQLabel.setText(self.temp_sender_name)
        self.mailProgressQLabel.setText(f'Mail ({self.job_counter+1}/{len(self.jobs)})')

        self.temp_job_name = self.job_tracker.makeJobNameUnique(self.temp_sender_name)
        self.temp_job_folder_name = str(datetime.date.today().strftime('%d-%m'))+'_'+self.temp_job_name
        self.temp_job_folder_global_path = os.path.join(os.path.join(self.gv['JOBS_DIR_HOME'], self.temp_job_folder_name))

        mail_body = self.mail_manager.getMailBody(job_msg)
        if isinstance(mail_body, bytes):
            mail_body = mail_body.decode('utf-8')

        self.mailQWebEngineView.setHtml(mail_body)
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
                 **kwargs):

        assert len(job_name_list) == len(files_global_paths_list),\
            f'length of job name list: {len(job_name_list)} should'\
            f'be equal to the files_global_path_list: {len(files_global_paths_list)}'

        super().__init__(parent,
                         gv,
                         os.path.join(gv['LOCAL_UI_DIR'], 'enter_job_details_dialog.ui'),
                         job_tracker,
                         *args,
                         **kwargs)

        self.jobs = job_name_list
        self.files_global_paths_list = files_global_paths_list

    def loadJobContent(self):
        ''' Load content of mail into dialog. '''

        self.temp_job_name = self.job_tracker.makeJobNameUnique(self.jobs[self.job_counter])
        self.temp_make_items = self.files_global_paths_list[self.job_counter]

        self.temp_make_files_dict = {}
        self.temp_store_files_dict = {}

        self.jobNameQLabel.setText(self.temp_job_name)
        self.jobProgressQLabel.setText(f'Job ({self.job_counter+1}/{len(self.jobs)})')

        self.temp_job_folder_name = str(datetime.date.today().strftime('%d-%m'))+'_'+self.temp_job_name
        self.temp_job_folder_global_path = os.path.join(os.path.join(self.gv['JOBS_DIR_HOME'], self.temp_job_folder_name))
        self.loadItemContent()

    @abc.abstractmethod
    def loadItemContent(self):
        ''' Load content of mail item into dialog. '''


class SelectQDialog(QDialog):
    """ Select file dialog. """
    def __init__(self, parent, gv: dict, ui_global_path: str, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.gv=gv

        loadUi(ui_global_path, self)

        # shortcut on Esc button
        QShortcut(QKeySequence(Qt.Key.Key_Escape), self).activated.connect(self.closeDialog)

    def closeDialog(self):
        ''' Close the dialog, press cancel. '''
        self.close()


class FilesSelectQDialog(SelectQDialog):
    """ Select files dialog. """
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
    """ Select folder dialog. """
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

    def __init__(self, parent: QWidget, gv: dict, options: list, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.gv = gv


        loadUi(os.path.join(self.gv['GLOBAL_UI_DIR'], 'select_done_dialog.ui'), self)

        # shortcuts on arrow keys
        QShortcut(QKeySequence(Qt.Key.Key_Up), self).activated.connect(self.toPreviousRow)
        QShortcut(QKeySequence(Qt.Key.Key_Down), self).activated.connect(self.toNextRow)

        # shortcuts on VIM motions
        QShortcut(QKeySequence('k'), self).activated.connect(self.toPreviousRow)
        QShortcut(QKeySequence('j'), self).activated.connect(self.toNextRow)

        for (option, option_data, done) in options:

            item = QListWidgetItem()
            item.setData(1, option_data)

            if isinstance(done, bool):
                if done:
                    item.setText('✅ '+option)
                else:
                    item.setText('❎ '+option)
            else:
                    item.setText(option)

            item.setFont(QFont('Cantarell', 14))
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
    """ Display information about creator administrator. """

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
        QShortcut(QKeySequence(Qt.Key.Key_Escape), self).activated.connect(self.closeDialog)

    def openGithubInBrowser(self, _):
        ''' Open Github in browser. '''
        webbrowser.open('https://github.com/GijsGroote/creator_administrator/')

    def closeDialog(self):
        ''' Close the dialog, press cancel. '''
        self.close()


