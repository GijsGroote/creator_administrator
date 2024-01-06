import os
import re
from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets, uic
from PyQt5.QtWidgets import *

from typing import Tuple
import datetime
from global_variables import gv
from src.qdialog import ImportFromMailQDialog, SelectFileQDialog
from src.mail_manager import MailManager

from laser_job_tracker import LaserJobTracker

from src.convert_functions import mail_to_name, make_job_name_unique


class LaserImportFromMailQDialog(ImportFromMailQDialog):

    def __init__(self, parent, valid_msgs, *args, **kwargs):
        ui_global_path = os.path.join(gv['REPO_DIR_HOME'], 'laser/ui/import_mail_dialog.ui')
        ImportFromMailQDialog.__init__(self, parent, ui_global_path, *args, **kwargs)

        self.mail_manager = parent.mail_manager
        self.valid_msgs = valid_msgs
        self.msg_counter = 0
        self.attachment_counter = 0
        self.new_material_text = 'New Material'
        self.job_tracker = LaserJobTracker()
        self.loadMailContent()

        self.materialQComboBox.currentIndexChanged.connect(self.onMaterialComboboxChanged)

        self.buttonBox.accepted.connect(self.collectAttachmentInfo)


    def loadContent(self):
        if self.attachment_counter+1 >= len(self.temp_attachments):
            self.createLaserJob()
            self.sendConfirmationMail()

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

        self.mailFromQLabel.setText(f'Mail From: {mail_to_name(self.mail_manager.getEmailAddress(valid_msg))}')
        self.mailProgressQLabel.setText(f'Mail ({self.msg_counter+1}/{len(self.valid_msgs)})')

        sender_name = mail_to_name(self.mail_manager.getEmailAddress(valid_msg))

        self.temp_job_name = make_job_name_unique(gv, sender_name)
        self.temp_job_folder_name = str(datetime.date.today().strftime('%d-%m'))+'_'+self.temp_job_name
        self.temp_job_folder_global_path = os.path.join(os.path.join(gv['JOBS_DIR_HOME'], self.temp_job_folder_name))

        self.mailQWebEngineView.setHtml(self.mail_manager.getMailBody(valid_msg).decode('utf-8'))
        self.loadAttachmentContent()


    def loadAttachmentContent(self):
        ''' Load content of attachment into dialog. '''

        attachment = self.temp_attachments[self.attachment_counter]
        attachment_name = self.mail_manager.getAttachmentFileName(attachment)

        if attachment_name.endswith(gv['ACCEPTED_EXTENSIONS']):
            self.attachmentProgressQLabel.setText(f'Attachment ({self.attachment_counter+1}/{len(self.temp_attachments)})')
            self.attachmentNameQLabel.setText(f'File Name: {attachment_name}')

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
                                         material+'_'+thickness+'_'+amount+'x_'+'_'+attachment_name)

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



    def sendConfirmationMail(self):

        # send a confirmation mail
        msg_file_path = self.mail_manager.getMailGlobalPathFromFolder(self.temp_job_folder_global_path)
        self.mail_manager.replyToEmailFromFileUsingTemplate(msg_file_path,
                                "RECEIVED_MAIL_TEMPLATE",
                                {"{jobs_in_queue}": self.job_tracker.getNumberOfJobsInQueue()},
                                popup_reply=False)

        self.mail_manager.moveEmailToVerwerktFolder(self.valid_msgs[self.msg_counter])


    def createLaserJob(self):
        """ Create a laser job. """
        msg = self.valid_msgs[self.msg_counter]

        self.job_tracker.addJob(self.temp_job_name,
                                 self.temp_job_folder_global_path,
                                 self.temp_laser_cut_files_dict)

        os.mkdir(self.temp_job_folder_global_path)
        self.mail_manager.saveMail(msg, self.temp_job_folder_global_path)

        # save the attachments
        print('the attachments in a dict')
        for attachment_dict in self.temp_attachments_dict.values():
            print(attachment_dict)
            self.mail_manager.saveAttachment(attachment_dict['attachment'], attachment_dict['file_global_path'])


class LaserSelectFileQDialog(SelectFileQDialog):
    """ Select file dialog. """
    def __init__(self, parent, *args, **kwargs):
        ui_global_path = os.path.join(gv['REPO_DIR_HOME'], 'laser/ui/select_file_dialog.ui')
        SelectFileQDialog.__init__(self, parent, ui_global_path, *args, **kwargs)

        self.buttonBox.accepted.connect(self.validate)


    def validate(self):
        if self.PasswordQLineEdit.text() != gv['PASSWORD']:
            dlg = QMessageBox(self)
            dlg.setText('Password Incorrect')
            dlg.exec()
            return

        if self.selectFolderButton.folder_global_path is None:
            dlg = QMessageBox(self)
            dlg.setText('Select a Folder')
            button = dlg.exec()
            return

        if len(self.ProjectNameQLineEdit.text()) == 0:
            dlg = QMessageBox(self)
            dlg.setText('Provide a Project Name')
            button = dlg.exec()
            return

        self.accept()

