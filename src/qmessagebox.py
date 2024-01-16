from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from src.worker import Worker

class Dialog2(QDialog):

    def __init__(self, parent, text='sometext'):
        QDialog.__init__(self, parent)

        self.setModal(0)
        self.label = QLabel(text, self)
        self.timeout = 3
        self.timer = QTimer(self)
        self.timer.setInterval(1000*self.timeout)
        self.timer.start()
        print(f"tart timer!")   
        self.timer.timeout.connect(self.exit)

        # b1 = QPushButton("ok", self)
        # b1.move(50, 50)
        # b1.clicked.connect(self.exit)
        self.setWindowTitle("Nonmodal Dialog")
        self.show()

        print(f"is partent active window {parent.isActiveWindow()} and self. {self.isActiveWindow()}")

        # parent.activateWindow()

# self.setFocus()


    def exit(self):
        print(f"exit klicked")  
        self.deleteLater() 
        self.close()

class TimedQMessageBox(QMessageBox):

    def __init__(self, parent=None, text='setthis', icon=QMessageBox.Information, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.setText(text)
        self.timeout = 5
        self.timer = QTimer(self)
        self.timer.setInterval(1000*self.timeout)
        self.timer.start()
        self.timer.timeout.connect(self.accept)
        self.setModal(0)
        # self.setWindowModality(Qt.NonModal)

        self.setIcon(icon)

        # self.show() # needed to move to top right
        print(f"show the dialog now~!")
        self.show()
        self.exec_()


        # message_worker = Worker(self.exec_)

        # parent.threadpool.start(message_worker)


    def moveToTopRightCorner(self, parent):
        parent_geometry = parent.geometry()
        parent_right_x = parent_geometry.x() + parent_geometry.width()
        parent_top_y = parent_geometry.y()
        margin = 0

        self.move(parent_right_x-self.geometry().width()-30-margin, parent_top_y+38+margin)

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

