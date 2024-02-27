import abc

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut, QFont
from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QLabel

from src.directory_functions import open_file, open_folder

class OverviewQListWidget(QListWidget):
    ''' Overview of multiple items in a list. In most subclasses
    these items are job folders. '''

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # shortcut on the Enter key
        QShortcut(QKeySequence(Qt.Key.Key_Return), self).activated.connect(self.itemEnterPressed)

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
        self.addNoItemsLabel()

        if len(item_names) == 0:
            self.parent().no_items_label.show()
        else:
            self.parent().no_items_label.hide()
            
        for item_name in item_names:

            item = QListWidgetItem()
            if isinstance(item_name, tuple):
                (item_data, item_name) = item_name
            else:
                item_data = item_name

            item.setData(1, item_data)
            item.setText(item_name)
            self.addItem(item)
            item.setFont(QFont('Cantarell', 14))

    def addNoItemsLabel(self):
        ''' Add no_items_label if it is not yet present. '''
        if not hasattr(self.parent(), 'no_items_label'):
            self.parent().no_items_label = QLabel(text='No Jobs to Display',
                                    parent=self.parent())
            self.parent().no_items_label.setGeometry(
                (self.parent().geometry().width()-self.parent().no_items_label.geometry().width())//2, 
                (self.parent().geometry().height()-self.parent().no_items_label.geometry().width())//2,
                300, 20) 

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

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.current_item_name = None


        # shortcut for the Enter button
        QShortcut(QKeySequence(Qt.Key.Key_Return), self).activated.connect(self.itemEnterPressed)
        self.itemDoubleClicked.connect(self.fileDoubleClicked)

    def refresh(self):
        if self.current_item_name is not None:
            self.clear()
            self.loadContent(self.current_item_name)

    def itemEnterPressed(self):
        current_file = self.currentItem()
        
        if current_file is not None:
            self.fileDoubleClicked(current_file)

    def fileDoubleClicked(self, clicked_file):
        ''' Double click on a file (or item) to open it. '''
        open_file(clicked_file.data(1))

    @abc.abstractmethod
    def loadContent(self, item_name):
        ''' load the content. '''
