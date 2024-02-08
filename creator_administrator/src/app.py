import sys
from PyQt6 import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6 import uic

class MainWindow(QMainWindow):

    def __init__(self, ui_global_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(ui_global_path, self)

    def keyPressEvent(self, event):
        ''' Handle shortcuts on main window. '''

        # close application on 'q' press
        if isinstance(event, QKeyEvent):
            if event.key() == Qt.Key.Key_Q:
                self.close()

        # Move around using arrows or vim style
        # if isinstance(event, QKeyEvent):
        #     if event.key() == Qt.Key_H or event.key() == Qt.Key_Left:
        #         self.jobsQTabWidget.toLeftTab()

        #     if event.key() == Qt.Key_L or event.key() == Qt.Key_Right:
        #         self.jobsQTabWidget.toRightTab()

        #     if event.key() == Qt.Key_K or event.key() == Qt.Key_Up:
        #         self.jobsQTabWidget.toPreviousRow()

        #     if event.key() == Qt.Key_J or event.key() == Qt.Key_Down:
        #         self.jobsQTabWidget.toNextRow()

            # shortcut on Enter key
            if event.key() == Qt.Key.Key_Return:
                # go through GUI structure to call the itemEnterPressed function the currenlty displayed item
                self.jobsQTabWidget.currentWidget().findChild(QStackedWidget).currentWidget().findChild(QListWidget).itemEnterPressed()
            # shortcut on Esc button
            # if event.key() == Qt.Key_Escape:
                
            #     for child in self.jobsQTabWidget.currentWidget().findChild(QStackedWidget).currentWidget().findChildren(QPushButton):
            #         print(f"stupid {child.objectName()}")
            #     print(f"who you {self.jobsQTabWidget.currentWidget().findChild(QStackedWidget).currentWidget().objectName()}")
            #     print(self.jobsQTabWidget.currentWidget().findChild(QStackedWidget).currentWidget().findChild(BackQPushButton).objectName())

