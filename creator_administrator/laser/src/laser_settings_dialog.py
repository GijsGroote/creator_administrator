import sys
import os
import json
import subprocess
from functools import partial

from src.settings_dialog import SettingsQDialog
from src.qmessagebox import WarningQMessageBox
from src.directory_functions import shorten_folder_name

from global_variables import gv

class LaserSettingsQDialog(SettingsQDialog):

    def __init__(self, parent, *args, **kwargs):
        ui_global_path = os.path.join(gv['LOCAL_UI_DIR'], 'settings_dialog.ui')
        super().__init__(parent, ui_global_path, gv, *args, **kwargs)

        self.loadLaserSettings()

    def loadLaserSettings(self):
        ''' Load the laser specific settings. '''

        template_name = 'UNCLEAR_MAIL_TEMPLATE'
        widget_button = self.selectUnclearTemplateButton

        if template_name in self.gv:
            widget_button.setStartingDirectory(os.path.dirname(self.gv[template_name]))
            widget_button.setText(shorten_folder_name(self.gv[template_name]))
            widget_button.file_global_path = self.gv[template_name]
        widget_button.clicked.connect(partial(self.checkHTML, widget_button))

    def saveMachineSettings(self):
        ''' Save the settings specific to a mahichine (3D printer / laser cutter). '''

        with open(self.gv['SETTINGS_FILE_PATH'], 'r') as settings_file:
            settings_dict = json.load(settings_file)

            template_name = 'UNCLEAR_MAIL_TEMPLATE'
            widget_button = self.selectUnclearTemplateButton

            if widget_button.file_global_path is not None:
                if sys.platform == 'win32':
                    settings_dict[template_name] = widget_button.file_global_path.replace('/', '\\')
                else:
                    settings_dict[template_name] = widget_button.file_global_path


        with open(self.gv['SETTINGS_FILE_PATH'], 'w' ) as settings_file:
            json.dump(settings_dict, settings_file, indent=4)


    def validateMachineSettings(self) -> bool:
        ''' Validate the machine specific settings. '''

        check_and_warnings = []
        template_name = 'UNCLEAR_MAIL_TEMPLATE'
        widget_button = self.selectUnclearTemplateButton

        if widget_button.file_global_path is not None:
            check_and_warnings.append(
                (not os.path.exists(widget_button.file_global_path),
                f'Template {template_name} path {widget_button.file_global_path} does not exist'))

            check_and_warnings.append((not (self.checkHTML(widget_button)),
            f'Template {template_name} should be an HTML file and is {widget_button.file_global_path}'))

        # check input values
        for check, warning_string in check_and_warnings:
            if check:
                WarningQMessageBox(self, self.gv, warning_string)
                return False
        return True


    def restartApp(self):
        ''' Restart the application. '''
        subprocess.call("python " + '"'+
            f'{os.path.join(self.gv["REPO_DIR_HOME"], "laser/src/laser_app.py")}'
                        +'"', shell=True)
