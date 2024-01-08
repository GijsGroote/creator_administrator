
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTabWidget, QShortcut, QListWidget, QStackedWidget

from PyQt5.QtGui import QKeySequence

# from laser_qlist_widget import JobsOverviewQListWidget


class JobsQTabWidget(QTabWidget):

    def __init__(self, *args, **kwargs):
        QTabWidget.__init__(self, *args, **kwargs)

        # shortcuts on arrow keys
        QShortcut(QKeySequence(Qt.Key_Left), self).activated.connect(self.toLeftTab)
        QShortcut(QKeySequence(Qt.Key_Right), self).activated.connect(self.toRightTab)
        QShortcut(QKeySequence(Qt.Key_Up), self).activated.connect(self.toPreviousRow)
        QShortcut(QKeySequence(Qt.Key_Down), self).activated.connect(self.toNextRow)

        # shortcuts on VIM motions
        QShortcut(QKeySequence('h'), self).activated.connect(self.toLeftTab)
        QShortcut(QKeySequence('l'), self).activated.connect(self.toRightTab)
        QShortcut(QKeySequence('k'), self).activated.connect(self.toPreviousRow)
        QShortcut(QKeySequence('j'), self).activated.connect(self.toNextRow)

    def toRightTab(self):
        if self.currentIndex() == self.count()-1:
            set_to_index = 0
        else:
            set_to_index = self.currentIndex()+1
        self.setCurrentIndex(set_to_index)

    def toLeftTab(self):
        if self.currentIndex() == 0:
            set_to_index = self.count()-1
        else:
            set_to_index = self.currentIndex()-1
        self.setCurrentIndex(set_to_index)

    def toNextRow(self):
        # from current tab get current page and get the QListWidget from there
        qlist_widget = self.currentWidget().findChild(QStackedWidget).currentWidget().findChild(QListWidget)
        current_row = qlist_widget.currentRow()

        if current_row == qlist_widget.count()-1:
            qlist_widget.setCurrentRow(0)
        else:
            qlist_widget.setCurrentRow(current_row+1)

    def toPreviousRow(self):
        qlist_widget = self.currentWidget().findChild(QStackedWidget).currentWidget().findChild(QListWidget)
        current_row = qlist_widget.currentRow()

        if current_row == 0:
            qlist_widget.setCurrentRow(qlist_widget.count()-1)
        else:
            qlist_widget.setCurrentRow(current_row-1)


