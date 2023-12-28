import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton
from PyQt5.QtGui import QKeyEvent
# from dialog import Ui_Dialog
from PyQt5 import uic
from global_variables import gv

from myWidgets import JumpButton

from app import MainWindow

class PrintMainWindow(MainWindow):

    def __init__(self, *args, **kwargs):
        MainWindow.__init__(self, *args, **kwargs)

        # btn = JumpButton()

        # display_text('hoi ik ben laserMainWIndows')


        # def display_text(self, text):
            # self.testQLabel.set_text(text)


    # def onEmployeeBtnClicked(self):
    #     """Launch the employee dialog."""
    #     dlg = EmployeeDlg(self)
    #     dlg.exec()

# class EmployeeDlg(QDialog):
    # """Employee dialog."""
    # def __init__(self, parent=None):
    #     super().__init__(parent)
    #     # Create an instance of the GUI
    #     self.ui = Ui_Dialog()
    #     # Run the .setupUi() method to show the GUI
    #     self.ui.setupUi(self)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    print_window = PrintMainWindow()
    print_window.show()
    app.exec_()
