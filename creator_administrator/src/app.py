import sys
import webbrowser
from functools import partial
from PyQt6 import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6 import uic

from src.qmessagebox import InfoQMessageBox
from src.qdialog import AboutDialog

class MainWindow(QMainWindow):

    def __init__(self, ui_global_path: str, gv: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(ui_global_path, self)

        self.gv = gv

        self.openDocumentationAction.triggered.connect(partial(self.openWebPage, 'https://github.com/GijsGroote/creator_administrator/tree/main/creator_administrator/doc'))
        self.reportaBugAction.triggered.connect(partial(self.openWebPage, 'https://github.com/GijsGroote/creator_administrator/issues'))
        self.actionAbout.triggered.connect(self.openAboutDialog)


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


    def openAboutDialog(self):
        ''' Open About Dialog. '''
        AboutDialog(self, self.gv).exec()

    def openWebPage(self, url: str):
        ''' Open web page in default browser. '''
        webbrowser.open(url)


