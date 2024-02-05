from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class TimedMessage(QMessageBox):
    ''' Short message that can only be clicked away. 
    It should not interfere with the main application, it does that anyway...'''

    def __init__(self, gv: dict, parent: QWidget, text: str, icon=QMessageBox.Information):
        super().__init__(parent)

        # DISPLAY THE TIMER WOULD BE NICE
        if gv['DISPLAY_TEMP_MESSAGES']:
            self.setWindowTitle('')
            self.setText(text)
            self.setIcon(icon)

            self.timer = QTimer(self)
            self.timer.setInterval(4000)
            self.timer.timeout.connect(self.exit)
            self.timer.start()
            self.exec_()


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
        
    def getMainWidget(self, widget):
        while widget.parent() is not None:
            print(f'the main widget is now {widget.objectName()}')
            widget = widget.parent()

        return widget 

class JobFinishedMessageBox(QMessageBox):

    def __init__(self, parent, text, icon=QMessageBox.Information, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.setText(text)
        self.addButton(QMessageBox.Ok)
        self.setIcon(icon)
        self.exec_()

class YesOrNoMessageBox(QMessageBox):

    def __init__(self, parent: QWidget, text: str, yes_button_text='Yes', no_button_tex='No', *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.setText(text)
        self.addButton(QMessageBox.No)
        self.addButton(QMessageBox.Yes)
        self.setDefaultButton(QMessageBox.Yes)
        self.setIcon(QMessageBox.Question)
        self.button(QMessageBox.Yes).setText(no_button_tex)
        self.button(QMessageBox.Yes).setText(yes_button_text)

    def answer(self) -> bool:
        ''' Return True for yes, False for no. '''

        if self.exec_()==QMessageBox.Yes:
            return True
        return False




class InfoQMessageBox(QMessageBox):

    def __init__(self, parent: QWidget, text: str, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.setText(text)
        self.addButton(QMessageBox.Ok)
        self.setIcon(QMessageBox.Information)
        self.exec_()


class WarningQMessageBox(QMessageBox):

    def __init__(self, gv: dict, parent: QWidget, text: str, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        if gv['DISPLAY_WARNING_MESSAGES']:
            self.setText(text)
            self.addButton(QMessageBox.Ok)
            self.setIcon(QMessageBox.Warning)
            self.exec_()

class ErrorQMessageBox(QMessageBox):

    def __init__(self, parent: QWidget, text: str, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.setText(text)
        self.addButton(QMessageBox.Ok)
        self.setIcon(QMessageBox.Critical)
        self.exec_()
