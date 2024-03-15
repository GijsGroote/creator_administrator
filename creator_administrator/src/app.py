import webbrowser
from functools import partial
import qdarktheme

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QShortcut, QKeySequence 
from PyQt6.QtWidgets import QMainWindow, QListWidget, QStackedWidget
from PyQt6.uic import loadUi

from src.qdialog import AboutDialog

class MainWindow(QMainWindow):

    def __init__(self, ui_global_path: str, gv: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        loadUi(ui_global_path, self)
        if gv['DARK_THEME']:
            qdarktheme.setup_theme()
            self.setStyleSheet("""QToolTip { 
                           background-color: black; 
                           color: white; 
                           border: black solid 1px
                           }""")
            
        self.gv = gv


        self.openDocumentationAction.triggered.connect(partial(webbrowser.open, 'https://github.com/GijsGroote/creator_administrator/tree/main/creator_administrator/doc'))

        self.reportaBugAction.triggered.connect(partial(webbrowser.open, 'https://github.com/GijsGroote/creator_administrator/issues'))
        self.actionAbout.triggered.connect(self.openAboutDialog)


        # shortcut to close the application
        QShortcut(QKeySequence("Ctrl+Q"), self).activated.connect(self.close)

    

    def keyPressEvent(self, event):
        ''' Handle shortcuts on main window. '''

        # go through GUI structure to call the itemEnterPressed
        # function the currenlty displayed item
        if event.key() == Qt.Key.Key_Return:
                self.jobsQTabWidget.currentWidget().findChild(QStackedWidget).currentWidget().findChild(QListWidget).itemEnterPressed()


    def openAboutDialog(self):
        ''' Open About Dialog. '''
        AboutDialog(self, self.gv).exec()
