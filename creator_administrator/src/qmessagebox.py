import os
import time

from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import (
        QDialog,
        QWidget,
        QMessageBox,
        QApplication, 
        QProgressBar,
        QLabel)

from PyQt6.QtCore import Qt, QTimer, QObject, pyqtSignal, pyqtSlot, QRunnable
from PyQt6.uic import loadUi


class WorkerSignals(QObject):
    progress = pyqtSignal(int)
    finished = pyqtSignal()

class JobRunner(QRunnable):

    def __init__(self):
        super().__init__()
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        for n in range(100):
            self.signals.progress.emit(100-n)
            time.sleep(0.05)
        self.signals.finished.emit()

class TimedMessage(QDialog):
    ''' Short message that can only be clicked away. '''

    def __init__(self, gv: dict, parent: QWidget, text: str, icon=QMessageBox.Icon.Information):
        super().__init__(parent)

        # DISPLAY THE TIMER WOULD BE NICE, then this should be a QWidget
        if gv['DISPLAY_TEMP_MESSAGES']:

            loadUi(os.path.join(gv['GLOBAL_UI_DIR'], 'timed_message_dialog.ui'), self)
            self.textLabel.setText(text)


            self.runner = JobRunner()
            self.runner.signals.progress.connect(self.update_progress)
            self.runner.signals.finished.connect(self.exit)
            gv['THREAD_POOL'].start(self.runner)

            # self.setStandardButtons(QMessageBox.StandardButton.NoButton)
            QShortcut(QKeySequence(Qt.Key.Key_Escape), self).activated.connect(self.exit)
            # QShortcut(QKeySequence(Qt.Key.Key_Enter), self).activated.connect(self.doNothing)

            self.exec()

    def update_progress(self, n):
        self.progressBar.setValue(n)


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

    def doNothing(self):
        ''' Literally do nothing. '''
        
    def getMainWidget(self, widget):
        while widget.parent() is not None:
            print(f'the main widget is now {widget.objectName()}')
            widget = widget.parent()

        return widget 

class JobFinishedMessageBox(QMessageBox):

    def __init__(self, parent, text, *args, icon=QMessageBox.Icon.Information, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.setText(text)
        self.addButton(QMessageBox.StandardButton.Ok)
        self.setIcon(icon)
        self.exec()

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

    def __init__(self, gv: dict, parent: QWidget, text: str, *args, **kwargs):
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



