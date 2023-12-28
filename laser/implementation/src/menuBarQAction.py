
from PyQt5.QtWidgets import QAction

class ActionSelectFile(QAction):

    def __init__(self, *args, **kwargs):
        QAction.__init__(self, *args, **kwargs)

        self.ActionSelectFile.connect(clicked)

    def clicked(self):
        print('please select a file now')





