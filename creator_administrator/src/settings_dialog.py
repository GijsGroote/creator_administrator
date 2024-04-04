import os
import abc
import sys
import json
from functools import partial

from PyQt6.QtWidgets import QWidget, QDialog
from PyQt6.uic import loadUi

from src.directory_functions import shorten_folder_name
from src.qmessagebox import WarningQMessageBox, TimedMessage
from src.validate import (
        check_int,
        check_extensions_tuple,
        check_comma_seperated_tuple,
        check_html,
        check_is_directory)


class SettingsQDialog(QDialog):

    def __init__(self, parent: QWidget, ui_global_path: str, gv: dict, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        loadUi(ui_global_path, self)
        self.gv = gv
        self.buttonBox.accepted.connect(self.applySettings)
        self.loadSettings(gv)

    def loadSettings(self, gv: dict):
        ''' Load the existing settings. '''

        self.daysToKeepJobsLineEdit.setText(str(gv['DAYS_TO_KEEP_JOBS']))
        self.daysToKeepJobsLineEdit.textChanged.connect(partial(check_int, self.daysToKeepJobsLineEdit, self.gv))

        if len(gv['ACCEPTED_EXTENSIONS']) == 1:
            self.acceptedExtentionsLineEdit.setText(str(gv['ACCEPTED_EXTENSIONS'][0]))
        else:
            self.acceptedExtentionsLineEdit.setText(str(gv['ACCEPTED_EXTENSIONS'])[1:-1].replace("'", ''))

        self.acceptedExtentionsLineEdit.textChanged.connect(
                partial(check_extensions_tuple, self.acceptedExtentionsLineEdit, self.gv))

        if len(gv['ACCEPTED_MATERIALS']) == 1:
            self.acceptedMaterialsLineEdit.setText(str(gv['ACCEPTED_MATERIALS'][0]))
        else:
            self.acceptedMaterialsLineEdit.setText(str(gv['ACCEPTED_MATERIALS'])[1:-1].replace("'", ''))

        self.acceptedMaterialsLineEdit.textChanged.connect(
                partial(check_comma_seperated_tuple, self.acceptedMaterialsLineEdit, self.gv))


        for variable_name, check_box in (('DARK_THEME', self.darkModeCheckBox),
                                     ('DISPLAY_TEMP_MESSAGES', self.dispTempMessageCheckBox),
                                     ('DISPLAY_WARNING_MESSAGES', self.dispWarnMessageCheckBox),
                                     ('ONLY_UNREAD_MAIL', self.onlyUnreadMailCheckBox),
                                     ('MOVE_MAILS_TO_VERWERKT_FOLDER', self.moveMailToVerwerktCheckBox),
                                     ('SEND_MAILS_ON_SEPERATE_THREAD', self.sendMailThreadedCheckBox),
                                     ('EMPTY_TODO_DIR_BEFORE_EXPORT', self.emptyTodoDirCheckBox),
                                     ('DARK_THEME', self.darkModeCheckBox)):

            if gv[variable_name]:
                check_box.setChecked(True)


        for template_name, widget_button in (('RECEIVED_MAIL_TEMPLATE', self.selectReceivedTemplateButton),
                                             ('FINISHED_MAIL_TEMPLATE', self.selectFinishedTemplateButton),
                                             ('DECLINED_MAIL_TEMPLATE', self.selectDeclinedTemplateButton)):
            if template_name in gv:
                widget_button.setStartingDirectory(os.path.dirname(gv[template_name]))
                widget_button.setText(shorten_folder_name(gv[template_name], 45))
                widget_button.file_global_path = gv[template_name]
            widget_button.clicked.connect(partial(check_html, widget_button, self.gv))


        for folder_name, widget_button in (('DATA_DIR_HOME', self.selectDataDirectoryButton),
                                           ('TODO_DIR_HOME', self.selectTodoDirectoryButton)):
            widget_button.setStartingDirectory(gv[folder_name])
            widget_button.setText(shorten_folder_name(gv[folder_name], 45))
            widget_button.folder_global_path = gv[folder_name]
            widget_button.clicked.connect(partial(check_is_directory, widget_button, self.gv))


    def applySettings(self):
        ''' Save Settigns accepted function. '''
        if self.validateSettings() and self.validateMachineSettings():
            # save and restart application
            self.saveSettings()
            self.saveMachineSettings()
            TimedMessage(self, self.gv, 'Settings saved, Restarting Creator Administrator.')
            self.close()
            self.parent().close()
            self.restartApp()


    def validateSettings(self) -> bool:
        ''' Validate general (not machine specific) settings. '''

        check_types_and_warnings = [
            (check_int(self.daysToKeepJobsLineEdit, self.gv),
            f'Days to Store Jobs is not an number but {self.daysToKeepJobsLineEdit.text()}'),

            (check_extensions_tuple(self.acceptedExtentionsLineEdit, self.gv),
            'Accepted Extensions could not be convered to a list of extensions'),

            (check_comma_seperated_tuple(self.acceptedMaterialsLineEdit, self.gv),
            'Accepted Materials could not be convered to a list of materials')]

        # first, check types, otherwise type errors might break upcoming checks
        for check, warning_string in check_types_and_warnings:
            if not check:
                WarningQMessageBox(self, self.gv, warning_string)
                return False

        check_and_warnings = [
            (int(self.daysToKeepJobsLineEdit.text()) >= 0,
            f'Days to Store Jobs is not an positive number but {self.daysToKeepJobsLineEdit.text()}'),

            (check_is_directory(self.selectDataDirectoryButton, self.gv),
            f'Data Directory {self.selectDataDirectoryButton.folder_global_path} is not a directory'),

            (check_is_directory(self.selectTodoDirectoryButton, self.gv),
            f'Todo Directory {self.selectTodoDirectoryButton.folder_global_path} is not a directory'),
         ]

        for template_name, widget_button in (('RECEIVED_MAIL_TEMPLATE', self.selectReceivedTemplateButton),
                                             ('FINISHED_MAIL_TEMPLATE', self.selectFinishedTemplateButton),
                                             ('DECLINED_MAIL_TEMPLATE', self.selectDeclinedTemplateButton)):
            if widget_button.file_global_path is not None:
                check_and_warnings.append(
                    (os.path.exists(widget_button.file_global_path),
                    f'Template {template_name} path {widget_button.file_global_path} does not exist'))

                check_and_warnings.append((check_html(widget_button, self.gv),
                f'Template {template_name} should be an HTML file and is {widget_button.file_global_path}'))


        # check input values
        for check, warning_string in check_and_warnings:
            if not check:
                WarningQMessageBox(self, self.gv, warning_string)
                return False
        return True


    def saveSettings(self):
        ''' Save the settings to a JSON file. '''

        with open(self.gv['SETTINGS_FILE_PATH'], 'r') as settings_file:
            settings_dict = json.load(settings_file)

        settings_dict['ACCEPTED_EXTENSIONS'] = self.acceptedExtentionsLineEdit.text()
        settings_dict['ACCEPTED_MATERIALS'] =  self.acceptedMaterialsLineEdit.text()
        settings_dict['DAYS_TO_KEEP_JOBS'] = self.daysToKeepJobsLineEdit.text()

        if sys.platform == 'win32':
            settings_dict['DATA_DIR_HOME'] = self.selectDataDirectoryButton.folder_global_path.replace('/', '\\')
            settings_dict['TODO_DIR_HOME'] = self.selectTodoDirectoryButton.folder_global_path.replace('/', '\\')
        else:
            settings_dict['DATA_DIR_HOME'] = self.selectDataDirectoryButton.folder_global_path
            settings_dict['TODO_DIR_HOME'] = self.selectTodoDirectoryButton.folder_global_path

        for checkbox_name, widget in (('DISPLAY_WARNING_MESSAGES', self.dispWarnMessageCheckBox),
                                     ('DISPLAY_TEMP_MESSAGES', self.dispTempMessageCheckBox),
                                     ('ONLY_UNREAD_MAIL', self.onlyUnreadMailCheckBox),
                                     ('MOVE_MAILS_TO_VERWERKT_FOLDER', self.moveMailToVerwerktCheckBox),
                                     ('SEND_MAILS_ON_SEPERATE_THREAD', self.sendMailThreadedCheckBox),
                                     ('EMPTY_TODO_DIR_BEFORE_EXPORT', self.emptyTodoDirCheckBox),
                                     ('DARK_THEME', self.darkModeCheckBox)):

            settings_dict[checkbox_name] = 'true' if widget.isChecked() else 'false'

        for template_name, widget_button in (('RECEIVED_MAIL_TEMPLATE', self.selectReceivedTemplateButton),
                                             ('FINISHED_MAIL_TEMPLATE', self.selectFinishedTemplateButton),
                                             ('DECLINED_MAIL_TEMPLATE', self.selectDeclinedTemplateButton)):
            if widget_button.file_global_path is not None:
                if sys.platform == 'win32':
                    settings_dict[template_name] = widget_button.file_global_path.replace('/', '\\')
                else:
                    settings_dict[template_name] = widget_button.file_global_path


        with open(self.gv['SETTINGS_FILE_PATH'], 'w' ) as settings_file:
            json.dump(settings_dict, settings_file, indent=4)
    
    @abc.abstractmethod
    def validateMachineSettings(self) -> bool:
        ''' Validate the machine specific settings. '''

    @abc.abstractmethod
    def saveMachineSettings(self):
        ''' Save the settings specific to a mahichine (3D printer / laser cutter). '''

    @abc.abstractmethod
    def restartApp(self):
        ''' Restart the application. '''
