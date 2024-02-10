import os
from functools import partial
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6 import uic


class SettingsQDialog(QDialog):

    def __init__(self, parent: QWidget, ui_global_path: str, gv: dict, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        uic.loadUi(ui_global_path, self)
        
        self.daysToKeepJobsLineEdit.setText(str(gv['DAYS_TO_KEEP_JOBS']))
        self.daysToKeepJobsLineEdit.textChanged.connect(partial(self.checkInt, self.daysToKeepJobsLineEdit))

        self.acceptedExtentionsLineEdit.setText(str(gv['ACCEPTED_EXTENSIONS'])[1:-1].replace("'", ''))
        self.acceptedExtentionsLineEdit.textChanged.connect(
                partial(self.checkExtensionsTuple, self.acceptedExtentionsLineEdit))

        self.accepetedMaterialsLineEdit.setText(str(gv['ACCEPTED_MATERIALS'])[1:-1].replace("'", ''))
        self.accepetedMaterialsLineEdit.textChanged.connect(
                partial(self.checkMaterialTuple, self.accepetedMaterialsLineEdit))

        if gv['DARK_MODE']:
            self.darkModeCheckBox.setChecked(True)

        if gv['DISPLAY_TEMP_MESSAGES']:
            self.dispTempMessageCheckBox.setChecked(True)

        if gv['DISPLAY_WARNING_MESSAGES']:
            self.dispWarnMessageCheckBox.setChecked(True)

        if gv['ONLY_UNREAD_MAIL']:
            self.onlyUnreadMailCheckBox.setChecked(True)

        if gv['MOVE_MAILS_TO_VERWERKT_FOLDER']:
            self.moveMailToVerwerktCheckBox.setChecked(True)

        self.selectOutlookEXEsButton.setText(self.shortenFolderName(gv['OUTLOOK_PATH']))
        self.selectDataDirectoryButton.setText(self.shortenFolderName(gv['DATA_DIR_HOME']))
        self.selectTodoDirectoryButton.setText(self.shortenFolderName(gv['TODO_DIR_HOME']))

    def shortenFolderName(self, path) -> str:
        ''' Return a short folder name. '''

        if len(path) > 50:
            path = '../'+path[-max_char_length+3:]
        return path


    def checkInt(self, widget: QWidget):
        try:
            int(widget.text())
            widget.setStyleSheet("background-color: rgba(0, 255, 0, 0.4);")
        except:
            widget.setStyleSheet("background-color: rgba(255, 0, 0, 0.4);")

    def checkExtensionsTuple(self, widget: QWidget):
        try:
            self.StrToTuple(widget.text())
        except:
            widget.setStyleSheet("background-color: rgba(255, 0, 0, 0.4);")

        for string in widget.text().split(', '):
            if not (string.startswith('.') and string[1:].isalnum()):
                widget.setStyleSheet("background-color: rgba(255, 0, 0, 0.4);")
                return

        widget.setStyleSheet("background-color: rgba(0, 255, 0, 0.4);")

    def checkMaterialTuple(self, widget: QWidget):
        try:
            self.StrToTuple(widget.text())
        except:
            widget.setStyleSheet("background-color: rgba(255, 0, 0, 0.4);")

        for string in widget.text().split(', '):
            if not string.isalpha():
                widget.setStyleSheet("background-color: rgba(255, 0, 0, 0.4);")
                return

        widget.setStyleSheet("background-color: rgba(0, 255, 0, 0.4);")

    def StrToTuple(self, text: str):
        return tuple(text.split(', '))

