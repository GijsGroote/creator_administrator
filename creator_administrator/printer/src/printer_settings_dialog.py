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
        check_comma_seperated_tuple,
        check_property)

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

        if 'DEFAULT_SLICER_EXECUTABLE_PATH' in gv:
            self.defaultSlicerExecutablePushButton.setText(
                shorten_folder_name(str(gv['DEFAULT_SLICER_EXECUTABLE_PATH'])))
            self.defaultSlicerExecutablePushButton.file_global_path = gv['DEFAULT_SLICER_EXECUTABLE_PATH']
        else:
            self.defaultSlicerExecutablePushButton.setText('System Default')

        self.defaultSlicerExecutablePushButton.clicked.connect(
                partial(check_is_executable, self.defaultSlicerExecutablePushButton, gv))


        self.defaultAcceptedMaterialsLineEdit.textChanged.connect(
                partial(check_comma_seperated_tuple, self.defaultAcceptedMaterialsLineEdit, gv))


    def saveMachineSettings(self):
        ''' Save the machine specific settings. '''

        with open(gv['SETTINGS_FILE_PATH'], 'r') as settings_file:
            settings_dict = json.load(settings_file)

            settings_dict['DEFAULT_PRINTER_NAME'] = self.defaultPrinterNameLineEdit.text()
            settings_dict['DEFAULT_SLICER_EXECUTABLE_PATH'] = self.defaultSlicerExecutablePushButton.text()
            settings_dict['SPECIAL_PRINTERS'] = self.special_printers_dicts

        with open(gv['SETTINGS_FILE_PATH'], 'w' ) as settings_file:
            json.dump(settings_dict, settings_file, indent=4)

    def validateMachineSettings(self) -> bool:
        ''' Validate the machine specific settings. '''

        check_and_warnings = [(check_empty(self.defaultPrinterNameLineEdit, gv), 'Printer Name cannot be empty'),
                              (self.defaultSlicerExecutablePushButton.text() == 'System Default' or\
                                  check_is_executable(self.defaultSlicerExecutablePushButton, gv),\
                               f'Slicer executable {self.defaultSlicerExecutablePushButton.file_global_path} is not an executable')]

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
            printer_name = add_printer_dialog.add_printer_dict['PRINTER_NAME']
            if printer_name in self.special_printers_dicts:
                WarningQMessageBox(self, gv, f'A printer with name {printer_name} already exists')
                return

            self.special_printers_dicts[printer_name] = add_printer_dialog.add_printer_dict
            self.refreshSpecialPrinterScrollArea()

    def removePrinter(self):
        ''' Remove a special printer. '''

        printer_list = [(key+': '+value['PRINTER_NAME'], key) for key, value in self.special_printers_dicts.items()]
        dialog = SelectOptionsQDialog(self, gv, printer_list, question='Select printers to remove')

        if dialog.exec() == 1:
            remove_printer_keys = [item.data(1) for item in dialog.optionsQListWidget.selectedItems()]
            [self.special_printers_dicts.pop(remove_key) for remove_key in remove_printer_keys]

        self.refreshSpecialPrinterScrollArea()

    def refreshSpecialPrinterScrollArea(self):
        ''' Refresh property widget. '''

        content_widget = QWidget()
        scroll_layout = QVBoxLayout(content_widget)

        space = '&nbsp;'*5


        for printer_key, printer_value in self.special_printers_dicts.items():

            slicer_executable_path = 'System Default'
            if 'SLICER_EXECUTABLE_PATH' in printer_value:
                slicer_executable_path = shorten_folder_name(printer_value['SLICER_EXECUTABLE_PATH'])

            printer_str = f'<big><big>{printer_value["PRINTER_NAME"]}<hr>'\
                    f'<br>{space} Printer Name: {space}{printer_key}'\
                    f'<br>{space} Slicer Executable: {space}{slicer_executable_path}'\
                    f'<br>{space} Accepted Materials: {space}{printer_value["ACCEPTED_MATERIALS"]}'\
                    f'<br>{space} Properties:</big></big><br>' 

            for property_name, property_dict in printer_value['PROPERTIES'].items():

                printer_str += f''\
                        f'<big><big><br>{space*2}Property Name: {space}{property_name}{space*2}<br>{space*2}Data Type: {space}{property_dict["DATA_TYPE"]}'\
                        f'<br>{space*2}Default Value: {space}{property_dict["DEFAULT_VALUE"]}<br></big></big>'\

            scroll_layout.addWidget(QLabel(printer_str, self))

        scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scrollArea.setWidget(content_widget)

