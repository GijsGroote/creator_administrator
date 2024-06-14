import os
import time

from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import (
        QDialog,
        QWidget,
        QMessageBox,
        QApplication)

from PyQt6.QtCore import Qt, QObject, pyqtSignal, pyqtSlot, QRunnable
from PyQt6.uic import loadUi

class YesOrNoMessageBox(QMessageBox):

    def __init__(self, parent: QWidget, text: str, *args, yes_button_text='Yes', no_button_text='No', **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.setText(text)
        self.addButton(QMessageBox.StandardButton.Yes)
        self.addButton(QMessageBox.StandardButton.No)
        self.setDefaultButton(QMessageBox.StandardButton.Yes)
        self.setIcon(QMessageBox.Icon.Question)
        self.button(QMessageBox.StandardButton.Yes).setText(yes_button_text)
        self.button(QMessageBox.StandardButton.No).setText(no_button_text)

    def answer(self) -> bool:
        ''' Return True for yes, False for no. '''

        if self.exec()==QMessageBox.StandardButton.Yes:
            return True
        return False


class InfoQMessageBox(QMessageBox):

    def __init__(self, parent: QWidget, text: str, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.setText(text)
        self.addButton(QMessageBox.StandardButton.Ok)
        self.setIcon(QMessageBox.Icon.Information)
        self.exec()


class WarningQMessageBox(QMessageBox):

    def __init__(self, parent: QWidget, gv: dict, text: str, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        if gv['DISPLAY_WARNING_MESSAGES']:
            self.setText(text)
            self.addButton(QMessageBox.StandardButton.Ok)
            self.setIcon(QMessageBox.Icon.Warning)
            self.exec()

class ErrorQMessageBox(QMessageBox):

    def __init__(self, parent: QWidget, text: str, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.setText(text)
        self.addButton(QMessageBox.StandardButton.Ok)
        self.setIcon(QMessageBox.Icon.Critical)
        self.exec()


class TimedMessage(QDialog):
    ''' Short message that can only be clicked away. '''

    def __init__(self, parent: QWidget, gv: dict, text: str):
        super().__init__(parent)

        if gv['DISPLAY_TEMP_MESSAGES']:
            loadUi(os.path.join(gv['GLOBAL_UI_DIR'], 'timed_message_dialog.ui'), self)
            self.textLabel.setText(text)
            self.progressBar.setStyleSheet('''
                QProgressBar {
                 background-color: #C0C6CA;
                 border: 0px;
                 padding: 0px;
                 height: 20px;
                }
                QProgressBar::chunk {
                 background: #7D94B0;
                 width:5px
                }
                ''')

            self.runner = ProgressBarRunner()
            self.runner.signals.progress.connect(self.progressBar.setValue)
            self.runner.signals.finished.connect(self.exit)
            gv['THREAD_POOL'].start(self.runner)

            QShortcut(QKeySequence(Qt.Key.Key_Escape), self).activated.connect(self.exit)
            QShortcut(QKeySequence(Qt.Key.Key_Return), self).activated.connect(self.exit)

            self.exec()
            
    def moveToTopRightOfScreen(self):
        ''' Move widget to the top right of the screen. '''
        x = QApplication.desktop().screenGeometry().width() - self.width()
        self.move(x-100, 100)
        
    def moveToTopOfScreen(self):
        ''' Move widget to top of screen, horizontally centered. '''
        x = (QApplication.desktop().screenGeometry().width() - self.width()) // 2
        self.move(x, 100)

    def moveToTopRightCorner(self, parent):
        parent_geometry = parent.geometry()
        parent_right_x = parent_geometry.x() + parent_geometry.width()
        parent_top_y = parent_geometry.y()
        margin = 0

        self.move(parent_right_x-self.geometry().width()-30-margin, parent_top_y+38+margin)

    def exit(self):
        self.deleteLater() 
        self.close()

class ProgressBarSignals(QObject):
    progress = pyqtSignal(int)
    finished = pyqtSignal()

class ProgressBarRunner(QRunnable):

    def __init__(self):
        super().__init__()
        self.signals = ProgressBarSignals()

    @pyqtSlot()
    def run(self):
        for n in range(100):
            self.signals.progress.emit(100-n)
            time.sleep(0.03)
        self.signals.finished.emit()



