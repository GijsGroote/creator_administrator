import os
import re
import sys
import copy
from PyQt6 import *
from PyQt6.QtCore import *
from PyQt6 import QtWebEngineWidgets
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from PyQt6.uic import loadUi

import datetime
from global_variables import gv
from src.qdialog import ImportFromMailQDialog, SelectQDialog

from src.mail_manager import MailManager
from src.qmessagebox import TimedMessage, ErrorQMessageBox

from requests.exceptions import ConnectionError
from laser_job_tracker import LaserJobTracker
from src.worker import Worker
from src.threaded_mail_manager import ThreadedMailManager
from src.directory_functions import copy_item
  

class LaserImportFromMailQDialog(ImportFromMailQDialog):

    def __init__(self, parent, valid_msgs, *args, **kwargs):
        ui_global_path = os.path.join(gv['REPO_DIR_HOME'], 'laser/ui/import_mail_dialog.ui')
        super().__init__(parent, ui_global_path, *args, **kwargs)

        self.mail_manager = MailManager(gv)
        self.valid_msgs = valid_msgs
 
        self.msg_counter = 0
        self.attachment_counter = 0
        self.new_material_text = 'New Material'
        self.new_materials_list = []

        self.threadpool = gv['THREAD_POOL']

        self.job_tracker = LaserJobTracker(self)

        self.materialQComboBox.currentIndexChanged.connect(self.onMaterialComboboxChanged)

        self.skipPushButton.clicked.connect(self.skipMail)
        self.sendUnclearMailPushButton.clicked.connect(self.sendUnclearRequestMailJob)
        self.buttonBox.accepted.connect(self.collectAttachmentInfo)

        self.loadMailContent()


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
            self.new_materials_list.append(material)

        thickness = self.thicknessQLineEdit.text()
        amount = self.amountQLineEdit.text()
        
        if not self.validate(material, thickness, amount):
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

    def sendUnclearRequestMailJob(self):
        ''' Send a mail asking for the material, thickness and amount. '''

        # save mail in TEMP folder
        msg = self.valid_msgs[self.msg_counter]
        self.temp_job_folder_global_path = os.path.join(gv['DATA_DIR_HOME'], 'TEMP', self.temp_job_name)

        if not os.path.exists(self.temp_job_folder_global_path):
            os.mkdir(self.temp_job_folder_global_path)

        self.mail_manager.saveMail(msg, self.temp_job_folder_global_path)

        ThreadedMailManager(parent_widget=self, gv=gv).startUnclearMailWorker(
                success_message=f'Unclear request mail send to {self.temp_sender_name}',
                error_message=f'No unclear request mail was send to {self.temp_sender_name}',
                job_folder_global_path=copy.copy(self.temp_job_folder_global_path),
                template_content= {})
                
        self.skipMail()

    def threadedSendReceivedMailAndCreateLaserJob(self):
        """ Create a laser job. """
        msg = self.valid_msgs[self.msg_counter]
        
        self.job_tracker.addJob(self.temp_job_name,
                                self.temp_sender_name,
                                self.temp_job_folder_global_path,
                                self.temp_laser_cut_files_dict)

        if not os.path.exists(self.temp_job_folder_global_path):
            os.mkdir(self.temp_job_folder_global_path)

        self.mail_manager.saveMail(msg, self.temp_job_folder_global_path)

        # save the attachments
        for attachment_dict in self.temp_attachments_dict.values():
            self.mail_manager.saveAttachment(attachment_dict['attachment'], attachment_dict['file_global_path'])
        
        ThreadedMailManager(parent_widget=self, gv=gv).startReceivedMailWorker(
                success_message=f'Job request receieved mail send to {self.temp_sender_name}',
                error_message=f'No job request receieved mail send to {self.temp_sender_name}',
                job_folder_global_path=copy.copy(self.temp_job_folder_global_path),
                template_content= {"{jobs_in_queue}": self.job_tracker.getNumberOfJobsInQueue()},
                msg=msg)
                
        TimedMessage(gv, self, text=f'Laser job {self.temp_job_name} created')

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
            dlg.exec()
            return

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

class LaserFileInfoQDialog(QDialog):
    ''' Ask for file laser file details (material, thickness, amount) and create laser jobs.
    job_name: List with job names
    files_global_paths_list: nested lists with global paths for every file in the job.  

    '''

    def __init__(self, parent, job_name_list: list, files_global_paths_list: list, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        loadUi(os.path.join(gv['REPO_DIR_HOME'], 'laser/ui/enter_job_details_dialog.ui'), self)

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
        self.new_materials_list = []

        self.materialQComboBox.currentIndexChanged.connect(self.onMaterialComboboxChanged)
        self.skipPushButton.clicked.connect(self.skipJob)
        self.buttonBox.accepted.connect(self.collectFileInfo)
        self.loadJobContent()

    def loadContent(self):
        if self.file_counter >= len(self.temp_files_global_paths):
            self.createLaserJob()

            if self.job_counter+1 >= len(self.job_name_list):
                self.accept()
            else:
                self.job_counter += 1
                self.file_counter= 0
                self.loadJobContent()
        else:
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

            materials = list(set(gv['ACCEPTED_MATERIALS']).union(self.job_tracker.getExistingMaterials()).union(self.new_materials_list))
            self.materialQComboBox.addItems(materials)
            self.materialQComboBox.addItem(self.new_material_text)

            # guess the material, thickness and amount
            for material in materials:
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

            if self.file_counter+1 >= len(self.temp_files_global_paths):
                self.createLaserJob()
                self.job_counter += 1

                if self.job_counter >= len(self.job_name_list):
                    self.loadJobContent()
            else:
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
            self.new_materials_list.append(material)
            
        thickness = self.thicknessQLineEdit.text()
        amount = self.amountQLineEdit.text()
        
        if not self.validate(material, thickness, amount):
            return

        source_file_global_path = self.temp_files_global_paths[self.file_counter]

        original_file_name = os.path.basename(source_file_global_path)
        if material in original_file_name and\
            thickness in original_file_name and\
            amount in original_file_name:
            file_name = original_file_name
        else:
            file_name = material+'_'+thickness+'mm_'+amount+'x_'+original_file_name
        
        target_file_global_path = os.path.join(self.temp_job_folder_global_path, file_name)

        self.temp_laser_cut_files_dict[self.temp_job_name + '_' + file_name] = {
                            'file_name': file_name,
                            'file_global_path': target_file_global_path,
                            'material': material,
                            'thickness': thickness,
                            'amount': amount,
                            'done': False}

        self.temp_files_dict[file_name] = {'source_file_global_path': source_file_global_path,
                                             'target_file_global_path': target_file_global_path}
        self.file_counter += 1
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
                                'No Sender Name',
                                self.temp_job_folder_global_path,
                                self.temp_laser_cut_files_dict)

        if not os.path.exists(self.temp_job_folder_global_path):
            os.mkdir(self.temp_job_folder_global_path)

        # save the attachments
        for file_dict in self.temp_files_dict.values():
            copy_item(file_dict['source_file_global_path'], file_dict['target_file_global_path'])

        TimedMessage(gv, self, text=f"Laser job {self.temp_job_name} created")

