import os
import re

from PyQt6.QtWidgets import QWidget

from src.qdialog import CreateJobsFromMailQDialog, CreateJobsFromFileSystemQDialog
from src.qmessagebox import TimedMessage
from src.threaded_mail_manager import ThreadedMailManager
from src.directory_functions import copy_item

from laser_job_tracker import LaserJobTracker
from laser_validate import validate_material_info

from global_variables import gv


class CreateLaserJobsFromMailQDialog(CreateJobsFromMailQDialog):
    ''' Create laser jobs with data from mail or the file system. '''

    def __init__(self,
                 parent: QWidget,
                 valid_msgs,
                 *args,
                 **kwargs):

        super().__init__(parent,
                         gv,
                         os.path.join(gv['LOCAL_UI_DIR'], 'import_mail_dialog.ui'),
                         LaserJobTracker(self),
                         valid_msgs,
                         *args,
                         **kwargs)

        self.new_material_text = 'New Material'
        self.new_materials_list = []

        self.sendUnclearMailPushButton.clicked.connect(self.sendUnclearRequestMailJob)
        self.materialQComboBox.currentIndexChanged.connect(self.onMaterialComboboxChanged)

        self.loadJobContent()


    def loadItemContent(self):
        ''' Load content of attachment into dialog. '''

        attachment = self.temp_make_items[self.make_item_counter]
        attachment_name = self.mail_manager.getAttachmentFileName(attachment)

        if attachment_name.lower().endswith(gv['ACCEPTED_EXTENSIONS']):
            self.attachmentProgressQLabel.setText(f'Attachment ({self.make_item_counter+1}/{len(self.temp_make_items)})')
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
            self.temp_store_files_dict[attachment_name] = {'attachment': attachment,
                                                     'file_global_path': file_global_path}
            self.make_item_counter += 1
            self.loadContent()


    def onMaterialComboboxChanged(self):
        if self.materialQComboBox.currentText() == self.new_material_text:
            self.newMaterialQLabel.setHidden(False)
            self.newMaterialQLineEdit.setHidden(False)
        else:
            self.newMaterialQLabel.setHidden(True)
            self.newMaterialQLineEdit.setHidden(True)

    def collectItemInfo(self):
        ''' Collect material, thickness and amount info. '''
        material = self.materialQComboBox.currentText()
        if material == self.new_material_text:
            material = self.newMaterialQLineEdit.text()
            self.new_materials_list.append(material)

        thickness = self.thicknessQLineEdit.text()
        amount = self.amountQLineEdit.text()

        if not validate_material_info(self, material, thickness, amount):
            return

        attachment = self.temp_make_items[self.make_item_counter]
        original_file_name = self.mail_manager.getAttachmentFileName(attachment)

        attachment = self.temp_make_items[self.make_item_counter]
        original_file_name = self.mail_manager.getAttachmentFileName(attachment)

        if material in original_file_name and\
            thickness in original_file_name and\
            amount in original_file_name:
            file_name= original_file_name
        else:
            file_name = material+'_'+thickness+'mm_'+amount+'x_'+original_file_name

        file_global_path = os.path.join(self.temp_job_folder_global_path, file_name)

        self.temp_make_files_dict[self.temp_job_name + '_' + file_name] = {
                            'file_name': file_name,
                            'file_global_path': file_global_path,
                            'material': material,
                            'thickness': thickness,
                            'amount': amount,
                            'done': False}
        self.temp_store_files_dict[file_name] = {'attachment': attachment,
                                                     'file_global_path': file_global_path}
        self.make_item_counter += 1
        self.loadContent()

    def sendUnclearRequestMailJob(self):
        ''' Send a mail asking for the material, thickness and amount. '''

        msg = self.jobs[self.job_counter]

        ThreadedMailManager(parent=self, gv=gv).startMailWorker(
                sender_name=self.temp_sender_name,
                mail_type='UNCLEAR',
                mail_item=msg,
                move_mail_to_verwerkt=True,
                sender_mail_adress=self.mail_manager.getEmailAddress(msg),
                sender_mail_receive_time=self.mail_manager.getSenderMailReceiveTime(msg))

        self.skipJob()

    def createJob(self):
        """ Create a laser job. """
        msg = self.jobs[self.job_counter]
        sender_mail_adress = self.mail_manager.getEmailAddress(msg)
        sender_mail_receive_time = self.mail_manager.getSenderMailReceiveTime(msg)

        self.job_tracker.addJob(self.temp_job_name,
                                self.temp_sender_name,
                                self.temp_job_folder_global_path,
                                self.temp_make_files_dict,
                                sender_mail_adress=sender_mail_adress,
                                sender_mail_receive_time=sender_mail_receive_time)

        if not os.path.exists(self.temp_job_folder_global_path):
            os.mkdir(self.temp_job_folder_global_path)

        self.mail_manager.saveMail(msg, self.temp_job_folder_global_path)

        # save the attachments
        for attachment_dict in self.temp_store_files_dict.values():
            self.mail_manager.saveAttachment(attachment_dict['attachment'], attachment_dict['file_global_path'])

        ThreadedMailManager(parent=self, gv=gv).startMailWorker(
                sender_name=self.temp_sender_name,
                mail_type='RECEIVED',
                mail_item=msg,
                move_mail_to_verwerkt=True,
                template_content= {"{jobs_in_queue}": self.job_tracker.getNumberOfJobsInQueue()},
                sender_mail_adress=sender_mail_adress,
                sender_mail_receive_time=sender_mail_receive_time)

        TimedMessage(gv, self, text=f'Laser job {self.temp_job_name} created')


    def loadAttachmentContent(self):
        ''' Load content of attachment into dialog. '''

        attachment = self.temp_make_items[self.make_item_counter]
        attachment_name = self.mail_manager.getAttachmentFileName(attachment)

        if attachment_name.lower().endswith(gv['ACCEPTED_EXTENSIONS']):
            self.attachmentProgressQLabel.setText(f'Attachment ({self.make_item_counter+1}/{len(self.temp_make_items)})')
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
            self.temp_minor_files_dict[attachment_name] = {'attachment': attachment,
                                                     'file_global_path': file_global_path}
            self.make_item_counter += 1
            self.loadContent()


