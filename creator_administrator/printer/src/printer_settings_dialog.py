import os
from src.settings_dialog import SettingsQDialog

class PrintSettingsQDialog(SettingsQDialog):

    def __init__(self, parent, gv: dict, *args, **kwargs):
        ui_global_path = os.path.join(gv['LOCAL_UI_DIR'], 'settings_dialog.ui')
        super().__init__(parent, ui_global_path, gv, *args, **kwargs)

    # TODO: add settings specific for the prints here
