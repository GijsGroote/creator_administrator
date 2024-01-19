import os
from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic


class MainWindow(QMainWindow):

    def __init__(self, ui_global_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(ui_global_path, self)


        # job_name = 'haha'

        # message_worker = Worker(TimedQMessageBox,
        #                         text=f"Job finished mail send to {job_name}",
        #                         parent=self)
        # self.threadpool.start(message_worker)

        # TODO: save height and widtt and position when closing, use that when opening
        # desktop_center = QApplication.desktop().availableGeometry().center()
        # self.move(desktop_center.x() - int(self.width()*0.5), desktop_center.y() - int(self.height()*0.5))

    def keyPressEvent(self, event):
        ''' Handle shortcuts on main window. '''

        # close application on 'q' press
        if isinstance(event, QKeyEvent):
            if event.key() == Qt.Key_Q:
                self.close()

        # Move around using arrows or vim style
        if isinstance(event, QKeyEvent):
            if event.key() == Qt.Key_H or event.key() == Qt.Key_Left:
                self.jobsQTabWidget.toLeftTab()

            if event.key() == Qt.Key_L or event.key() == Qt.Key_Right:
                self.jobsQTabWidget.toRightTab()

            if event.key() == Qt.Key_K or event.key() == Qt.Key_Up:
                self.jobsQTabWidget.toPreviousRow()

            if event.key() == Qt.Key_J or event.key() == Qt.Key_Down:
                self.jobsQTabWidget.toNextRow()

            # shortcut on Enter key
            if event.key() == Qt.Key_Return:
                # go through GUI structure to call the itemEnterPressed function the currenlty displayed item
                self.jobsQTabWidget.currentWidget().findChild(QStackedWidget).currentWidget().findChild(QListWidget).itemEnterPressed()
            # shortcut on Esc button
            # if event.key() == Qt.Key_Escape:
                
            #     for child in self.jobsQTabWidget.currentWidget().findChild(QStackedWidget).currentWidget().findChildren(QPushButton):
            #         print(f"stupid {child.objectName()}")
            #     print(f"who you {self.jobsQTabWidget.currentWidget().findChild(QStackedWidget).currentWidget().objectName()}")
            #     print(self.jobsQTabWidget.currentWidget().findChild(QStackedWidget).currentWidget().findChild(BackQPushButton).objectName())

