from PyQt5.QtWidgets import QTabWidget

from PyQt5.uic import loadUi
from global_variables import gv


class JobsQTabWidget(QTabWidget):

    def __init__(self, parent, ui_global_path):
        super().__init__(parent)

        loadUi(ui_global_path, self)


