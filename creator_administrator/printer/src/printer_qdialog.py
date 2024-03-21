import os
import re

from PyQt6.QtWidgets import QWidget

from src.qdialog import CreateJobsFromMailQDialog, CreateJobsFromFileSystemQDialog
from src.qmessagebox import TimedMessage
from src.threaded_mail_manager import ThreadedMailManager

from printer_job_tracker import PrintJobTracker
from printer_validate import validate_material_info

from global_variables import gv

class CreatePrintJobsFromMailQDialog(CreateJobsFromMailQDialog):
    ''' Create print jobs from mail data. '''

    def __init__(self,
                 parent: QWidget,
                 valid_msgs,
                 *args,
                 **kwargs):

        super().__init__(parent,
                         gv,
                         PrintJobTracker(self),
                         valid_msgs,
                         *args,
                         **kwargs)

        # TODO; settings based on printer profile

        self.loadJobContent()


    def loadItemContent(self):
        ''' Load content of attachment into dialog. '''

        attachment = self.temp_make_items[self.make_item_counter]
        attachment_name = self.mail_manager.getAttachmentFileName(attachment)

        self.attachmentProgressQLabel.setText(f'Attachment ({self.make_item_counter+1}/{len(self.temp_make_items)})')
        self.attachmentNameQLabel.setText(attachment_name)

        # initially hide option for new material
        self.newMaterialQLabel.setHidden(True)
        self.newMaterialQLineEdit.setHidden(True)

        self.materialQComboBox.clear()
        self.newMaterialQLineEdit.clear()
        self.amountQLineEdit.clear()

        materials = list(set(gv['ACCEPTED_MATERIALS']).union(self.job_tracker.getExistingMaterials()).union(self.new_materials_list))
        self.materialQComboBox.addItems(materials)
        self.materialQComboBox.addItem(self.new_material_text)

        # guess the amount
        match = re.search(r"\d+\.?\d*(?=x_)", attachment_name)
        if match:
            self.amountQLineEdit.setText(match.group())
        else:
            self.amountQLineEdit.setText('1')


    def collectItemInfo(self):
        ''' Collect material amount info. '''
        material = self.materialQComboBox.currentText()
        if material == self.new_material_text:
            material = self.newMaterialQLineEdit.text()
            self.new_materials_list.append(material)

        amount = self.amountQLineEdit.text()

        if not validate_material_info(self, material, amount):
            return

        attachment = self.temp_make_items[self.make_item_counter]
        original_file_name = self.mail_manager.getAttachmentFileName(attachment)

        attachment = self.temp_make_items[self.make_item_counter]
        original_file_name = self.mail_manager.getAttachmentFileName(attachment)

        if material in original_file_name and\
            amount in original_file_name:
            file_name= original_file_name
        else:
            file_name = material+'_'+amount+'x_'+original_file_name

        file_global_path = os.path.join(self.temp_job_folder_global_path, file_name)

        self.temp_make_files_dict[self.temp_job_name + '_' + file_name] = {
                            'file_name': file_name,
                            'file_global_path': file_global_path,
                            'material': material,
                            'amount': amount,
                            'done': False}

        self.temp_store_files_dict[file_name] = {'attachment': attachment,
                                                 'target_file_global_path': file_global_path}
        self.make_item_counter += 1
        self.loadContent()

    def createJob(self):
        """ Create a print job. """

        msg = self.jobs[self.job_counter]
        sender_mail_adress = self.mail_manager.getEmailAddress(msg)
        sender_mail_receive_time = self.mail_manager.getSenderMailReceiveTime(msg)

        self.job_tracker.addJob(self.temp_job_name,
                                self.temp_job_folder_global_path,
                                self.temp_make_files_dict,
                                sender_name=self.temp_sender_name,
                                sender_mail_adress=sender_mail_adress,
                                sender_mail_receive_time=sender_mail_receive_time)

        if not os.path.exists(self.temp_job_folder_global_path):
            os.mkdir(self.temp_job_folder_global_path)

        self.mail_manager.saveMail(msg, self.temp_job_folder_global_path)

        # save the attachments
        for attachment_dict in self.temp_store_files_dict.values():
            self.mail_manager.saveAttachment(attachment_dict['attachment'], attachment_dict['target_file_global_path'])

        self.parent().refreshAllWidgets()

        ThreadedMailManager(parent=self, gv=gv).startMailWorker(
                sender_name=self.temp_sender_name,
                mail_type='RECEIVED',
                mail_item=msg,
                move_mail_to_verwerkt=True,
                template_content= {"{jobs_in_queue}": self.job_tracker.getNumberOfJobsInQueue()},
                sender_mail_adress=sender_mail_adress,
                sender_mail_receive_time=sender_mail_receive_time)

        TimedMessage(self, gv, f'Created {self.temp_job_name}')


class CreatePrintJobsFromFileSystemQDialog(CreateJobsFromFileSystemQDialog):
    ''' Create print jobs from file system data. '''

    def __init__(self, parent, job_name_list: list, files_global_paths_list: list, *args, **kwargs):


        super().__init__(parent,
                         gv,
                         PrintJobTracker(self),
                         job_name_list,
                         files_global_paths_list,
                         *args, **kwargs)

        self.skipPushButton.clicked.connect(self.skipJob)
        self.loadJobContent()


    def loadItemContent(self):
        ''' Load content local file into dialog. '''
        assert not len(self.temp_make_items) == 0, 'make_files_items contains no items'

        file_global_path = self.temp_make_items[self.make_item_counter]
        file_name = os.path.basename(file_global_path)

        self.fileProgressQLabel.setText(f'File({self.make_item_counter+1}/{len(self.temp_make_items)})')
        self.fileNameQLabel.setText(file_name)

        self.materialQComboBox.clear()
        self.newMaterialQLineEdit.clear()
        self.amountQLineEdit.clear()

        materials = list(set(gv['ACCEPTED_MATERIALS']).union(self.job_tracker.getExistingMaterials()).union(self.new_materials_list))
        self.materialQComboBox.addItems(materials)
        self.materialQComboBox.addItem(self.new_material_text)

        # guess the amount
        match = re.search(r"\d+\.?\d*(?=x_)", file_name)
        if match:
            self.amountQLineEdit.setText(match.group())
        else:
            self.amountQLineEdit.setText('1')


    def collectItemInfo(self):
        ''' Collect material and amount info. '''
        material = self.materialQComboBox.currentText()
        if material == self.new_material_text:
            material = self.newMaterialQLineEdit.text()
            self.new_materials_list.append(material)

        amount = self.amountQLineEdit.text()

        if not validate_material_info(self, material, amount):
            return

        source_file_global_path = self.temp_make_items[self.make_item_counter]

        original_file_name = os.path.basename(source_file_global_path)
        if material in original_file_name and\
            amount in original_file_name:
            file_name = original_file_name
        else:
            file_name = material+'_'+amount+'x_'+original_file_name

        target_file_global_path = os.path.join(self.temp_job_folder_global_path, file_name)

        self.temp_make_files_dict[self.temp_job_name + '_' + file_name] = {
                            'file_name': file_name,
                            'file_global_path': target_file_global_path,
                            'material': material,
                            'amount': amount,
                            'done': False}

        self.temp_store_files_dict[file_name] = {'source_file_global_path': source_file_global_path,
                                             'target_file_global_path': target_file_global_path}
        self.make_item_counter += 1
        self.loadContent()
