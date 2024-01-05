import os
from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets, uic
from PyQt5.QtWidgets import QDialog, QMessageBox, QLabel

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

        mail_qlabel = self.findChild(QLabel, 'mailQLabel')
        # loop over all mails, check if they are valid and create laser jobs
        for i, msg in enumerate(valid_msgs):

            print(f"Can I set this mailqlabel please to ")
            print(f'Mail ({i}/{len(valid_msgs)}) from: {mail_to_name(self.mail_manager.getEmailAddress(msg))}')

            mail_qlabel.setText(f'Mail ({i}/{len(valid_msgs)}) from: {mail_to_name(self.mail_manager.getEmailAddress(msg))}')
            self.handleMailMessage(msg)

        print('you can accept now')

        self.accept()


    def handleMailMessage(self, msg):
        ''' handle mail message and create laser job. '''

        sender_name = mail_to_name(self.mail_manager.getEmailAddress(msg))

        job_name = make_job_name_unique(gv, sender_name)
        job_folder_name = str(datetime.date.today().strftime('%d-%m'))+'_'+job_name
        job_folder_global_path = os.path.join(os.path.join(gv['JOBS_DIR_HOME'], job_folder_name))

        # find material, thickness and amount
        files_dict, attachments_dict = self.enterLaserFileDetails(msg, job_name, job_folder_global_path)


        
        self.create_laser_job(msg, job_name, job_folder_global_path, files_dict, attachments_dict)

        # send a confirmation mail
        msg_file_path = self.mail_manager.getMailGlobalPathFromFolder(job_folder_global_path)
        self.mail_manager.replyToEmailFromFileUsingTemplate(msg_file_path,
                                "RECEIVED_MAIL_TEMPLATE",
                                {"{jobs_in_queue}": LaserJobTracker().getNumberOfJobsInQueue()},
                                popup_reply=False)

        self.mail_manager.moveEmailToVerwerktFolder(msg)



    def enterLaserFileDetails(self, msg, job_name: str, job_folder_global_path: str) -> Tuple[dict, dict]:
        """ Return the material, thickness and amount for all (valid) attachments of a laser job. """

        laser_cut_files_dict = {}
        attachments_dict = {}
        attachments = self.mail_manager.getAttachments(msg)

        for i, attachment in enumerate(attachments):

            attachment_name = self.mail_manager.getAttachmentFileName(attachment)

            if attachment_name.lower().endswith(gv['ACCEPTED_EXTENSIONS']):

                self.findChild(QLabel, 'attachmentQLabel').setText(f'attachment ({i}/{len(attachments)}')

                self.mail_manager.printMailBody(msg)

                # TODO: continue here please
                material, thickness, amount = self.enterMaterialThicknessAmount(attachment_name)

                file_global_path = os.path.join(job_folder_global_path,
                                         material+'_'+thickness+'_'+amount+'x_'+'_'+attachment_name)

                laser_cut_files_dict[job_name + '_' + attachment_name] = {
                                    'file_name': attachment_name,
                                    'file_global_path': file_global_path,
                                    'material': material,
                                    'thickness': thickness,
                                    'amount': amount,
                                    'done': False}

                attachments_dict[attachment_name] = {'attachment': attachment,
                                                     'file_global_path': file_global_path}
            else:
                file_global_path = os.path.join(job_folder_global_path, attachment_name)
                attachments_dict[attachment_name] = {'attachment': attachment,
                                                     'file_global_path': file_global_path}


        return laser_cut_files_dict, attachments_dict


    def create_laser_job(self, msg, job_name: str, job_folder_global_path: str, files_dict: dict, attachments_dict: dict):
        """ Create a laser job. """

        LaserJobTracker().addJob(job_name, job_folder_global_path, files_dict)

        os.mkdir(job_folder_global_path)
        self.mail_manager.saveMail(msg, job_folder_global_path)

        # save the attachments
        for attachment_dict in attachments_dict.values():
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

