import os
import re

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QSizePolicy, QFormLayout


from src.qdialog import CreateJobsFromMailQDialog, CreateJobsFromFileSystemQDialog, SearchJobDialog
from src.qmessagebox import TimedMessage
from src.threaded_mail_manager import ThreadedMailManager
from src.validate import check_property 

from printer_job_tracker import PrintJobTracker
from printer_validate import validate_material_info, validate_print_properties


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

        self.requested_item_parameters_dict = {} 
        self.printer_properties = {}
        self.form_layout = None


        self.printerComboBox.addItem(gv['DEFAULT_PRINTER_NAME'])
        for printer_dict in gv['SPECIAL_PRINTERS'].values():
            self.printerComboBox.addItem(printer_dict['PRINTER_NAME'])

        self.printerComboBox.currentIndexChanged.connect(self.onPrinterComboBoxChanged)
        self.loadJobContent()


    def loadItemContent(self):
        ''' Load content of attachment into dialog. '''

        attachment = self.temp_make_items[self.make_item_counter]
        attachment_name = self.mail_manager.getAttachmentFileName(attachment)

        self.attachmentProgressQLabel.setText(f'Attachment ({self.make_item_counter+1}/{len(self.temp_make_items)})')
        self.attachmentNameQLabel.setText(attachment_name)


        if self.requested_parameters_dict is not None and\
                attachment_name in self.requested_parameters_dict and\
                'printer_name' in self.requested_parameters_dict[attachment_name]:

            self.requested_item_parameters_dict = self.requested_parameters_dict[attachment_name]
        
            self.printerComboBox.setCurrentIndex(self.printerComboBox.findText(
                self.requested_parameters_dict[attachment_name]['printer_name']))

        else:
            self.requested_item_parameters_dict = None
            self.printerComboBox.setCurrentIndex(self.printerComboBox.findText(gv['DEFAULT_PRINTER_NAME']))

        # create print property fields
        self.makePrinterPropertyFieldsForItem()
        self.makeSpecialPrinterPropertyFieldsForItem()

        # guess what should be in the property fields
        self.guessPropertyFieldsForItem()
        self.guessSpecialPropertyFieldsForItem()


    def makePrinterPropertyFieldsForItem(self):
        ''' Load material into material propery field. '''

        self.materialQComboBox.clear()
        self.newMaterialQLineEdit.clear()
        self.amountQLineEdit.clear()

        # initially hide option for new material
        self.newMaterialQLabel.setHidden(True)
        self.newMaterialQLineEdit.setHidden(True)

        materials = list(set(gv['ACCEPTED_MATERIALS']).union(\
                self.job_tracker.getExistingMaterials()).union(self.new_materials_list))
        self.materialQComboBox.addItems(materials)
        self.materialQComboBox.addItem(self.new_material_text)

    def makeSpecialPrinterPropertyFieldsForItem(self):
        ''' Make the labels and text input widgets for the special printer currently selected. '''

        if self.requested_item_parameters_dict is None:
            return

        # clear and clean everything
        self.materialQComboBox.clear()
        self.printer_properties = {}

        if self.form_layout is not None:
            # It could be that this loop needs some deleteLater
            while self.form_layout.rowCount() > 0:
                self.form_layout.removeRow(0)
            self.form_layout.update()

        self.form_layout = QFormLayout()
        self.form_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft)

        # Make the widgets
        content_widget = QWidget()
        selected_printer = self.printerComboBox.currentText()

        materials = list(set(gv['SPECIAL_PRINTERS'][selected_printer]['ACCEPTED_MATERIALS']).union(
            self.job_tracker.getExistingMaterials()).union(self.new_materials_list))

        self.materialQComboBox.addItems(materials)
        self.materialQComboBox.addItem(self.new_material_text)

        # make all label and line edits that belong to the requested printer
        for property_key, property_dict in gv['SPECIAL_PRINTERS'][selected_printer]['PROPERTIES'].items():
            label = QLabel(property_dict['PROPERTY_NAME'])
            qline_edit = QLineEdit()

            self.printer_properties[property_dict['PROPERTY_NAME']] = {'qline_edit_widget': qline_edit, 
               'data_type': gv['SPECIAL_PRINTERS'][selected_printer]['PROPERTIES'][property_key]['DATA_TYPE']}

            self.form_layout.addRow(label, qline_edit)

        content_widget.setLayout(self.form_layout)
        self.printPropertyScrollArea.setWidget(content_widget)

        # adjust height of scoll area
        self.printPropertyScrollArea.setMinimumHeight(content_widget.sizeHint().height())

    def guessPropertyFieldsForItem(self):
        ''' Load/guess what printer parameters from file name. '''
        attachment_name = self.attachmentNameQLabel.text().lower()

        # guess the material
        for n_material in range(self.materialQComboBox.count()):
            material = self.materialQComboBox.itemText(n_material)

            if material.lower() in attachment_name:
                self.materialQComboBox.setCurrentIndex(self.materialQComboBox.findText(material))

        # guess the amount
        match = re.search(r"\d+\.?\d*(?=x_)", attachment_name)
        if match:
            self.amountQLineEdit.setText(match.group())
        else:
            self.amountQLineEdit.setText('1')



    def guessSpecialPropertyFieldsForItem(self):
        ''' Load the requested parameters. '''

        if self.requested_item_parameters_dict is None:
            return

        if 'amount' in self.requested_item_parameters_dict:
            try:
                amount_int = int(self.requested_item_parameters_dict['amount'])
                self.amountQLineEdit.setText(amount_int)

            except ValueError:
                pass

        # Load requested parameters into the text widgets
        for property_key, property_dict in gv['SPECIAL_PRINTERS'][self.
                          requested_item_parameters_dict['printer_name']]['PROPERTIES'].items():

            if property_dict['PROPERTY_NAME'] in self.requested_item_parameters_dict:
                requested_text = self.requested_item_parameters_dict[property_dict['PROPERTY_NAME']]
                self.printer_properties[property_dict['PROPERTY_NAME']]['qline_edit_widget'].setText(requested_text)

            else:
                self.printer_properties[property_dict['PROPERTY_NAME']]['qline_edit_widget'].setText(
                    gv['SPECIAL_PRINTERS'][self.requested_item_parameters_dict['printer_name']]\
                    ['PROPERTIES'][property_key]['DEFAULT_VALUE'])


            if 'material' in self.requested_item_parameters_dict:
                if self.requested_item_parameters_dict['material'].lower() in self.materialQComboBox:
                    self.materialQComboBox.setCurrentIndex(self.materialQComboBox.findText(self.requested_item_parameters_dict['material']))
                else:

                    self.materialQComboBox.setCurrentIndex(self.materialQComboBox.findText(self.new_material_text))
                    self.newMaterialQLineEdit.setText(self.requested_item_parameters_dict['material'])


    def onPrinterComboBoxChanged(self):
        ''' Add the printer properties to the comboBox. '''

        if self.printerComboBox.currentText() in gv['SPECIAL_PRINTERS']:
            self.printPropertyScrollArea.setHidden(False)

        self.printPropertyScrollArea.setHidden(True)



    def collectItemInfo(self):
        ''' Collect material amount info. '''
        material = self.materialQComboBox.currentText()
        if material == self.new_material_text:
            material = self.newMaterialQLineEdit.text()
            self.new_materials_list.append(material)

        amount = self.amountQLineEdit.text()

        if not validate_material_info(self, material, amount):
            return

        if not validate_print_properties(self, self.printer_properties):
            return

        attachment = self.temp_make_items[self.make_item_counter]
        original_file_name = self.mail_manager.getAttachmentFileName(attachment)

        attachment = self.temp_make_items[self.make_item_counter]
        original_file_name = self.mail_manager.getAttachmentFileName(attachment)

        file_name_prefix = ''

        # TODO: this might be usefull later
        # if material not in original_file_name:
        #     file_name_prefix += material+'_'
        
        if amount+'x_' not in original_file_name:
            file_name_prefix += str(amount)+'x_'
        
        file_name = file_name_prefix + original_file_name

        file_global_path = os.path.join(self.temp_job_folder_global_path, file_name)

        file_dict = {
            'file_name': file_name,
            'file_global_path': file_global_path,
            'printer_name': self.printerComboBox.currentText(),
            'material': material,
            'amount': amount,
            'done': False}

        for property_key, property_dict in self.printer_properties.items():
            file_dict[property_key] = property_dict['qline_edit_widget'].text()

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
                template_content= {"{jobs_in_queue}": self.job_tracker.getNumberOfJobsWithStatus(['WACHTRIJ', 'GESLICED'])},
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