class AddPrinterQDialog(QDialog):
    ''' Add a new special printer dialog. '''

    def __init__(self, parent: QWidget, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.add_printer_dict = None
        self.properties = {}

        loadUi(os.path.join(gv['LOCAL_UI_DIR'], 'add_printer_dialog.ui'), self)

        self.printerNameLineEdit.textChanged.connect(partial(check_empty, self.printerNameLineEdit, gv))
        self.acceptedMaterialsLineEdit.textChanged.connect(
                partial(check_comma_seperated_tuple, self.acceptedMaterialsLineEdit, gv))
        self.slicerExecutablePushButton.clicked.connect(partial(check_is_executable, self.slicerExecutablePushButton, gv))

        self.buttonBox.accepted.connect(self.applySettings)
        self.addPropertyButton.clicked.connect(self.applyNewProperty)

        # property related widgets
        self.newPropertyNameLineEdit.textChanged.connect(partial(check_empty, self.newPropertyNameLineEdit, gv))
        self.dataTypeQComboBox.currentIndexChanged.connect(self.checkDefaultPropertyValue)
        self.propertyDefaultValueLineEdit.textChanged.connect(self.checkDefaultPropertyValue)

    def applyNewProperty(self):
        ''' Validate and add new property. '''

        check_and_warnings = [(check_empty(self.newPropertyNameLineEdit, gv), 'New Property Name cannot be emtpy'),
                          (check_property(self.propertyDefaultValueLineEdit, self.dataTypeQComboBox.currentText(), gv), 'Default value is not valid')]

        # check input values
        for check, warning_string in check_and_warnings:
            if not check:
                WarningQMessageBox(self, gv, warning_string)
                return

        self.addProperty()

    def applySettings(self):
        ''' Validate and save settings. '''
        if self.validateNewPrinterSettings():
            self.add_printer_dict = {'PRINTER_NAME': self.printerNameLineEdit.text(),
                'ACCEPTED_MATERIALS': self.acceptedMaterialsLineEdit.text(),
                'SLICER_EXECUTABLE_PATH': self.slicerExecutablePushButton.text(),
                'PROPERTIES': self.properties}
            self.close()
        
    def validateNewPrinterSettings(self) -> bool:
        ''' Validate general (not machine specific) settings. '''

        check_and_warnings = [
            (check_empty(self.printerNameLineEdit, gv),
                 'Printer Name cannot be empty'),
            (check_comma_seperated_tuple(self.acceptedMaterialsLineEdit, gv),
                 'Accepted Materials is not a comma seperated list of values'),
            (check_is_executable(self.slicerExecutablePushButton, gv),
                 f'Slicer Executable is {self.slicerExecutablePushButton.text()}, select a .exe file')]

        # check input values
        for check, warning_string in check_and_warnings:
            if not check:
                WarningQMessageBox(self, gv, warning_string)
                return False
        return True

    def addProperty(self):
        ''' Add property to widget. '''
        property_key = 'PROPERTY_'+str(len(self.properties)+1)

        self.properties[property_key] = {'PROPERTY_NAME': self.newPropertyNameLineEdit.text(),
                                         'DATA_TYPE': self.dataTypeQComboBox.currentText(),
                                         'DEFAULT_VALUE': self.propertyDefaultValueLineEdit.text()}

        for widget in (self.newPropertyNameLineEdit, self.propertyDefaultValueLineEdit):
            widget.clear()
            widget.setStyleSheet("") 

        self.refreshPropetyScrollArea()

    def refreshPropetyScrollArea(self):
        ''' Refresh property widget. '''

        content_widget = QWidget()
        scroll_layout = QVBoxLayout(content_widget)
        space = '&nbsp;'*5

        for property_key, property_dict in self.properties.items():

            property_str = f'<big><big>{property_key.replace("_", " ").capitalize()}: {property_dict["PROPERTY_NAME"]}<hr>'\
                    f'<br>{space}Data Type: {space}{property_dict["DATA_TYPE"]}'\
                    f'<br>{space}Default Value: {space}{property_dict["DEFAULT_VALUE"]}</big></big>'

            scroll_layout.addWidget(QLabel(property_str+'<br>', self))


        scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scrollArea.setWidget(content_widget)

    def checkDefaultPropertyValue(self):
        ''' Check if the default property value is a valid input. '''

        check_property(self.propertyDefaultValueLineEdit,
                      self.dataTypeQComboBox.currentText(), gv)
