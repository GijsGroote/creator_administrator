import os
import re
from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5 import QtWebEngineWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


from PyQt5.uic import loadUi

import datetime
from global_variables import gv
from src.qdialog import ImportFromMailQDialog, SelectQDialog

from src.mail_manager import MailManager
from src.qmessagebox import TimedMessage, ErrorQMessageBox

from requests.exceptions import ConnectionError
from laser_job_tracker import LaserJobTracker
from src.worker import Worker
from src.directory_functions import copy



class LaserImportFromMailQDialog(ImportFromMailQDialog):

    def __init__(self, parent, valid_msgs, *args, **kwargs):
        ui_global_path = os.path.join(gv['REPO_DIR_HOME'], 'laser/ui/import_mail_dialog.ui')
        super().__init__(parent, ui_global_path, *args, **kwargs)

        self.mail_manager = MailManager(gv)
        self.valid_msgs = valid_msgs
 
        self.msg_counter = 0
        self.attachment_counter = 0
        self.new_material_text = 'New Material'


        self.threadpool = gv['THREAD_POOL']

        self.job_tracker = LaserJobTracker(self)

        self.materialQComboBox.currentIndexChanged.connect(self.onMaterialComboboxChanged)

        # self.findChild(QPushButton, 'skipPushButton').clicked.connect(self.skipMail)
        self.skipPushButton.clicked.connect(self.skipMail)

        self.sendUnclearMailPushButton.clicked.connect(self.sendUnclearMaterialDetailsMail)
        self.buttonBox.accepted.connect(self.collectAttachmentInfo)

        self.loadMailContent()


    def loadContent(self):
        if self.attachment_counter+1 >= len(self.temp_attachments):
            self.createLaserJob()

            send_mail_worker = Worker(self.sendConfirmationMail)
            send_mail_worker.signals.finished.connect(self.confirmationMailSendMessage)
            send_mail_worker.signals.error.connect(self.handleMailError)
            self.threadpool.start(send_mail_worker)

            if self.msg_counter+1 >= len(self.valid_msgs):
                # done! close dialog
                self.accept() 
            else:
                self.msg_counter += 1
                self.attachment_counter = 0
                self.loadMailContent()
        else:
            self.attachment_counter += 1
            self.loadAttachmentContent()


    def loadMailContent(self):
        ''' Load content of mail into dialog. '''

        valid_msg = self.valid_msgs[self.msg_counter]


        self.temp_attachments = self.mail_manager.getAttachments(valid_msg)

        self.temp_laser_cut_files_dict = {}
        self.temp_attachments_dict = {}


        sender_name = self.mail_manager.getSenderName(valid_msg)
        self.mailFromQLabel.setText(sender_name)
        self.mailProgressQLabel.setText(f'Mail ({self.msg_counter+1}/{len(self.valid_msgs)})')

        self.temp_job_name = self.job_tracker.makeJobNameUnique(sender_name)
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

            materials = list(set(gv['ACCEPTED_MATERIALS']).union(self.job_tracker.getExistingMaterials()))
            self.materialQComboBox.addItems(materials)
            self.materialQComboBox.addItem(self.new_material_text)

            # guess the material, thickness and amount
            for material in gv['ACCEPTED_MATERIALS']:
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

            if self.attachment_counter+1 >= len(self.temp_attachments):
                self.createLaserJob()
                self.sendConfirmationMail()

                if self.msg_counter+1 >= len(self.temp_attachments):
                    self.msg_counter += 1
                    self.loadMailContent()
            else:
                self.attachment_counter += 1
                self.loadAttachmentContent()

    def onMaterialComboboxChanged(self):
        if self.materialQComboBox.currentText() == self.new_material_text:
            self.newMaterialQLabel.setHidden(False)
            self.newMaterialQLineEdit.setHidden(False)
        else:
            self.newMaterialQLabel.setHidden(True)
            self.newMaterialQLineEdit.setHidden(True)
        
    def collectAttachmentInfo(self):
        ''' Collect material, thickness and amount info. '''
        material = self.materialQComboBox.currentText()
        if material == self.new_material_text:
            material = self.newMaterialQLineEdit.text()
        thickness = self.thicknessQLineEdit.text()
        amount = self.amountQLineEdit.text()
        
        if not self.validate(material, thickness, amount):
            return

        attachment = self.temp_attachments[self.attachment_counter]
        attachment_name = self.mail_manager.getAttachmentFileName(attachment)

        file_global_path = os.path.join(self.temp_job_folder_global_path,
                                         material+'_'+thickness+'_'+amount+'x_'+attachment_name)

        self.temp_laser_cut_files_dict[self.temp_job_name + '_' + attachment_name] = {
                            'file_name': attachment_name,
                            'file_global_path': file_global_path,
                            'material': material,
                            'thickness': thickness,
                            'amount': amount,
                            'done': False}
        self.temp_attachments_dict[attachment_name] = {'attachment': attachment,
                                                     'file_global_path': file_global_path}
        self.loadContent()

    def skipMail(self):
        ''' Skip mail and go to the next. '''
        # TODO: mail should not go to verwerkt folder, move it back
        if self.msg_counter+1 >= len(self.valid_msgs):
            self.accept() 
        else:
            self.msg_counter += 1
            self.attachment_counter = 0
            self.loadMailContent()

    def validate(self, material: str, thickness: str, amount: str) -> bool:
        for (thing, value) in [('material', material), ('thickness', thickness), ('amount', amount)]:
            if value == "":
                dlg = QMessageBox(self)
                dlg.setText(f'Fill in {thing}')
                dlg.exec()
                return False

        try:
            thickness_float = float(thickness)
        except Exception:
            dlg = QMessageBox(self)
            dlg.setText(f'Thickness should be a positive number, not {thickness}')
            dlg.exec()
            return False
        if thickness_float <=0:
            dlg = QMessageBox(self)
            dlg.setText(f'Thickness should be a positive number, not {thickness}')
            dlg.exec()
            return False

        try:
            amount_int = int(amount)
        except Exception:
            dlg = QMessageBox(self)
            dlg.setText(f'Amount should be a positive interger, not: {amount}')
            dlg.exec()
            return False

        if amount_int <= 0:
            dlg = QMessageBox(self)
            dlg.setText(f'Amount should be a positive interger, not: {amount}')
            dlg.exec()
            return False

        return True


    def sendUnclearMaterialDetailsMail(self):
        ''' Send a mail asking for the material, thickness and amount. '''
        print(f"unclear stuff hyo")
        # TODO: mail from a mail that is not yet downloaded. 


