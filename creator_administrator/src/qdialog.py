import os
import abc
import webbrowser
import pkg_resources

from PyQt6.QtWidgets import QDialog, QWidget, QListWidgetItem, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut, QFont
from PyQt6.uic import loadUi


from src.mail_manager import MailManager
from src.threaded_mail_manager import ThreadedMailManager
from src.job_tracker import JobTracker 


class CreateJobsQDialog(QDialog):
    ''' Create jobs with data from mail or the file system. '''

    def __init__(self,
                 parent: QWidget,
                 gv: dict,
                 ui_global_path: str,
                 job_tracker: JobTracker,
                 *args, 
                 valid_msgs=None,
                 job_name_list=None,
                 files_global_paths_list=None,
                 **kwargs):
        super().__init__(parent, *args, **kwargs)

        assert valid_msgs is not None or\
               job_name_list is not None and files_global_paths_list is not None,\
                'supply either valid_msgs or job_name_list and files_global_paths_list'

        loadUi(ui_global_path, self)

        self.gv=gv
        self.mail_manager = MailManager(gv)
        self.job_tracker = job_tracker 
        self.threadpool = gv['THREAD_POOL']

        self.valid_msgs = valid_msgs
        self.msg_counter = 0
        self.attachment_counter = 0
        self.new_material_text = 'New Material'
        self.new_materials_list = []


        self.skipPushButton.clicked.connect(self.skipMail)
        self.buttonBox.accepted.connect(self.collectAttachmentInfo)

        # shortcut on Esc button
        QShortcut(QKeySequence(Qt.Key.Key_Escape), self).activated.connect(self.close)

        self.loadContent()

    def collectFileInfo(self):
        ''' Collect info for the current file displayed. '''
        if self.valid_msgs is not None:
            self.collectInfoFromMailAttachment()
        elif self.job_name_list is not None and self.files_global_paths_list is not None:
            self.collectInfoFromLocalFile()
        raise ValueError('data to create jobs is not supplied')

    @abc.abstractmethod
    def collectInfoFromMailAttachment(self):
        ''' Collect info from mail attachment. '''

    @abc.abstractmethod
    def collectInfoFromLocalFile(self):
        ''' Collect info from a local file. '''



    # TODO: make this go through mails or through files on file system
    def loadContent(self):
        if self.attachment_counter >= len(self.temp_attachments):
            self.threadedSendReceivedMailAndCreateLaserJob()
            self.msg_counter += 1
            self.attachment_counter = 0

            if self.msg_counter >= len(self.valid_msgs):
                # done! close dialog
                self.accept() 
            else:
                self.loadMailContent()
        else:
            self.loadAttachmentContent()


    def loadMailContent(self):
        ''' Load content of mail into dialog. '''

        valid_msg = self.valid_msgs[self.msg_counter]

        self.temp_attachments = self.mail_manager.getAttachments(valid_msg)
        self.temp_sender_name = self.mail_manager.getSenderName(valid_msg)

        self.temp_laser_cut_files_dict = {}
        self.temp_attachments_dict = {}

        self.mailFromQLabel.setText(self.temp_sender_name)
        self.mailProgressQLabel.setText(f'Mail ({self.msg_counter+1}/{len(self.valid_msgs)})')

        self.temp_job_name = self.job_tracker.makeJobNameUnique(self.temp_sender_name)
        self.temp_job_folder_name = str(datetime.date.today().strftime('%d-%m'))+'_'+self.temp_job_name
        self.temp_job_folder_global_path = os.path.join(os.path.join(gv['JOBS_DIR_HOME'], self.temp_job_folder_name))

        mail_body = self.mail_manager.getMailBody(valid_msg)
        if isinstance(mail_body, bytes):
            mail_body = mail_body.decode('utf-8')

        self.mailQWebEngineView.setHtml(mail_body)
        self.loadAttachmentContent()


    def loadAttachmentContent(self):
        ''' Load content of attachment into dialog. '''

        attachment = self.temp_attachments[self.attachment_counter]
        attachment_name = self.mail_manager.getAttachmentFileName(attachment)

        if attachment_name.lower().endswith(gv['ACCEPTED_EXTENSIONS']):
            self.attachmentProgressQLabel.setText(f'Attachment ({self.attachment_counter+1}/{len(self.temp_attachments)})')
            self.attachmentNameQLabel.setText(attachment_name)

            # initially hide option for new material 
            self.newMaterialQLabel.setHidden(True)
            self.newMaterialQLineEdit.setHidden(True)

            self.materialQComboBox.clear()
            self.newMaterialQLineEdit.clear()
            self.thicknessQLineEdit.clear()
            self.amountQLineEdit.clear()

            materials = list(set(gv['ACCEPTED_MATERIALS']).union(self.job_tracker.getExistingMaterials()).union(self.new_materials_list))
            self.materialQComboBox.addItems(materials)
            self.materialQComboBox.addItem(self.new_material_text)

            # guess the material, thickness and amount
            for material in materials:
                if material.lower() in attachment_name.lower():
                    self.materialQComboBox.setCurrentIndex(self.materialQComboBox.findText(material))
            match = re.search(r"\d+\.?\d*(?=mm)", attachment_name)

            if match:
                self.thicknessQLineEdit.setText(match.group())

            match = re.search(r"\d+\.?\d*(?=x_)", attachment_name)
            if match:
                self.amountQLineEdit.setText(match.group())
            else:
                self.amountQLineEdit.setText('1')

        else:
            file_global_path = os.path.join(self.temp_job_folder_global_path, attachment_name)
            self.temp_attachments_dict[attachment_name] = {'attachment': attachment,
                                                     'file_global_path': file_global_path}
            self.attachment_counter += 1
            self.loadContent()

    def collectAttachmentInfo(self):
        ''' Collect material, thickness and amount info. '''
        material = self.materialQComboBox.currentText()
        if material == self.new_material_text:
            material = self.newMaterialQLineEdit.text()
            self.new_materials_list.append(material)

        thickness = self.thicknessQLineEdit.text()
        amount = self.amountQLineEdit.text()
        
        if not validate_material_info(self, material, thickness, amount):
            return

        attachment = self.temp_attachments[self.attachment_counter]
        original_file_name = self.mail_manager.getAttachmentFileName(attachment)

        attachment = self.temp_attachments[self.attachment_counter]
        original_file_name = self.mail_manager.getAttachmentFileName(attachment)

        if material in original_file_name and\
            thickness in original_file_name and\
            amount in original_file_name:
            file_name= original_file_name
        else:
            file_name = material+'_'+thickness+'mm_'+amount+'x_'+original_file_name

        file_global_path = os.path.join(self.temp_job_folder_global_path, file_name)
    
        self.temp_laser_cut_files_dict[self.temp_job_name + '_' + file_name] = {
                            'file_name': file_name,
                            'file_global_path': file_global_path,
                            'material': material,
                            'thickness': thickness,
                            'amount': amount,
                            'done': False}
        self.temp_attachments_dict[file_name] = {'attachment': attachment,
                                                     'file_global_path': file_global_path}
        self.attachment_counter += 1
        self.loadContent()

    def skipMail(self):
        ''' Skip mail and go to the next. '''
        if self.msg_counter+1 >= len(self.valid_msgs):
            self.accept() 
        else:
            self.msg_counter += 1
            self.attachment_counter = 0
            self.loadMailContent()



# class ImportFromMailQDialog(QDialog):
#     """ Import from mail dialog. """
#     def __init__(self, parent: QWidget, gv: dict, ui_global_path: str, *args, **kwargs):
#         super().__init__(parent, *args, **kwargs)
#         self.gv=gv

#         loadUi(ui_global_path, self)
        
#         # shortcut on Esc button
#         QShortcut(QKeySequence(Qt.Key.Key_Escape), self).activated.connect(self.closeDialog)

    # def closeDialog(self):
    #     ''' Close the dialog, press cancel. '''
    #     self.close()


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
    """ Import from mail dialog. """
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
