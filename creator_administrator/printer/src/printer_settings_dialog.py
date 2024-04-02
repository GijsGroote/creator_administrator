import os
import json
import abc
import subprocess
from functools import partial


from PyQt6.QtWidgets import QDialog, QWidget
from PyQt6.uic import loadUi

from src.settings_dialog import SettingsQDialog
from src.qmessagebox import WarningQMessageBox
from src.validate import (
        check_int,
        check_extensions_tuple,
        check_comma_seperated_tuple,
        check_html,
        check_is_directory)

from global_variables import gv

class PrintSettingsQDialog(SettingsQDialog):

    def __init__(self, parent, gv: dict, *args, **kwargs):
        ui_global_path = os.path.join(gv['LOCAL_UI_DIR'], 'settings_dialog.ui')
        super().__init__(parent, ui_global_path, gv, *args, **kwargs)

        self.addPrinterPushButton.clicked.connect(self.addNewSpecialPrinter)

    @abc.abstractmethod
    def saveMachineSettings(self):
        ''' Save the settings specific to a mahichine (3D printer / laser cutter). '''

        with open(self.gv['SETTINGS_FILE_PATH'], 'r') as settings_file:
            settings_dict = json.load(settings_file)

        with open(self.gv['SETTINGS_FILE_PATH'], 'w' ) as settings_file:
            json.dump(settings_dict, settings_file, indent=4)

    @abc.abstractmethod
    def validateMachineSettings(self) -> bool:
        ''' Validate the machine specific settings. '''
        check_and_warnings = []
                # check input values
        for check, warning_string in check_and_warnings:
            if check:
                WarningQMessageBox(self, self.gv, warning_string)
                return False
        return True

    def restartApp(self):
        ''' Restart the application. '''
        subprocess.call("python " + '"'+
            f'{os.path.join(self.gv["REPO_DIR_HOME"], "printer/src/printer_app.py")}'
                        +'"', shell=True)

    def addNewSpecialPrinter(self):
        ''' Add a new special printer. '''
        AddPrinterQDialog(self).exec()


class AddPrinterQDialog(QDialog):
    ''' Add a new special printer dialog. '''

    def __init__(self, parent: QWidget, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        loadUi(os.path.join(gv['LOCAL_UI_DIR'], 'add_printer_dialog.ui'), self)



        self.buttonBox.accepted.connect(self.applySettings)
        self.addPropertyButton.clicked.connect(self.applyNewProperty)

        self.customListLineEdit.setHidden(True)
        self.customListLabel.setHidden(True)
        self.dataTypeQComboBox.currentIndexChanged.connect(self.onDataTypeQComboBoxChanged)

        self.customListLineEdit.textChanged.connect(
                partial(check_comma_seperated_tuple, self.customListLineEdit, gv))

    def applyNewProperty(self):
        ''' Validate and add new property. '''
        if self.newPropertyNameLineEdit.text() == '':
            return

        if self.dataTypeQComboBox ==  'Custom List of Stings':
            data_type = self.customListLineEdit.text()
        else:
            data_type = self.dataTypeQComboBox.text()
        print(f"data_type {data_type}")


    def applySettings(self):
        ''' Validate and save settings. '''


        if self.validateSettings():
            self.saveSettings()
            TimedMessage(self, gv, 'Settings saved, Restarting Creator Administrator.')
            self.close()
            self.parent().close()
            self.restartApp()


    def validateSettings(self) -> bool:
        ''' Validate general (not machine specific) settings. '''

#         check_types_and_warnings = [
#             (not self.checkInt(self.daysToKeepJobsLineEdit),
#             f'Days to Store Jobs is not an number but {self.daysToKeepJobsLineEdit.text()}'),

#             (not self.checkExtensionsTuple(self.acceptedExtentionsLineEdit),
#             'Accepted Extensions could not be convered to a list of extensions'),

#             (not self.checkMaterialTuple(self.acceptedMaterialsLineEdit),
#             'Accepted Materials could not be convered to a list of materials')]

#         # first, check types, otherwise type errors might break upcoming checks
#         for check, warning_string in check_types_and_warnings:
#             if check:
#                 WarningQMessageBox(self, self.gv, warning_string)
#                 return False

#         check_and_warnings = [
#             (int(self.daysToKeepJobsLineEdit.text()) < 0,
#             f'Days to Store Jobs is not an positive number but {self.daysToKeepJobsLineEdit.text()}'),

#             (not self.checkIsDirectory(self.selectDataDirectoryButton),
#             f'Data Directory {self.selectDataDirectoryButton.folder_global_path} is not a directory'),

#             (not self.checkIsDirectory(self.selectTodoDirectoryButton),
#             f'Todo Directory {self.selectTodoDirectoryButton.folder_global_path} is not a directory'),
#          ]

#         for template_name, widget_button in (('RECEIVED_MAIL_TEMPLATE', self.selectReceivedTemplateButton),
#                                              ('FINISHED_MAIL_TEMPLATE', self.selectFinishedTemplateButton),
#                                              ('DECLINED_MAIL_TEMPLATE', self.selectDeclinedTemplateButton)):
#             if widget_button.file_global_path is not None:
#                 check_and_warnings.append(
#                     (not os.path.exists(widget_button.file_global_path),
#                     f'Template {template_name} path {widget_button.file_global_path} does not exist'))

#                 check_and_warnings.append((not (self.checkHTML(widget_button)),
#                 f'Template {template_name} should be an HTML file and is {widget_button.file_global_path}'))


#         # check input values
#         for check, warning_string in check_and_warnings:
#             if check:
#                 WarningQMessageBox(self.gv, self, warning_string)
#                 return False
#         return True
        pass

    def onDataTypeQComboBoxChanged(self):
        ''' Show/hide custom list option. '''
        if self.dataTypeQComboBox.currentText() == 'Custom List of Stings':
            self.customListLineEdit.setHidden(False)
            self.customListLabel.setHidden(False)
        else:
            self.customListLineEdit.setHidden(True)
            self.customListLabel.setHidden(True)
