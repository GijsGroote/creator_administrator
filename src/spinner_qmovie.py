

import sys 
from PyQt5 import QtCore, QtGui, QtWidgets 
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QMovie 
from PyQt5.QtCore import Qt 

class LoadingGif():

    def __init__(self, parent, *args, **kwargs):
        # Label Create 
        self.label = QLabel(parent) 
        self.label.setGeometry(QtCore.QRect(25, 25, 200, 200)) 
        self.label.setMinimumSize(QtCore.QSize(250, 250)) 
        self.label.setMaximumSize(QtCore.QSize(250, 250)) 
        self.label.setObjectName("lb1") 
        # FrontWindow.setCentralWidget(parent) 

        # Loading the GIF 
        self.movie = QMovie("loader.gif") 
        self.label.setMovie(self.movie) 

        self.startAnimation() 

    # Start Animation 
    def startAnimation(self): 
        print('start animation')
        self.movie.start() 

    # Stop Animation(According to need) 
    def stopAnimation(self): 
        self.movie.stop() 