#         # send a confirmation mail
#         msg_file_path = self.mail_manager.getMailGlobalPathFromFolder(self.temp_job_folder_global_path)
# TODO: do net forget ConnectionError
#         self.mail_manager.replyToEmailFromFileUsingTemplate(msg_file_path,
#                                 "RECEIVED_MAIL_TEMPLATE",
#                                 {"{jobs_in_queue}": self.job_tracker.getNumberOfJobsInQueue()},
#                                 popup_reply=False)

#         self.mail_manager.moveEmailToVerwerktFolder(self.valid_msgs[self.msg_counter])

        # TimedQMessageBox(
        #             text=f"Confirmation mail send to {self.temp_job_name}",
        #             parent=self)

        TimedMessage(gv, self, f"This function is not yet implemented")



    def sendConfirmationMail(self):
        ''' Send a confirmation mail. ''' 

        self.mail_manager.replyToEmailFromFileUsingTemplate(
                msg_file_path=self.mail_manager.getMailGlobalPathFromFolder(self.temp_job_folder_global_path), 
                template_file_name="RECEIVED_MAIL_TEMPLATE",
                template_content={"{jobs_in_queue}": self.job_tracker.getNumberOfJobsInQueue()},
                popup_reply=False)
        self.mail_manager.moveEmailToVerwerktFolder(
                                  msg=self.valid_msgs[self.msg_counter])

    def confirmationMailSendMessage(self):
        ''' Display a message with: confimation mail send. '''
        # job_name = data
        TimedMessage(gv, parent=self, text=f'Confimation mail send')

    def handleMailError(self, exc):
        ''' Handle mail error. '''

        assert isinstance(exc, Exception), f'Expected type Exception, received type: {type(exc)}'

        if isinstance(exc, ConnectionError):
            ErrorQMessageBox(self,
                    text=f'Error: {str(exc)}')
        else:
            ErrorQMessageBox(self, text=f'Error Occured: {str(exc)}')


    def createLaserJob(self):
        """ Create a laser job. """
        msg = self.valid_msgs[self.msg_counter]

        self.job_tracker.addJob(self.temp_job_name,
                                 self.temp_job_folder_global_path,
                                 self.temp_laser_cut_files_dict)


        if not os.path.exists(self.temp_job_folder_global_path):
            os.mkdir(self.temp_job_folder_global_path)

        self.mail_manager.saveMail(msg, self.temp_job_folder_global_path)

        # save the attachments
        for attachment_dict in self.temp_attachments_dict.values():
            self.mail_manager.saveAttachment(attachment_dict['attachment'], attachment_dict['file_global_path'])

        # TimedMessage(self, text=f'Laser job {self.temp_job_name} created')

