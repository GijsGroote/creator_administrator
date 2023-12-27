
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton

class JumpButton(QPushButton):

    def __init__(self, *args, **kwargs):
        QPushButton.__init__(self, *args, **kwargs)
        self.setStyleSheet('background-color: blue')

        self.clicked.connect(self.clickme)

        self.change_text('in print')

    def change_text(self, new_text: str):
        self.setText(new_text)

    def clickme(self):
        print('button is clicked, in print')
        self.setText('print')

