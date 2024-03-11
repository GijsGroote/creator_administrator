import os
import webbrowser
import pkg_resources

from PyQt6.QtWidgets import QDialog, QWidget, QListWidgetItem, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut, QFont
from PyQt6.uic import loadUi


class CreateJobsQDialog(QDialog):
    ''' Create jobs with data from mail or the file system. '''
    pass

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


class SelectOptionsQDialog(QDialog):
    ''' Select one of the options. '''

    def __init__(self, parent: QWidget, gv: dict, options: list, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.gv = gv

        
        loadUi(os.path.join(self.gv['GLOBAL_UI_DIR'], 'select_done_dialog.ui'), self)


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

    def openGithubInBrowser(self, _):
        ''' Open Github in browser. '''
        webbrowser.open('https://github.com/GijsGroote/creator_administrator/')

    def closeDialog(self):
        ''' Close the dialog, press cancel. '''
        self.close()



class SelectQDialog(QDialog):
    """ Select file dialog. """
    def __init__(self, parent, gv: dict, ui_global_path: str, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.gv=gv

        loadUi(ui_global_path, self)

        # shortcut on Esc button
        QShortcut(QKeySequence(Qt.Key.Key_Escape), self).activated.connect(self.closeDialog)

    def closeDialog(self):
        ''' Close the dialog, press cancel. '''
        self.close()

class FilesSelectQDialog(SelectQDialog):
    """ Select files dialog. """
    def __init__(self, parent: QWidget, gv: dict, *args, **kwargs):
        ui_global_path = os.path.join(gv['GLOBAL_UI_DIR'], 'select_files_dialog.ui')
        super().__init__(parent, gv, ui_global_path, *args, **kwargs)

        self.buttonBox.accepted.connect(self.validate)

    def validate(self):

        if len(self.selectFilesButton.files_global_paths) == 0:
            dlg = QMessageBox(self)
            dlg.setText('Select Files')
            dlg.exec()
            return

        contains_accepted_extension = False
        for file_global_path in self.selectFilesButton.files_global_paths:
            if file_global_path.lower().endswith(self.gv['ACCEPTED_EXTENSIONS']):
                contains_accepted_extension = True

        if not contains_accepted_extension:
            dlg = QMessageBox(self)
            dlg.setText(f'Selected files should contain one or more files with extension {self.gv["ACCEPTED_EXTENSIONS"]}')
            dlg.exec()
            return

        if len(self.projectNameQLineEdit.text()) == 0:
            dlg = QMessageBox(self)
            dlg.setText('Provide a Job Name')
            dlg.exec()
            return

        self.accept()

class FolderSelectQDialog(SelectQDialog):
    """ Select folder dialog. """
    def __init__(self, parent: QWidget, gv: dict, *args, **kwargs):
        ui_global_path = os.path.join(gv['GLOBAL_UI_DIR'], 'select_folders_dialog.ui')
        super().__init__(parent, gv, ui_global_path, *args, **kwargs)

        self.buttonBox.accepted.connect(self.validate)

    def validate(self):

        if self.selectFolderButton.folder_global_path is None:
            dlg = QMessageBox(self)
            dlg.setText('Select a Folder')
            dlg.exec()
            return

        if len(self.projectNameQLineEdit.text()) == 0:
            dlg = QMessageBox(self)
            dlg.setText('Provide a Project Name')
            dlg.exec()
            return

        self.accept()
