import os
import subprocess

from src.settings_dialog import SettingsQDialog

class LaserSettingsQDialog(SettingsQDialog):

    def __init__(self, parent, gv: dict, *args, **kwargs):
        ui_global_path = os.path.join(gv['LOCAL_UI_DIR'], 'settings_dialog.ui')
        super().__init__(parent, ui_global_path, gv, *args, **kwargs)

    # TODO: add settings specific for the lasers here

    def restartApp(self):
        ''' Restart the application. '''
        subprocess.call("python " + '"'+
            f'{os.path.join(self.gv["REPO_DIR_HOME"], "laser/src/laser_app.py")}'
                        +'"', shell=True)
