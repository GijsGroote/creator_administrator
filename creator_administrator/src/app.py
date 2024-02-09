import sys
from PyQt6 import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6 import uic
from src.qmessagebox import InfoQMessageBox

class MainWindow(QMainWindow):

    def __init__(self, ui_global_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(ui_global_path, self)

        self.showLaserDocumentationAction.triggered.connect(self.openLaserDocumentation)
        self.show3DPrintDocumentationAction.triggered.connect(self.open3DPrintDocumentation)

    def keyPressEvent(self, event):
        ''' Handle shortcuts on main window. '''

        # close application on 'q' press
        if isinstance(event, QKeyEvent):
            if event.key() == Qt.Key.Key_Q:
                self.close()

        # go through GUI structure to call the itemEnterPressed
        # function the currenlty displayed item
        if event.key() == Qt.Key.Key_Return:
                self.jobsQTabWidget.currentWidget().findChild(QStackedWidget).currentWidget().findChild(QListWidget).itemEnterPressed()

    # TODO: link toward documentation please
    def open3DPrintDocumentation(self):
        ''' Open 3D print documentation in web browser. '''
        InfoQMessageBox(self, 'Documentation dialog not yet implemented')

    def openLaserDocumentation(self):
        ''' Open Laser documentation in web browser. '''
        InfoQMessageBox(self, 'Documentation dialog not yet implemented')
