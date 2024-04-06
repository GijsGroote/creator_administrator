import os
import json
import subprocess
from functools import partial


from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QWidget, QVBoxLayout, QLabel
from PyQt6.uic import loadUi

from src.directory_functions import shorten_folder_name
from src.settings_dialog import SettingsQDialog
from src.qmessagebox import WarningQMessageBox
from src.qdialog import SelectOptionsQDialog
from src.validate import (
        check_empty,
        check_is_executable,
        check_comma_seperated_tuple)

from global_variables import gv

class PrintSettingsQDialog(SettingsQDialog):

    def __init__(self, parent, *args, **kwargs):
        ui_global_path = os.path.join(gv['LOCAL_UI_DIR'], 'settings_dialog.ui')
        super().__init__(parent, ui_global_path, gv, *args, **kwargs)

        self.special_printers_dicts = gv['SPECIAL_PRINTERS']
        self.refreshSpecialPrinterScrollArea()

        self.addPrinterPushButton.clicked.connect(self.addPrinter)
        self.removePrinterPushButton.clicked.connect(self.removePrinter)

        self.defaultPrinterNameLineEdit.setText(str(gv['DEFAULT_PRINTER_NAME']))
        self.defaultPrinterNameLineEdit.textChanged.connect(
                partial(check_empty, self.defaultPrinterNameLineEdit, gv))

        self.defaultAcceptedMaterialsLineEdit.textChanged.connect(
                partial(check_comma_seperated_tuple, self.defaultAcceptedMaterialsLineEdit, gv))


    def saveMachineSettings(self):
        ''' Save the machine specific settings. '''

        with open(gv['SETTINGS_FILE_PATH'], 'r') as settings_file:
            settings_dict = json.load(settings_file)

            settings_dict['DEFAULT_PRINTER_NAME'] = self.defaultPrinterNameLineEdit.text()
            settings_dict['SPECIAL_PRINTERS'] = self.special_printers_dicts

        with open(gv['SETTINGS_FILE_PATH'], 'w' ) as settings_file:
            json.dump(settings_dict, settings_file, indent=4)

    def validateMachineSettings(self) -> bool:
        ''' Validate the machine specific settings. '''

        check_and_warnings = [(check_empty(self.defaultPrinterNameLineEdit, gv), 'Printer Name cannot be empty')]

        # check input values
        for check, warning_string in check_and_warnings:
            if not check:
                WarningQMessageBox(self, gv, warning_string)
                return False
        return True

    def restartApp(self):
        ''' Restart the application. '''
        subprocess.call("python " + '"'+
            f'{os.path.join(gv["REPO_DIR_HOME"], "printer/src/printer_app.py")}'
                        +'"', shell=True)

    def addPrinter(self):
        ''' Add a new special printer. '''
        add_printer_dialog = AddPrinterQDialog(self)
        add_printer_dialog.exec()
        if add_printer_dialog.add_printer_dict is not None:
            printer_name = add_printer_dialog.add_printer_dict['printer_name']
            if printer_name in self.special_printers_dicts:
                WarningQMessageBox(self, gv, f'A printer with name {printer_name} already exists')
                return

            self.special_printers_dicts[printer_name] = add_printer_dialog.add_printer_dict
            self.refreshSpecialPrinterScrollArea()

    def removePrinter(self):
        ''' Remove a special printer. '''

        printer_list = [(key+': '+value['printer_name'], key) for key, value in self.special_printers_dicts.items()]
        dialog = SelectOptionsQDialog(self, gv, printer_list, question='Select printers to remove')

        if dialog.exec() == 1:
            remove_printer_keys = [item.data(1) for item in dialog.optionsQListWidget.selectedItems()]
            [self.special_printers_dicts.pop(remove_key) for remove_key in remove_printer_keys]

        self.refreshSpecialPrinterScrollArea()

    def refreshSpecialPrinterScrollArea(self):
        ''' Refresh property widget. '''

        content_widget = QWidget()
        scroll_layout = QVBoxLayout(content_widget)


        for printer_key, printer_value in self.special_printers_dicts.items():

            slicer_global_path = 'System Default'
            if 'slicer_executable_global_path' in printer_value:
                slicer_global_path = shorten_folder_name(printer_value['slicer_executable_global_path'], 45)

            printer_str = f'<big><big>{printer_value["printer_name"]}<hr>'\
                    f'<br>&nbsp;&nbsp;&nbsp;&nbsp; Printer Name: {printer_key}'\
                    f'<br>&nbsp;&nbsp;&nbsp;&nbsp; Slicer: {slicer_global_path}'\
                    f'<br>&nbsp;&nbsp;&nbsp;&nbsp; Accepted Materials:&nbsp;&nbsp;'\
                    f'{printer_value["ACCEPTED_MATERIALS"]}</big></big>'

            for property_name, property_dict in printer_value['properties'].items():

                printer_str += f'<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<big><big>{property_name}</big></big>'\
                        f'<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'\
                        f'</big></big> Data Type:<big><big> {property_dict["data_type"]}</big></big>'

                if 'custom_list_of_strings' in property_dict:
                    printer_str += f'<big><big> = {property_dict["custom_list_of_strings"]}</big></big>'
                printer_str += '<br>'

            scroll_layout.addWidget(QLabel(printer_str+'<br>', self))

        scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scrollArea.setWidget(content_widget)