class LaserFilesSelectQDialog(SelectQDialog):
    """ Select files dialog. """
    def __init__(self, parent, *args, **kwargs):
        ui_global_path = os.path.join(gv['REPO_DIR_HOME'], 'laser/ui/select_files_dialog.ui')
        super().__init__(parent, ui_global_path, *args, **kwargs)
        self.filesGlobalPathsQLabel.hide()

        self.buttonBox.accepted.connect(self.validate)

    def validate(self):
        if self.passwordQLineEdit.text() != gv['PASSWORD']:
            dlg = QMessageBox(self)
            dlg.setText('Password Incorrect')
            dlg.exec()
            return

        if len(self.selectFilesButton.files_global_paths) == 0:
            dlg = QMessageBox(self)
            dlg.setText('Select Files')
            dlg.exec()
            return

        contains_accepted_extension = False
        for file_global_path in self.selectFilesButton.files_global_paths:
            if file_global_path.lower().endswith(gv['ACCEPTED_EXTENSIONS']):
                contains_accepted_extension = True

        if not contains_accepted_extension:
            dlg = QMessageBox(self)
            dlg.setText(f'Select should contain one or more files with extension {gv["ACCEPTED_EXTENSIONS"]}')
            dlg.exec()
            return

        if len(self.projectNameQLineEdit.text()) == 0:
            dlg = QMessageBox(self)
            dlg.setText('Provide a Job Name')
            dlg.exec()
            return

        self.accept()

class LaserFolderSelectQDialog(SelectQDialog):
    """ Select folder dialog. """
    def __init__(self, parent, *args, **kwargs):
        ui_global_path = os.path.join(gv['REPO_DIR_HOME'], 'laser/ui/select_folders_dialog.ui')
        super().__init__(parent, ui_global_path, *args, **kwargs)

        self.buttonBox.accepted.connect(self.validate)

    def validate(self):
        if self.passwordQLineEdit.text() != gv['PASSWORD']:
            dlg = QMessageBox(self)
            dlg.setText('Password Incorrect')
            dlg.exec_()
            return

        if self.selectFolderButton.folder_global_path is None:
            dlg = QMessageBox(self)
            dlg.setText('Select a Folder')
            dlg.exec_()
            return

        if len(self.projectNameQLineEdit.text()) == 0:
            dlg = QMessageBox(self)
            dlg.setText('Provide a Project Name')
            dlg.exec_()
            return

        self.accept()

