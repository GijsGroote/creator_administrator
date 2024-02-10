import os
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from src.settings_dialog import SettingsQDialog

class LaserSettingsQDialog(SettingsQDialog):

    def __init__(self, parent, gv: dict, *args, **kwargs):
        ui_global_path = os.path.join(gv['UI_DIR_HOME'], 'settings_dialog.ui')
        super().__init__(parent, ui_global_path, gv, *args, **kwargs)