class AddPrinterQDialog(QDialog):
    ''' Add a new special printer dialog. '''

    def __init__(self, parent: QWidget, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.add_printer_dict = None
        self.properties = {}

        loadUi(os.path.join(gv['LOCAL_UI_DIR'], 'add_printer_dialog.ui'), self)

        self.custom_list_of_strings = 'Custom List of Strings'
        self.buttonBox.accepted.connect(self.applySettings)
        self.addPropertyButton.clicked.connect(self.applyNewProperty)

        self.customListLineEdit.setHidden(True)
        self.customListLabel.setHidden(True)
        self.dataTypeQComboBox.currentIndexChanged.connect(self.onDataTypeQComboBoxChanged)



        self.printerNameLineEdit.textChanged.connect(partial(check_empty, self.printerNameLineEdit, gv))
 

        self.acceptedMaterialsLineEdit.textChanged.connect(
                partial(check_comma_seperated_tuple, self.acceptedMaterialsLineEdit, gv))

        self.newPropertyNameLineEdit.textChanged.connect(partial(check_empty, self.newPropertyNameLineEdit, gv))

        self.customListLineEdit.textChanged.connect(partial(check_comma_seperated_tuple, self.customListLineEdit, gv))

        # TODO: add the default value, check it when data type selection changed
        # self.propertyDefaultValueLineEdit.textChanged(


    def applyNewProperty(self):
        ''' Validate and add new property. '''

        check_and_warnings = [(check_empty(self.newPropertyNameLineEdit, gv), 'New Property Name cannot be emtpy')]

        if self.dataTypeQComboBox.currentText() == self.custom_list_of_strings:
            check_and_warnings.append((check_comma_seperated_tuple(self.customListLineEdit, gv), f'{self.custom_list_of_strings} is not a comma seperated list of strings'))

        # check input values
        for check, warning_string in check_and_warnings:
            if not check:
                WarningQMessageBox(self, gv, warning_string)
                return

        self.addProperty()

    def applySettings(self):
        ''' Validate and save settings. '''
        if self.validateNewPrinterSettings():
            self.add_printer_dict = {'printer_name': self.printerNameLineEdit.text(),
                'ACCEPTED_EXTENSIONS': self.acceptedExtensionsLineEdit.text(),
                'SLICER_EXECUTABLE_PATH': self.slicerExecutablePushButton.text(),
                'properties': self.properties}
            self.close()
        
    def validateNewPrinterSettings(self) -> bool:
        ''' Validate general (not machine specific) settings. '''

        check_and_warnings = [
            (check_empty(self.printerNameLineEdit, gv), 'Printer Name cannot be empty'),
            (check_comma_seperated_tuple(self.acceptedMaterialsLineEdit, gv), 'Accepted Materials is not a comma seperated list of values'),
            (check_is_executable(self.slicerExecutablePushButton, gv), f'Select an Executable, .exe file, not {self.slicerExecutableButton.file_global_path}'),
         ]

        # check input values
        for check, warning_string in check_and_warnings:
            if not check:
                WarningQMessageBox(self, gv, warning_string)
                return False
        return True

    def addProperty(self):
        ''' Add property to widget. '''
        property_key = 'property_'+str(len(self.properties)+1)

        self.properties[property_key] = {'property_name': self.newPropertyNameLineEdit.text(),
                                         'data_type': self.dataTypeQComboBox.currentText()}

        if self.dataTypeQComboBox.currentText() == self.custom_list_of_strings:
            self.properties[property_key]['custom_list_of_strings'] = self.customListLineEdit.text()

        self.newPropertyNameLineEdit.clear()
        self.newPropertyNameLineEdit.setStyleSheet("") 
        self.customListLineEdit.clear()
        self.customListLineEdit.setStyleSheet("") 

        self.refreshPropetyScrollArea()

    def refreshPropetyScrollArea(self):
        ''' Refresh property widget. '''

        content_widget = QWidget()
        scroll_layout = QVBoxLayout(content_widget)

        for property_key, property_dict in self.properties.items():

            property_str = f'{property_key.replace("_", " ").capitalize()}: <big><big>{property_dict["property_name"]}</big></big><hr>'\
                    f'<br>&nbsp;&nbsp;&nbsp;&nbsp;Data Type:<big><big> {property_dict["data_type"]}</big></big>'

            if 'custom_list_of_strings' in property_dict:
                property_str += f' = <big><big>{property_dict["custom_list_of_strings"]}</big></big>'

            scroll_layout.addWidget(QLabel(property_str+'<br>', self))


        scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scrollArea.setWidget(content_widget)

    def onDataTypeQComboBoxChanged(self):
        ''' Show/hide custom list option. '''
        if self.dataTypeQComboBox.currentText() == self.custom_list_of_strings:
            self.customListLineEdit.setHidden(False)
            self.customListLabel.setHidden(False)
        else:
            self.customListLineEdit.setHidden(True)
            self.customListLabel.setHidden(True)
