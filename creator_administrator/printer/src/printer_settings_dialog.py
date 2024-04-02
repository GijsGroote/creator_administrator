import os
import json
import abc
import subprocess

from src.settings_dialog import SettingsQDialog
from src.qmessagebox import WarningQMessageBox

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
        print("hey, add that shit")

