# from PyQt5 import Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class LoadingQDialog(QDialog):

    def __init__(self):
        QWidget.__init__(self)

        self.setFixedSize(200, 200)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.CustomizeWindowHint)
        self.label_animation = QLabel(self)
        self.movie = QMovie('/home/gijs/loader.gif')
        self.label_animation.setMovie(self.movie)
        self.timer=QTimer(self)

        layout = QVBoxLayout()
        layout.addWidget(self.label_animation)

        # Set the layout for the dialog
        self.setLayout(layout)
        self.setWindowTitle('GIF Dialog')
        self.setGeometry(300, 300, 500, 500)
        self.setFixedSize(500, 500)  # Fix the size of the dialog



    def startAnimation(self):

        self.show()
        self.timer.singleShot(10000, self.stopAnimation)
        print(f"started the animationnnn")
        print(f"started the animationnnnNNNN")
        self.movie.start()
        print(f"started the animationnnnNNNNNNNNN")

    def stopAnimation(self):

        print(f"stopped the animationNN")
        self.movie.stop()
        self.close()

