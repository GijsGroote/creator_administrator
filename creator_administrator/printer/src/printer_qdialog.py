import os
import re


from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QSizePolicy, QFormLayout


from src.qdialog import CreateJobsFromMailQDialog, CreateJobsFromFileSystemQDialog, SearchJobDialog
from src.qmessagebox import TimedMessage
from src.threaded_mail_manager import ThreadedMailManager
from src.validate import validate_properties

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


        self.printPropertyScrollArea.setHidden(True)
        self.printPropertyScrollArea.setWidgetResizable(True)

        self.requested_item_parameters_dict = None
        self.printer_properties = None

        self.printerComboBox.addItem(gv['DEFAULT_PRINTER_NAME'])
        for printer_dict in gv['SPECIAL_PRINTERS'].values():
            print(f"add the tingy {printer_dict['printer_name']}")
            self.printerComboBox.addItem(printer_dict['printer_name'])

        self.printerComboBox.currentIndexChanged.connect(self.onPrinterComboBoxChanged)
        self.loadJobContent()

    def onPrinterComboBoxChanged(self):
        ''' Add the printer properties to the comboBox. '''
        print(f'fuckingfuckfuicxkf{self.printerComboBox.currentText()}')

        content_widget = QWidget()
        vertical_layout = QVBoxLayout(content_widget)
        self.printer_properties = {}
        form_layout = QFormLayout()
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft)

        selected_printer = self.printerComboBox.currentText()

        # TODO: find why this is needed, an emtpy printer should not be added to start with
        if selected_printer == '':
            return

        # make all label and line edits that belong to the requested printer
        for property_name, property_dict in gv['SPECIAL_PRINTERS'][selected_printer]['properties'].items():
            label = QLabel(property_name)
            qline_edit = QLineEdit()

            print(gv['SPECIAL_PRINTERS'][selected_printer]['properties'])

            self.printer_properties[property_name] = {'qline_edit_widget': qline_edit, 
               'data_type': gv['SPECIAL_PRINTERS'][selected_printer]['properties'][property_name]['data_type']}
            form_layout.addRow(label, qline_edit)
            vertical_layout.addLayout(form_layout)

        content_widget.setLayout(vertical_layout)
        self.printPropertyScrollArea.setWidget(content_widget)

        # adjust height of scoll area
        self.printPropertyScrollArea.setMinimumHeight(content_widget.sizeHint().height())

    def loadItemContent(self):
        ''' Load content of attachment into dialog. '''

        attachment = self.temp_make_items[self.make_item_counter]
        attachment_name = self.mail_manager.getAttachmentFileName(attachment)

        # load requested parameters
        if self.requested_parameters_dict is not None and\
                attachment_name in self.requested_parameters_dict and\
                'printer_name' in self.requested_parameters_dict[attachment_name]:

            self.printerComboBox.setCurrentIndex(self.printerComboBox.findText(
                self.requested_parameters_dict[attachment_name]['printer_name']))

            self.requested_item_parameters_dict = self.requested_parameters_dict[attachment_name]
            self.loadRequestedParametersforAttachment()

        else:
            self.printPropertyScrollArea.setHidden(True)
            self.requested_item_parameters_dict = None


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

        # guess the material
        for material in materials:
            if material.lower() in attachment_name.lower():
                self.materialQComboBox.setCurrentIndex(self.materialQComboBox.findText(material))

        # guess the amount
        match = re.search(r"\d+\.?\d*(?=x_)", attachment_name.lower())
        if match:
            self.amountQLineEdit.setText(match.group())
        else:
            self.amountQLineEdit.setText('1')


    def loadRequestedParametersforAttachment(self):
        ''' Load the requested parameters. '''

        self.printPropertyScrollArea.setHidden(False)

        if 'material' in self.requested_item_parameters_dict:
            if self.requested_item_parameters_dict['material'].lower() in self.materialQComboBox:
                self.materialQComboBox.setCurrentIndex(self.materialQComboBox.findText(self.requested_item_parameters_dict['material']))
            else:
                self.materialQComboBox.setCurrentIndex(self.materialQComboBox.findText(self.new_material_text))
                self.newMaterialQLineEdit.setHidden(False)
                self.newMaterialQLineEdit.setText(self.requested_item_parameters_dict['material'])

        if 'amount' in self.requested_item_parameters_dict:
            try:
                amount_int = int(self.requested_item_parameters_dict['amount'])
                self.amountQLineEdit.setText(amount_int)

            except ValueError:
                pass


        for property_name, property_dict in gv['SPECIAL_PRINTERS'][self.requested_item_parameters_dict['printer_name']]['properties'].items():

            if property_name in self.requested_item_parameters_dict:
                requested_text = self.requested_item_parameters_dict[property_name]
                self.printer_properties[property_name]['qline_edit_widget'].setText(requested_text)

            else:
                print(f"The requested parametr {property_name} is not in the requested parametres, implement going to the default value.")



    def collectItemInfo(self):
        ''' Collect material amount info. '''
        material = self.materialQComboBox.currentText()
        if material == self.new_material_text:
            material = self.newMaterialQLineEdit.text()
            self.new_materials_list.append(material)

        amount = self.amountQLineEdit.text()

        if not validate_material_info(self, material, amount):
            return

        
        if self.printer_properties is not None and not validate_properties(self, self.printer_properties):
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

        file_dict = {
            'file_name': file_name,
            'file_global_path': file_global_path,
            'printer_name': self.printerComboBox.currentText(),
            'material': material,
            'amount': amount,
            'done': False}

        if self.printer_properties is not None:
            for property_name, property_dict in self.printer_properties.items():
                file_dict[property_name] = property_dict['qline_edit_widget'].text()

        self.temp_make_files_dict[self.temp_job_name + '_' + file_name] = file_dict



        self.temp_store_files_dict[file_name] = {'attachment': attachment,
                                                 'target_file_global_path': file_global_path}
        self.make_item_counter += 1
        self.loadContent()

    def createJob(self):
        ''' Create a print job. '''

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
                template_content= {"{jobs_in_queue}": self.job_tracker.getNumberOfJobsWithStatus(['WACHTRIJ'])},
                sender_mail_adress=sender_mail_adress,
                sender_mail_receive_time=sender_mail_receive_time)

        TimedMessage(self, gv, f'Created Job: {self.temp_job_name}')


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
        match = re.search(r"\d+\.?\d*(?=x_)", file_name.lower())
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

class PrintSearchJobDialog(SearchJobDialog):
    ''' Search all existing jobs in a dialog. '''
    def __init__(self, parent: QWidget, *args, **kwargs):
        ui_global_path = os.path.join(gv['LOCAL_UI_DIR'], 'search_job_dialog.ui')
        super().__init__(parent, ui_global_path, *args, **kwargs)

