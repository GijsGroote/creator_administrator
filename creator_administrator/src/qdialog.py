import os
import pkg_resources
from PyQt6 import uic
from PyQt6.QtWidgets import *

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut

from PyQt6.uic import loadUi

from global_variables import gv # TODO: what in the hell is this here?


class ImportFromMailQDialog(QDialog):
    """ Import from mail dialog. """
    def __init__(self, parent, ui_global_path, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        loadUi(ui_global_path, self)
        
        # shortcut on Esc button
        QShortcut(QKeySequence(Qt.Key.Key_Escape), self).activated.connect(self.closeDialog)

    def closeDialog(self):
        ''' Close the dialog, press cancel. '''
        self.close()

class SelectQDialog(QDialog):
    """ Select file dialog. """
    def __init__(self, parent, ui_global_path, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        loadUi(ui_global_path, self)
        self.passwordQLineEdit.textChanged.connect(partial(self.check_password, gv=gv))

        # shortcut on Esc button
        QShortcut(QKeySequence(Qt.Key.Key_Escape), self).activated.connect(self.closeDialog)

    def check_password(self, gv: dict):
        if self.passwordQLineEdit.text() == gv['PASSWORD']:
            self.passwordQLineEdit.setStyleSheet("background-color: rgba(0, 255, 0, 0.4);")
        else:
            self.passwordQLineEdit.setStyleSheet("background-color: rgba(255, 0, 0, 0.4);")

    def closeDialog(self):
        ''' Close the dialog, press cancel. '''
        self.close()

class SelectOptionsQDialog(QDialog):
    ''' Select one of the options. '''

    def __init__(self, parent, options: list, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        
        loadUi(os.path.join(gv['LOCAL_UI_DIR'], 'select_material_done_dialog.ui'), self)

        # QShortcut(QKeySequence(Qt.Key_Return), self).activated.connect(self.toggleSelection)

        # shortcuts on arrow keys
        QShortcut(QKeySequence(Qt.Key.Key_Up), self).activated.connect(self.toPreviousRow)
        QShortcut(QKeySequence(Qt.Key.Key_Down), self).activated.connect(self.toNextRow)

        # shortcuts on VIM motions
        QShortcut(QKeySequence('k'), self).activated.connect(self.toPreviousRow)
        QShortcut(QKeySequence('j'), self).activated.connect(self.toNextRow)

        for (option, option_data) in options:

            item = QListWidgetItem()
            item.setData(1, option_data)
            item.setText(option)
            self.optionsQListWidget.addItem(item)

    # def toggleSelection(self):
    #     current_item = self.optionsQListWidget.currentItem()
        
    #     if current_item is None:
    #         print('yeah that is noen')
    #     self.optionsQListWidget.itemClicked(current_item)

    def toNextRow(self):
        opt_ql_widget = self.optionsQListWidget

        if opt_ql_widget.currentRow() == opt_ql_widget.count()-1:
            opt_ql_widget.setCurrentRow(0)
        else:
            opt_ql_widget.setCurrentRow(opt_ql_widget.currentRow()+1)

    def toPreviousRow(self):
        opt_ql_widget = self.optionsQListWidget

        if opt_ql_widget.currentRow() == 0:
            opt_ql_widget.setCurrentRow(opt_ql_widget.count()-1)
        else:
            opt_ql_widget.setCurrentRow(opt_ql_widget.currentRow()-1)

class AboutDialog(QDialog):
    """ Import from mail dialog. """
    def __init__(self, parent: QWidget, gv: dict, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        loadUi(os.path.join(gv['GLOBAL_UI_DIR'], 'about_widget.ui') , self)

        self.versionLabel.setText(pkg_resources.get_distribution('creator_administrator').version)

        # shortcut on Esc button
        QShortcut(QKeySequence(Qt.Key.Key_Escape), self).activated.connect(self.closeDialog)

    def closeDialog(self):
        ''' Close the dialog, press cancel. '''
        self.close()

