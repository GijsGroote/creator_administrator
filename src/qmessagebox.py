from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from tab_widget import JobsQTabWidget

class TimedMessage(QDialog):
    ''' Short message that can only be clicked away. 
    It should not interfere with the main application, it does that anyway...'''

    def __init__(self, parent, text: str, loc='top'):
        QDialog.__init__(self, parent)

        self.setModal(0)
        self.setWindowTitle('')
        label = QLabel(text, self)
        layout = QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)
        self.adjustSize()

        self.timer = QTimer(self)
        self.timer.setInterval(4000)
        self.timer.start()
        self.timer.timeout.connect(self.exit)

        self.show()
        if loc=='top':
            self.moveToTopOfScreen()
        elif loc=='topright':
            self.moveToTopRightCorner(parent)
        else: 
            raise ValueError(f'Unknown location {loc}')



        parent.grabKeyboard()
        # # let main window catch key press events
        # main_window_or_dialog = self.getMainWidget(parent)
        # jobs_qtab_widget = main_window_or_dialog.findChild(JobsQTabWidget, 'jobsQTabWidget')
        # if jobs_qtab_widget is None:
        #     # main_window_or_dialog.grabKeyboard()
        #     pass
        # else:
        #     jobs_qtab_widget.grabKeyboard()

        
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


class WarningQMessageBox(QMessageBox):

    def __init__(self, parent, text=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

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