class CreateLaserJobsFromFileSystemQDialog(CreateJobsFromFileSystemQDialog):
    ''' Ask for file laser file details (material, thickness, amount) and create laser jobs.
    job_name: List with job names
    files_global_paths_list: nested lists with global paths for every file in the job.
    '''

    def __init__(self, parent, job_name_list: list, files_global_paths_list: list, *args, **kwargs):

        super().__init__(parent,
                         gv,
                         os.path.join(gv['LOCAL_UI_DIR'], 'enter_job_details_dialog.ui'),
                         LaserJobTracker(self),
                         job_name_list,
                         files_global_paths_list,
                         *args, **kwargs)



        self.new_material_text = 'New Material'
        self.new_materials_list = []

        self.materialQComboBox.currentIndexChanged.connect(self.onMaterialComboboxChanged)
        self.skipPushButton.clicked.connect(self.skipJob)
        self.buttonBox.accepted.connect(self.collectFileInfo)
        self.loadJobContent()


    def loadItemContent(self):
        ''' Load content local file into dialog. '''

        file_global_path = self.temp_make_items[self.make_item_counter]
        file_name = os.path.basename(file_global_path)

        if file_name.lower().endswith(gv['ACCEPTED_EXTENSIONS']):
            self.fileProgressQLabel.setText(f'File({self.make_item_counter+1}/{len(self.jobs)})')
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
            self.temp_store_files_dict[file_name] = {'source_file_global_path': file_global_path,
                                             'target_file_global_path': self.temp_make_items[self.make_item_counter]}

            if self.make_item_counter+1 >= len(self.jobs):
                self.createLaserJob()
                self.job_counter += 1

                if self.job_counter >= len(self.jobs):
                    self.loadJobContent()
            else:
                self.loadItemContent()


    def createJob(self):
        """ Create a laser job. """

        self.job_tracker.addJob(self.temp_job_name,
                                'no sender name',
                                self.temp_job_folder_global_path,
                                self.temp_make_files_dict)

        if not os.path.exists(self.temp_job_folder_global_path):
            os.mkdir(self.temp_job_folder_global_path)

        for item_dict in self.temp_store_files_dict.values():
            copy_item(item_dict['source_file_global_path'], item_dict['target_file_global_path'])

        TimedMessage(gv, self, text=f'Laser job {self.temp_job_name} created')



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

        if not validate_material_info(self, material, thickness, amount):
            return

        source_file_global_path = self.temp_make_items[self.make_item_counter]

        original_file_name = os.path.basename(source_file_global_path)
        if material in original_file_name and\
            thickness in original_file_name and\
            amount in original_file_name:
            file_name = original_file_name
        else:
            file_name = material+'_'+thickness+'mm_'+amount+'x_'+original_file_name

        target_file_global_path = os.path.join(self.temp_job_folder_global_path, file_name)

        self.temp_make_files_dict[self.temp_job_name + '_' + file_name] = {
                            'file_name': file_name,
                            'file_global_path': target_file_global_path,
                            'material': material,
                            'thickness': thickness,
                            'amount': amount,
                            'done': False}

        self.temp_store_files_dict[file_name] = {'source_file_global_path': source_file_global_path,
                                             'target_file_global_path': target_file_global_path}
        self.make_item_counter += 1
        self.loadContent()

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
