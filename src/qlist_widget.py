import os
import abc
from typing import List
import re
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore

FullPathRole = Qt.UserRole + 1



from src.directory_functions import open_file, open_folder

class OverviewQListWidget(QListWidget):
    ''' Overview of multiple items in a list. In most subclasses
    these items are job folders. '''

    def __init__(self, *args, **kwargs):
        QListWidget.__init__(self, *args, **kwargs)

        # shortcut on the Enter key
        QShortcut(QKeySequence(Qt.Key_Return), self).activated.connect(self.itemEnterPressed)

        self.itemDoubleClicked.connect(self.itemIsDoubleClicked)

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


    def itemEnterPressed(self):
        current_item = self.currentItem()
        if current_item is not None:
            self.displayItem(current_item.data(1))

    # itemDoubleClicked already defined, call it itemIsDoubleClicked
    def itemIsDoubleClicked(self, clicked_item):
        ''' Display the content of the item clicked. '''
        self.displayItem(clicked_item.data(1))

    @abc.abstractmethod
    def getItemNames(self) -> list:
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

        self.setDragEnabled(True)
        self.itemDoubleClicked.connect(self.fileDoubleClicked)
        # self.itemPressed.connect(self.startDrag)
        # self.itemEntered.connect(self.on_item_entered)
        # self.itemMoved.connect(self.on_item_moved)
        # self.itemDropped.connect(self.on_item_dropped)

    def startDrag(self, actions):
        drag = QDrag(self)
        indexes = self.selectedIndexes()
        mime = self.model().mimeData(indexes)
        urlList = []
        for index in indexes:
            urlList.append(QUrl.fromLocalFile(index.data()))
        mime.setUrls(urlList)

        print(f"start dragging this {urlList}")
        drag.setMimeData(mime)
        drag.exec_(actions)

    def dropEvent(self, e):
        if e.mimeData().hasUrls():
            e.setDropAction(Qt.CopyAction)
            e.accept()
            fpath_list = []
            for url in e.mimeData().urls():
                fpath_list.append(str(url.toLocalFile()))
            print(f"the list of paths {fpath_list}")

            for fpath in fpath_list:
                print(f'IMPORT {fpath}')
                fileName = QFileInfo(fpath).fileName()
                item = QListWidgetItem(fileName)
                item.setData(FullPathRole, fpath)
                self.addItem(fpath)
            print(f"done somehow")

    # def startDrag(self, file):

    #     if file:
    #         mime_data = QMimeData()
    #         file_path = file.data(1)
    #         print(f"the file path is  {file_path}")
    #         mime_data.setUrls([QUrl.fromLocalFile(file_path)])

    #         drag = QDrag(self)
    #         drag.setMimeData(mime_data)

    #         # Start the drag operation
    #         drag.exec_()


    # def dragEnterEvent(self, event):
    #     if event.mimeData().hasUrls():
    #         event.accept()
    #     else:
    #         event.ignore()


    # def dropEvent(self, event):
    #     urls = [url for url in event.mimeData().urls()]

    #     for url in urls:
    #         print(f"the entire thing {url}")
    #         print(url.toString())
    #         print(url.toLocalFile())


    # def dropEventtt(self, e):
    #     if e.mimeData().hasUrls():
    #         e.setDropAction(Qt.CopyAction)
    #         e.accept()
    #         fpath_list = []
    #         for url in e.mimeData().urls():
    #             fpath_list.append(str(url.toLocalFile()))

    #         for fpath in fpath_list:
    #             print(f'IMPORT {fpath}')
    #             fileName = QFileInfo(fpath).fileName()
    #             item = QListWidgetItem(fileName)
    #             item.setData(FullPathRole, fpath)
    #             self.addItem(fpath)

    def refresh(self):
        if self.current_item_name is not None:
            self.clear()
            self.loadContent(self.current_item_name)

    def fileEnterPressed(self):
        current_file = self.currentItem()
        
        if current_file is not None:
            self.fileDoubleClicked(current_file)

    def fileDoubleClicked(self, clicked_file):
        ''' Double click on a file (or item) to open it. '''
        open_file(clicked_file.data(1))

    @abc.abstractmethod
    def loadContent(self, item_name):
        ''' load the content. '''
