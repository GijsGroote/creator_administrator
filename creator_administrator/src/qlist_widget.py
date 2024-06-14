import os
import abc
import time
import json
from operator import itemgetter

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QKeySequence, QShortcut, QFont, QDrag, QPixmap, QPainter, QColor
from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QLabel, QWidget, QAbstractItemView, QMenu

from src.directory_functions import open_file
from src.job_tracker import JobTracker
from src.qdialog import QuestionsQDialog

class ContentQListWidgetItem(QListWidgetItem):
    ''' Item to add to QListWidget. '''

    def __init__(self, parent, item_dict: dict, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
            
        assert os.path.exists(item_dict['file_global_path']),\
            f'item global path {item_dict["file_global_path"]} does not exists'


        if 'done' in item_dict:
            if item_dict['done']:
                self.setText('✔️ '+item_dict['file_name'])
            else:
                self.setText('❌ '+item_dict['file_name'])
        else:
            self.setText(item_dict['file_name'])
        
        # TODO: this is not robust to check if the file is a make file
        if 'done' in item_dict:
            self.setData(3, json.dumps(item_dict, indent=4))

        self.setData(1, item_dict['file_global_path'])
        self.setFont(QFont('Cantarell', 14))


class OverviewQListWidget(QListWidget):
    ''' Overview of multiple items/jobs in a list. '''

    def __init__(self, parent, gv: dict, job_tracker: JobTracker, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.gv = gv
        self.job_tracker = job_tracker
        self.last_left_click_time = None 

        # shortcut on the Enter key
        QShortcut(QKeySequence(Qt.Key.Key_Return), self).activated.connect(self.itemEnterPressed)

    # Some child classes overwrite this function
    def displayItem(self, item_name: str):
        ''' Display the job content page. '''

        self.parent().parent().setCurrentIndex(1)
        # find the JobContentQListWidget by searching for QListWidget (search for JobContentQListWidget returns None)
        self.parent().parent().currentWidget().findChild(QListWidget).loadContent(item_name)

    def initialize(self, item_names: list):
        ''' Initialize with list of items. '''
        self.addNoItemsLabel()

        if len(item_names) == 0:
            self.parent().no_items_label.show()
        else:
            self.parent().no_items_label.hide()

        
        item_names = sorted(item_names, key=itemgetter(1))

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
        ''' Handle press on current item. '''
        current_item = self.currentItem()
        if current_item is not None:
            self.displayItem(current_item.data(1))


    def mousePressEvent(self, event):
        ''' Handle single click, dubble click and dragging for the mouse cursor. '''

        if self.itemAt(event.pos()) is None:
            return
        else:
            self.setCurrentItem(self.itemAt(event.pos()))

        if event.button() == Qt.MouseButton.LeftButton:  
            if self.last_left_click_time is None:
                self.last_left_click_time = time.time()

            elif int(time.time() - self.last_left_click_time) < 1:
                self.displayItem(self.currentItem().data(1))
                self.last_left_click_time = time.time()

            else:
                self.last_left_click_time = time.time()

        elif event.button() == Qt.MouseButton.RightButton:  
            self.contextMenuEvent(event)

    def contextMenuEvent(self, event):
        context_menu = QMenu(self)
        change_job_name_action = context_menu.addAction("Change Job Name")
        action = context_menu.exec(self.mapToGlobal(event.pos()))

        if action == change_job_name_action:
            self.change_job_name()


    def change_job_name(self):

        dlg = QuestionsQDialog(self, self.gv,
                           f'Enter new job name for job {self.currentItem().data(1)}')


        if dlg.exec() == 1:
            # update job name
            self.job_tracker.updateJobName(self.currentItem().data(1), 
                self.job_tracker.makeJobNameUnique(str(dlg.answerLineEdit.text())))

        # refresh Jobs
        self.refresh()




    def openItem(self, item):
        ''' Double click on a file (or item) to open it. '''
        assert isinstance(item, QListWidgetItem), f'item should be type QListWidgetItem and is {type(QListWidgetItem)}'
        open_file(item.data(1))

    @abc.abstractmethod
    def refresh(self):
        ''' Initialise the list widget with jobs. '''

class ContentQListWidget(QListWidget):
    ''' Keep content in a list widget. '''

    def __init__(self, parent, gv: dict, job_tracker: JobTracker, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.current_item_name = None
        self.gv = gv
        self.job_tracker = job_tracker
        self.last_left_click_time = None 

        # shortcut for the Enter button
        QShortcut(QKeySequence(Qt.Key.Key_Return), self).activated.connect(self.itemEnterPressed)

    def mousePressEvent(self, event):

        if self.itemAt(event.pos()) is None:
            return
        else:
            self.setCurrentItem(self.itemAt(event.pos()))

        if event.button() == Qt.MouseButton.LeftButton:  
            if self.last_left_click_time is None:
                self.last_left_click_time = time.time()
                self.startDrag(event)

            elif int(time.time() - self.last_left_click_time) < 1:
                self.openItem(self.currentItem())
                self.last_left_click_time = time.time()

            else:
                self.last_left_click_time = time.time()
                self.startDrag(event)


        elif event.button() == Qt.MouseButton.RightButton:  
            self.contextMenuEvent(event)

    def contextMenuEvent(self, event):
        context_menu = QMenu(self)
        file_done_action = context_menu.addAction("Mark file as Done")
        file_not_done_actions = context_menu.addAction("Mark file as not Done")
        action = context_menu.exec(self.mapToGlobal(event.pos()))

        if action == file_done_action:
            self.markFileAsDone()
        elif action == file_not_done_actions:
            self.markFileAsNotDone()

    def markFileAsDone(self):
        self.job_tracker.markFilesAsDone(self.current_item_name, self.currentItem().data(1), True)
        self.refresh()

    def markFileAsNotDone(self):
        self.job_tracker.markFilesAsDone(self.current_item_name, self.currentItem().data(1), False)
        self.refresh()

    def startDrag(self, event):
        ''' Start dragging an item. '''

        drag = QDrag(self)

        self.current_item = self.currentItem()
        
        if self.current_item is None:
            return

        indexes = self.selectedIndexes()

        mime = self.model().mimeData(indexes)
        mime.setUrls([QUrl.fromLocalFile(self.current_item.data(1))])

        label = QLabel(self.current_item.text(), self)
        width = label.fontMetrics().boundingRect(label.text()).width()

        pixmap = QPixmap(width+25, 50)
        
        # Create a QPainter object
        painter = QPainter(pixmap)
        if self.gv['DARK_THEME']:
            pixmap.fill(QColor('black'))
            painter.setPen(QColor('white'))
        else: 
            pixmap.fill()
        
        # Set font properties
        painter.drawText(pixmap.rect(), 0x0080, '   '+self.current_item.text())
        
        # End painting
        painter.end()
            
        drag.setPixmap(pixmap)
        drag.setMimeData(mime)        
        drag.exec(Qt.DropAction.CopyAction)

    def refresh(self):
        if self.current_item_name is not None:
            self.clear()
            self.loadContent(self.current_item_name)

    def itemEnterPressed(self):
        if self.currentItem() is not None:
            self.openItem(self.currentItem())

    def openItem(self, item):
        ''' Double click on a file (or item) to open it. '''
        assert isinstance(item, QListWidgetItem), f'item should be type QListWidgetItem and is {type(QListWidgetItem)}'
        open_file(item.data(1))

    @abc.abstractmethod
    def loadContent(self, item_name):
        ''' load the content. '''

class JobContentQListWidget(ContentQListWidget):

    def __init__(self, parent: QWidget, gv: dict, job_tracker: JobTracker, *args, **kwargs):
        super().__init__(parent, gv, job_tracker, *args, **kwargs)

        self.setDragDropMode(QAbstractItemView.DragDropMode.DragOnly)


    def loadContent(self, item_name):
        self.clear()
        self.current_item_name = item_name

        job_dict = self.job_tracker.getJobDict(item_name)

        if job_dict is not None:
            self.parent().findChild(QLabel).setText(job_dict['dynamic_job_name'])

            for file_name in os.listdir(job_dict['job_folder_global_path']):

                make_file_dict_list = [val for key,val in job_dict['make_files'].items() if file_name in key]
                if len(make_file_dict_list) == 0:
                    item = ContentQListWidgetItem(self, {'file_name': file_name,
                             'file_global_path': os.path.join(job_dict['job_folder_global_path'], file_name)})
                elif len(make_file_dict_list) == 1:
                    item = ContentQListWidgetItem(self, make_file_dict_list[0])
                else:
                    raise ValueError(f'make_file_dict_list should be of length 0 or 1, not {len(make_file_dict_list)}')

                self.addItem(item)



class OptionsQListWidget(QListWidget):
    ''' Content . '''

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

    # Do nothing for options QlistWidget refresh (but is should be callable)
    def refresh(self):
        pass
