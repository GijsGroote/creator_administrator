from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class TimedMessage(QMessageBox):
    ''' Short message that can only be clicked away. 
    It should not interfere with the main application, it does that anyway...'''

    def __init__(self, gv, parent, text: str, icon=QMessageBox.Information):
        super().__init__(parent)

        if gv['DISPLAY_TEMP_MESSAGES']:
            # self.setModal(0)
            self.setWindowTitle('')
            self.setText(text)
            # label = QLabel(text, self)
            # layout = QVBoxLayout()
            # layout.addWidget(label)
            # self.setLayout(layout)
            self.adjustSize()
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

    def __init__(self, parent, text='setthis', icon=QMessageBox.Information, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.setText(text)
        self.addButton(QMessageBox.Ok)
        self.setIcon(icon)
        self.exec_()

class YesOrNoMessageBox(QMessageBox):

    def __init__(self, parent, text='setthis', icon=QMessageBox.Question, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.setText(text)
        self.addButton(QMessageBox.No)
        self.addButton(QMessageBox.Yes)
        self.setDefaultButton(QMessageBox.Yes)
        self.setIcon(icon)



class InfoQMessageBox(QMessageBox):

    def __init__(self, parent, text, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.setText(text)
        self.addButton(QMessageBox.Ok)
        self.setIcon(QMessageBox.Information)
        self.exec_()


class WarningQMessageBox(QMessageBox):

    def __init__(self, gv, parent, text, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        if gv['DISPLAY_WARNING_MESSAGES']:
            self.setText(text)
            self.addButton(QMessageBox.Ok)
            self.setIcon(QMessageBox.Warning)
            self.exec_()


class ErrorQMessageBox(QMessageBox):

    def __init__(self, parent, text=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.setText(text)
        self.addButton(QMessageBox.Ok)
        self.setIcon(QMessageBox.Critical)
        self.exec_()
