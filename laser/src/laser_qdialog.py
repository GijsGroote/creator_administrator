import os
from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets, uic
from PyQt5.QtWidgets import QDialog, QMessageBox, QLabel, QLineEdit

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
        self.loadMailContent()

        self.buttonBox.accepted.connect(self.collectAttachmentInfo)



    def loadMailContent(self):
        ''' Load content of mail into dialog. '''

        valid_msg = self.valid_msgs[self.msg_counter]

        self.findChild(QLabel, 'mailQLabel').setText(
                f'Mail ({self.msg_counter+1}/{len(self.valid_msgs)}) from: '
                f'{mail_to_name(self.mail_manager.getEmailAddress(valid_msg))}')

        print(f"Can I set this mailqlabel please to ")

        self.temp_attachments = self.mail_manager.getAttachments(valid_msg)
        print(f"hoeveeel ataccchhments zitter hierin {self.temp_attachments}")
        print(f"hoeveeel ataccchhments zitter hierin {len(self.temp_attachments)}")
        self.temp_laser_cut_files_dict = {}
        self.temp_attachments_dict = {}

        sender_name = mail_to_name(self.mail_manager.getEmailAddress(valid_msg))

        self.temp_job_name = make_job_name_unique(gv, sender_name)
        self.temp_job_folder_name = str(datetime.date.today().strftime('%d-%m'))+'_'+self.temp_job_name
        self.temp_job_folder_global_path = os.path.join(os.path.join(gv['JOBS_DIR_HOME'], self.temp_job_folder_name))

        self.loadAttachmentContent()

        #TODO load the mail into the design template

    def loadAttachmentContent(self):
        ''' Load content of attachment into dialog. '''

        print(f"huh hoeveel in temp atach {len(self.temp_attachments)} ")
        print(f"hoe hoog is de counter? {self.attachment_counter}')")

        attachment = self.temp_attachments[self.attachment_counter]
        attachment_name = self.mail_manager.getAttachmentFileName(attachment)

        if attachment_name.endswith(gv['ACCEPTED_EXTENSIONS']):

            self.findChild(QLabel, 'attachmentQLabel').setText(
                    f'Attachments ({self.attachment_counter+1}/{len(self.temp_attachments)})')
            self.findChild(QLabel, 'attachmentsNameQLabel').setText(
                    f'File Name: {attachment_name}')

            # TODO: load with what you think is going to be the material
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
        
    def collectAttachmentInfo(self):
        ''' Collect material, thickness and amount info. '''
        material = self.findChild(QLineEdit, 'materialQLineEdit').text()
        thickness = self.findChild(QLineEdit, 'thicknessQLineEdit').text()
        amount = self.findChild(QLineEdit, 'amountQLineEdit').text()

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

        if self.attachment_counter+1 >= len(self.temp_attachments):
            self.createLaserJob()
            self.sendConfirmationMail()


            if self.msg_counter+1 >= len(self.valid_msgs):
                print(f"you MUST accept and fuck off please now")
                self.accept()
            else:
                self.msg_counter += 1
                self.attachment_counter = 0
                self.loadMailContent()
        else:

            self.attachment_counter += 1
            print(f"hoe hoo gi se counter {self.attachment_counter} paula")
            self.loadAttachmentContent()


    def sendConfirmationMail(self):

        # send a confirmation mail
        msg_file_path = self.mail_manager.getMailGlobalPathFromFolder(self.temp_job_folder_global_path)
        self.mail_manager.replyToEmailFromFileUsingTemplate(msg_file_path,
                                "RECEIVED_MAIL_TEMPLATE",
                                {"{jobs_in_queue}": LaserJobTracker().getNumberOfJobsInQueue()},
                                popup_reply=False)

        self.mail_manager.moveEmailToVerwerktFolder(self.valid_msgs[self.msg_counter])


    def createLaserJob(self):
        """ Create a laser job. """
        msg = self.valid_msgs[self.msg_counter]


        LaserJobTracker().addJob(self.temp_job_name,
                                 self.temp_job_folder_global_path,
                                 self.temp_laser_cut_files_dict)

        os.mkdir(self.temp_job_folder_global_path)
        self.mail_manager.saveMail(msg, self.temp_job_folder_global_path)

        # save the attachments
        for attachment_dict in self.temp_attachments_dict.values():
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

