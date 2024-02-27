import os
import webbrowser
from functools import partial
import pkg_resources

from PyQt6.QtWidgets import QDialog, QWidget, QListWidgetItem
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut, QFont
from PyQt6.uic import loadUi

class ImportFromMailQDialog(QDialog):
    """ Import from mail dialog. """
    def __init__(self, parent: QWidget, gv: dict, ui_global_path: str, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.gv=gv

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
        self.passwordQLineEdit.textChanged.connect(self.check_password)

        # shortcut on Esc button
        QShortcut(QKeySequence(Qt.Key.Key_Escape), self).activated.connect(self.closeDialog)

    def check_password(self):
        if self.passwordQLineEdit.text() == self.gv['PASSWORD']:
            self.passwordQLineEdit.setStyleSheet(f'background_color: {self.gv["GOOD_COLOR_RGBA"]};')
        else:
            self.passwordQLineEdit.setStyleSheet(f'background-color: {self.gv["BAD_COLOR_RGBA"]};')


    def closeDialog(self):
        ''' Close the dialog, press cancel. '''
        self.close()

class SelectOptionsQDialog(QDialog):
    ''' Select one of the options. '''

    def __init__(self, parent: QWidget, gv: dict, options: list, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.gv = gv

        
        loadUi(os.path.join(self.gv['LOCAL_UI_DIR'], 'select_material_done_dialog.ui'), self)

        # QShortcut(QKeySequence(Qt.Key_Return), self).activated.connect(self.toggleSelection)

        # shortcuts on arrow keys
        QShortcut(QKeySequence(Qt.Key.Key_Up), self).activated.connect(self.toPreviousRow)
        QShortcut(QKeySequence(Qt.Key.Key_Down), self).activated.connect(self.toNextRow)

        # shortcuts on VIM motions
        QShortcut(QKeySequence('k'), self).activated.connect(self.toPreviousRow)
        QShortcut(QKeySequence('j'), self).activated.connect(self.toNextRow)

        for (option, option_data, done) in options:

            item = QListWidgetItem()
            item.setData(1, option_data)

            if isinstance(done, bool):
                if done:
                    item.setText('✅ '+option)
                else:
                    item.setText('❎ '+option)
            else:
                    item.setText(option)

            item.setFont(QFont('Cantarell', 14))
            self.optionsQListWidget.addItem(item)

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
        self.githubSiteLabel.mousePressEvent = self.openGithubInBrowser

        if gv['DARK_THEME']:
            self.githubSiteLabel.setStyleSheet("QLabel { color : aqua; }");
        else:
            self.githubSiteLabel.setStyleSheet("QLabel { color : blue; }");


        # shortcut on Esc button
        QShortcut(QKeySequence(Qt.Key.Key_Escape), self).activated.connect(self.closeDialog)

    def openGithubInBrowser(self):
        ''' Open Github in browser. '''
        webbrowser.open('https://github.com/GijsGroote/creator_administrator/')

    def closeDialog(self):
        ''' Close the dialog, press cancel. '''
        self.close()