class LaserFileInfoQDialog(QDialog):
    ''' Ask for file laser file details (material, thickness, amount) and create laser jobs.
    job_name: List with job names
    files_global_paths_list: nested lists with global paths for every file in the job.  

    '''


    def __init__(self, parent, job_name_list: list, files_global_paths_list: list, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        loadUi(os.path.join(gv['REPO_DIR_HOME'], 'laser/ui/job_details_dialog.ui'), self)

        assert len(job_name_list) == len(files_global_paths_list),\
            f'length of job name list: {len(job_name_list)} should'\
            f'be equal to the files_global_path_list: {len(files_global_paths_list)}'

        self.job_tracker = LaserJobTracker(self)
        self.job_counter = 0
        self.file_counter = 0
        self.job_name_list = job_name_list
        self.files_global_paths_list = files_global_paths_list
        self.temp_job_name = self.job_tracker.makeJobNameUnique(self.job_name_list[self.job_counter])
        self.temp_files_global_paths = files_global_paths_list[self.job_counter]
 
        self.new_material_text = 'New Material'
        self.materialQComboBox.currentIndexChanged.connect(self.onMaterialComboboxChanged)
        self.skipPushButton.clicked.connect(self.skipJob)
        self.buttonBox.accepted.connect(self.collectFileInfo)
        self.loadJobContent()

    def loadContent(self):
        if self.file_counter+1 >= len(self.temp_files_global_paths):
            self.createLaserJob()

            if self.job_counter+1 >= len(self.job_name_list):
                self.accept()
            else:
                self.job_counter += 1
                self.file_counter= 0
                self.loadJobContent()
        else:
            # self.attachment_counter += 1
            self.loadFileContent()


    def loadJobContent(self):
        ''' Load content of mail into dialog. '''

        self.temp_job_name = self.job_tracker.makeJobNameUnique(self.job_name_list[self.job_counter])
        self.temp_files_global_paths = self.files_global_paths_list[self.job_counter]

        self.temp_laser_cut_files_dict = {}
        self.temp_files_dict = {}

        self.jobNameQLabel.setText(self.temp_job_name)
        self.jobProgressQLabel.setText(f'Job ({self.job_counter+1}/{len(self.job_name_list)})')

        self.temp_job_folder_name = str(datetime.date.today().strftime('%d-%m'))+'_'+self.temp_job_name
        self.temp_job_folder_global_path = os.path.join(os.path.join(gv['JOBS_DIR_HOME'], self.temp_job_folder_name))
        self.loadFileContent()


    def loadFileContent(self):
        ''' Load content of attachment into dialog. '''

        file_global_path = self.temp_files_global_paths[self.file_counter]
        file_name = os.path.basename(file_global_path)
        print(f"loading this file now {file_name}")

        if file_name.lower().endswith(gv['ACCEPTED_EXTENSIONS']):
            self.fileProgressQLabel.setText(f'File({self.file_counter+1}/{len(self.temp_files_global_paths)})')
            self.fileNameQLabel.setText(file_name)

            # initially hide option for new material 
            self.newMaterialQLabel.setHidden(True)
            self.newMaterialQLineEdit.setHidden(True)

            self.materialQComboBox.clear()
            self.newMaterialQLineEdit.clear()
            self.thicknessQLineEdit.clear()
            self.amountQLineEdit.clear()

            materials = list(set(gv['ACCEPTED_MATERIALS']).union(self.job_tracker.getExistingMaterials()))
            self.materialQComboBox.addItems(materials)
            self.materialQComboBox.addItem(self.new_material_text)

            # guess the material, thickness and amount
            for material in gv['ACCEPTED_MATERIALS']:
                if material.lower() in file_name.lower():
                    self.materialQComboBox.setCurrentIndex(self.materialQComboBox.findText(material))
            match = re.search(r"\d+\.?\d*(?=mm)", file_name)
            if match:
                self.thicknessQLineEdit.setText(match.group())

            match = re.search(r"\d+\.?\d*(?=x_)", file_name)
            if match:
                self.amountQLineEdit.setText(match.group())
            else:
                self.amountQLineEdit.setText('1')

        else:
            file_global_path = os.path.join(self.temp_job_folder_global_path, file_name)
            self.temp_files_dict[file_name] = {'source_file_global_path': file_global_path,
                                             'target_file_global_path': self.temp_files_global_paths[self.file_counter]}

            print(f"correct you txt file file {self.temp_files_dict[file_name]}")

            if self.file_counter+1 >= len(self.temp_files_global_paths):
                self.createLaserJob()

                if self.job_counter+1 >= len(self.job_name_list):
                    self.job_counter += 1
                    self.loadJobContent()
            else:
                self.file_counter += 1
                self.loadFileContent()

    def onMaterialComboboxChanged(self):
        if self.materialQComboBox.currentText() == self.new_material_text:
            self.newMaterialQLabel.setHidden(False)
            self.newMaterialQLineEdit.setHidden(False)
        else:
            self.newMaterialQLabel.setHidden(True)
            self.newMaterialQLineEdit.setHidden(True)
        
    def collectFileInfo(self):
        ''' Collect material, thickness and amount info. '''
        material = self.materialQComboBox.currentText()
        if material == self.new_material_text:
            material = self.newMaterialQLineEdit.text()
        thickness = self.thicknessQLineEdit.text()
        amount = self.amountQLineEdit.text()
        
        if not self.validate(material, thickness, amount):
            return


        source_file_global_path = self.temp_files_global_paths[self.file_counter]
        print(f"this is a  full path right {source_file_global_path}")
        file_name = os.path.basename(source_file_global_path)


        target_file_global_path = os.path.join(self.temp_job_folder_global_path,
                                         material+'_'+thickness+'_'+amount+'x_'+file_name)

        self.temp_laser_cut_files_dict[self.temp_job_name + '_' + file_name] = {
                            'file_name': file_name,
                            'file_global_path': target_file_global_path,
                            'material': material,
                            'thickness': thickness,
                            'amount': amount,
                            'done': False}

        self.temp_files_dict[file_name] = {'source_file_global_path': source_file_global_path,
                                             'target_file_global_path': target_file_global_path}
        self.loadContent()

    def skipJob(self):
        ''' Skip job and go to the next. '''
        if self.job_counter+1 >= len(self.job_name_list):
            self.accept() 
        else:

            self.job_counter += 1
            self.file_counter = 0
            self.loadJobContent()

    def validate(self, material: str, thickness: str, amount: str) -> bool:
        for (thing, value) in [('material', material), ('thickness', thickness), ('amount', amount)]:
            if value == "":
                dlg = QMessageBox(self)
                dlg.setText(f'Fill in {thing}')
                dlg.exec()
                return False

        try:
            thickness_float = float(thickness)
        except Exception:
            dlg = QMessageBox(self)
            dlg.setText(f'Thickness should be a positive number, not {thickness}')
            dlg.exec()
            return False
        if thickness_float <=0:
            dlg = QMessageBox(self)
            dlg.setText(f'Thickness should be a positive number, not {thickness}')
            dlg.exec()
            return False

        try:
            amount_int = int(amount)
        except Exception:
            dlg = QMessageBox(self)
            dlg.setText(f'Amount should be a positive interger, not: {amount}')
            dlg.exec()
            return False

        if amount_int <= 0:
            dlg = QMessageBox(self)
            dlg.setText(f'Amount should be a positive interger, not: {amount}')
            dlg.exec()
            return False

        return True

    def createLaserJob(self):
        """ Create a laser job. """

        self.job_tracker.addJob(self.temp_job_name,
                                 self.temp_job_folder_global_path,
                                 self.temp_laser_cut_files_dict)

        if not os.path.exists(self.temp_job_folder_global_path):
            os.mkdir(self.temp_job_folder_global_path)

        # save the attachments
        for file_dict in self.temp_files_dict.values():
            copy(file_dict['source_file_global_path'], file_dict['target_file_global_path'])

        TimedMessage(self, text=f"Laser job {self.temp_job_name} created")

