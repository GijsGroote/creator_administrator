import os
import abc
from typing import List
import re
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
        QShortcut,
        QListWidget, QPushButton,
        QWidget, QListWidgetItem, QStackedWidget,
        QVBoxLayout, QTabWidget
)


from src.directory_functions import open_file, open_folder

class OverviewQListWidget(QListWidget):
    ''' Overview of multiple items in a list. In most subclasses
    these items are job folders. '''

    def __init__(self, *args, **kwargs):
        QListWidget.__init__(self, *args, **kwargs)

        # TODO: could the shortcuts not be here? somehow materialOverviewQlistWidget then fails
        # QShortcut(QKeySequence(Qt.Key_Return), self).activated.connect(self.itemEnterPressed)

    def refresh(self):
        ''' Refresh displayed items. '''
        self.clear()
        self.initialize(self.getItemNames())

    def storeObjectNameInit(self):
        ''' Store the object name and initialize. '''
        self.object_name = self.objectName()
        self.initialize(self.getItemNames())

    def initialize(self, item_names: list):
        ''' Initialize with list of items. '''

        for item_name in item_names:

            item = QListWidgetItem()
            if isinstance(item_name, tuple):
                (item_data, item_name) = item_name
            else:
                item_data = item_name

            item.setData(1, item_data)
            item.setText(item_name)
            self.addItem(item)
            self.itemClicked.connect(self.itemIsClicked)


    def itemEnterPressed(self):
        current_item = self.currentItem()
        if current_item is not None:
            self.displayItem(current_item.data(1))

    # itemClicked is already a function, name it itemIsClicked
    def itemIsClicked(self, clicked_item):
        ''' Display the content of the item clicked. '''
        self.displayItem(clicked_item.data(1))

    @abc.abstractmethod
    def getItemNames(self):
        ''' Return a list of names or tuples. '''

    @abc.abstractmethod
    def displayItem(self, item_name: str):
        ''' Display the item page and load its content for the highlighted job. '''

class ContentQListWidget(QListWidget):

    def __init__(self, *args, **kwargs):
        QListWidget.__init__(self, *args, **kwargs)
        self.current_item_name = None


        # shortcut for the Enter button
        QShortcut(QKeySequence(Qt.Key_Return), self).activated.connect(self.fileEnterPressed)
        

    def refresh(self):
        if self.current_item_name is not None:
            self.clear()
            self.loadContent(self.current_item_name)

    def fileEnterPressed(self):
        current_file = self.currentItem()
        
        if current_file is not None:
            self.fileClicked(current_file)

    def fileClicked(self, clicked_file):
        open_file(clicked_file.data(1))

    @abc.abstractmethod
    def loadContent(self, item_name):
        ''' load the content. '''
