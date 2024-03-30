import os
import subprocess

from src.settings_dialog import SettingsQDialog

class PrintSettingsQDialog(SettingsQDialog):

    def __init__(self, parent, gv: dict, *args, **kwargs):
        ui_global_path = os.path.join(gv['LOCAL_UI_DIR'], 'settings_dialog.ui')
        super().__init__(parent, ui_global_path, gv, *args, **kwargs)

    def restartApp(self):
        ''' Restart the application. '''
        subprocess.call("python " + '"'+
            f'{os.path.join(self.gv["REPO_DIR_HOME"], "printer/src/printer_app.py")}'
                        +'"', shell=True)
