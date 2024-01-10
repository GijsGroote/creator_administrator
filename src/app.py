import os
from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic

class MainWindow(QMainWindow):

    def __init__(self, ui_global_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(ui_global_path, self)
        self.threadpool = QThreadPool() # the one and only threadpool


        # job_name = 'haha'

        # message_worker = Worker(TimedQMessageBox,
        #                         text=f"Job finished mail send to {job_name}",
        #                         parent=self)
        # self.threadpool.start(message_worker)

        # TODO: save height and widtt and position when closing, use that when opening
        # desktop_center = QApplication.desktop().availableGeometry().center()
        # self.move(desktop_center.x() - int(self.width()*0.5), desktop_center.y() - int(self.height()*0.5))

    def keyPressEvent(self, event):
        ''' Handle shortcuts on main window. '''

        # close application on 'q' press
        if isinstance(event, QKeyEvent):
            if event.key() == Qt.Key_Q:
                self.close()

def get_thread_pool(widget) -> QThreadPool:
    ''' Return the thread pool. '''
    main_window = get_main_window(widget)
    if main_window is not None:
        return main_window.threadpool

    raise ValueError(f'Could not find QMainWindow.threadpool from object with type {type(main_window)}')

def get_main_window(widget):
    """
    Traverses the parent hierarchy of a widget to find the main window.
    
    :param widget: The starting widget (child)
    :return: The found QMainWindow instance or None
    """
    current_widget = widget
    while current_widget is not None:
        if isinstance(current_widget, MainWindow):
            return current_widget
        current_widget = current_widget.parent()

    raise ValueError(f'Could not find QMainWindow as parent from {widget.objectName()} of type {type(widget)}')
