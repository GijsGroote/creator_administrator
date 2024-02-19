import time
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

class TimedMessage(QMessageBox):
    ''' Short message that can only be clicked away. '''

    def __init__(self, gv: dict, parent: QWidget, text: str, icon=QMessageBox.Icon.Information):
        super().__init__(parent)

        # DISPLAY THE TIMER WOULD BE NICE, then this should be a QWidget
        if gv['DISPLAY_TEMP_MESSAGES']:
            self.setWindowTitle('')
            self.setText(text)
            self.setIcon(icon)

            # self.progress = QProgressBar(self)
            # self.progress.setGeometry(200, 80, 250, 20)
            # self.btn = QPushButton('Download', self)
            # self.btn.clicked.connect(self.download)

            self.setStandardButtons(QMessageBox.StandardButton.NoButton)
            QShortcut(QKeySequence(Qt.Key.Key_Escape), self).activated.connect(self.exit)
            QShortcut(QKeySequence(Qt.Key.Key_Enter), self).activated.connect(self.doNothing)

            time_to_close = 4000
            self.timer = QTimer(self)
            self.timer.setInterval(time_to_close)
            self.timer.timeout.connect(self.exit)
            self.timer.start()
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

    def doNothing(self):
        ''' Literally do nothing. '''
        pass
        
    def getMainWidget(self, widget):
        while widget.parent() is not None:
            print(f'the main widget is now {widget.objectName()}')
            widget = widget.parent()

        return widget 

class JobFinishedMessageBox(QMessageBox):

    def __init__(self, parent, text, icon=QMessageBox.Icon.Information, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.setText(text)
        self.addButton(QMessageBox.StandardButton.Ok)
        self.setIcon(icon)
        self.exec()

class YesOrNoMessageBox(QMessageBox):

    def __init__(self, parent: QWidget, text: str, yes_button_text='Yes', no_button_tex='No', *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.setText(text)
        self.addButton(QMessageBox.StandardButton.No)
        self.addButton(QMessageBox.StandardButton.Yes)
        self.setDefaultButton(QMessageBox.StandardButton.Yes)
        self.setIcon(QMessageBox.Icon.Question)
        self.button(QMessageBox.StandardButton.Yes).setText(no_button_tex)
        self.button(QMessageBox.StandardButton.Yes).setText(yes_button_text)

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
