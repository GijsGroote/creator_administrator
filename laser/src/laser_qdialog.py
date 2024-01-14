import os
import re
from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5 import QtWebEngineWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import time

from src.app import get_thread_pool
import datetime
from global_variables import gv
from src.qdialog import ImportFromMailQDialog, SelectQDialog

from src.mail_manager import MailManager
from src.qmessagebox import TimedQMessageBox

from requests.exceptions import ConnectionError
from laser_job_tracker import LaserJobTracker
from src.worker import Worker

from src.app import get_thread_pool


class LaserImportFromMailQDialog(ImportFromMailQDialog):

    def __init__(self, parent, valid_msgs, *args, **kwargs):
        ui_global_path = os.path.join(gv['REPO_DIR_HOME'], 'laser/ui/import_mail_dialog.ui')
        super().__init__(parent, ui_global_path, *args, **kwargs)


        self.mail_manager = parent.mail_manager
        self.valid_msgs = valid_msgs
 
        self.msg_counter = 0
        self.attachment_counter = 0
        self.new_material_text = 'New Material'


        # self.threadpool = get_thread_pool(self)


        self.job_tracker = LaserJobTracker()
        self.loadMailContent()



        self.materialQComboBox.currentIndexChanged.connect(self.onMaterialComboboxChanged)


        # self.findChild(QPushButton, 'skipPushButton').clicked.connect(self.skipMail)

        self.skipPushButton.clicked.connect(self.skipMail)

        self.sendUnclearMailPushButton.clicked.connect(self.sendUnclearMaterialDetailsMail)
        self.buttonBox.accepted.connect(self.collectAttachmentInfo)

    def loadContent(self):
        if self.attachment_counter+1 >= len(self.temp_attachments):
            self.createLaserJob()

            # msg = self.valid_msgs[self.msg_counter]
            self.sendConfirmationMail()


            # self.sendConfirmationMail()

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
                print(f"fuck it is you, not good")
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
        if self.msg_counter+1 >= len(self.valid_msgs):
            # done! close dialog
            self.accept() 

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

        TimedQMessageBox(
                    text=f"This function is not yet implemented",
                    parent=self)



    def sendConfirmationMail(self):
        ''' Send a confirmation mail on a new thread. ''' 

        try:
            self.mail_manager.replyToEmailFromFileUsingTemplate(
                    msg_file_path=self.mail_manager.getMailGlobalPathFromFolder(self.temp_job_folder_global_path), 
                    template_file_name="RECEIVED_MAIL_TEMPLATE",
                    template_content={"{jobs_in_queue}": self.job_tracker.getNumberOfJobsInQueue()},
                    popup_reply=False)
            self.mail_manager.moveEmailToVerwerktFolder(
                                      msg=self.valid_msgs[self.msg_counter])
        except ConnectionError as e:
            TimedQMessageBox(
                    text=str(e),
                    parent=self, icon=QMessageBox.Critical)
            return

        # make workers
        # send_mail_worker = Worker(self.mail_manager.replyToEmailFromFileUsingTemplate,
        #         msg_file_path=self.mail_manager.getMailGlobalPathFromFolder(self.temp_job_folder_global_path), 
        #         template_file_name="RECEIVED_MAIL_TEMPLATE",
        #         template_content={"{jobs_in_queue}": self.job_tracker.getNumberOfJobsInQueue()},
        #         popup_reply=False)
        # move_mail_worker = Worker(self.mail_manager.moveEmailToVerwerktFolder,
        #                           msg=self.valid_msgs[self.msg_counter])

        # # start workers
        # self.threadpool.start(send_mail_worker)
        # self.threadpool.start(move_mail_worker)
    
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

        TimedQMessageBox(
                    text=f"Laser job {self.temp_job_name} created",
                    parent=self)

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

        if len(self.selectFilesButton.folder_global_path) == 0:
            dlg = QMessageBox(self)
            dlg.setText('Select Files')
            dlg.exec()
            return

        if len(self.ProjectNameQLineEdit.text()) == 0:
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
            button = dlg.exec()
            return

        if len(self.ProjectNameQLineEdit.text()) == 0:
            dlg = QMessageBox(self)
            dlg.setText('Provide a Project Name')
            button = dlg.exec()
            return

        self.accept()

