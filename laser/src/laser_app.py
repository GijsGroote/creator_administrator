import sys
import os
from PyQt5 import QtWidgets
from PyQt5 import QtCore

from qgis.core import QgsApplication
from qgis.gui import QgsMessageBar


from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from global_variables import gv
from src.app import MainWindow
from laser_qdialog import LaserImportFromMailQDialog, LaserSelectFileQDialog
from src.qmessagebox import TimedQMessageBox

from src.mail_manager import MailManager

# class Worker(QObject):
#     done = pyqtSignal(list)

#     def __init__(self, parent=None):
#         super().__init__(parent)

#     def doWork(self):
#         print("Start")
#         time.sleep(10)
#         self.done.emit(['one', 'two', 'three'])
#         print("done")

# class loaderDialog(QWidget):
#     def __init__(self, parent=None):
#         super(loaderDialog, self).__init__(parent)
#         self.initUI()
#         self.thread = QThread(self)
#         self.worker = Worker()
#         self.worker.moveToThread(self.thread) # worker will be runned in another thread
#         self.worker.done.connect(self.load_data_to_tree) # Call load_data_to_tree when worker.done is emitted
#         self.thread.started.connect(self.worker.doWork) # Call worker.doWork when the thread starts
#         self.thread.start() # Start the thread (and run doWork)

# class Spinner(QWidget):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         # self.setAlignment(QtCore.Qt.AlignCenter)
#         self.pixmap = QPixmap('loading.png')
#         self.setStyleSheet("background-color: yellow;") 

#         self.setFixedSize(30, 30)
#         self._angle = 0

#         self.animation = QPropertyAnimation(self, b"angle", self)
#         self.animation.setStartValue(0)
#         self.animation.setEndValue(360)
#         self.animation.setLoopCount(-1)
#         self.animation.setDuration(2000)
#         self.animation.start()


#     def angle(self):
#         return self._angle

#     def angle(self, value):
#         self._angle = value
#         self.update()


#     def paintEvent(self, ev=None):
#         painter = QPainter(self)
#         painter.translate(15, 15)
#         painter.rotate(self._angle)
#         painter.translate(-15, -15)
#         painter.drawPixmap(5, 5, self.pixmap)

class LaserMainWindow(MainWindow):
    def __init__(self, *args, **kwargs):
        ui_global_path = os.path.join(gv['UI_DIR_HOME'], 'laser_main_window.ui')
        MainWindow.__init__(self, ui_global_path, *args, **kwargs)

        self.messageBar = QgsMessageBar()
        self.messageBar.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)


        # menu bar actions
        self.ActionImportFromMail.triggered.connect(self.onActionImportFromMail)
        self.ActionSelectFile.triggered.connect(self.onActionSelectFileclicked)


        QShortcut(QKeySequence('m'), self).activated.connect(self.showMessage)


    def showMessage(self):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setText("Some message")
        msg.setModal(True)
        msg.show()
        # msg = QMessageBox(self, text='some stuppp')
        # msg.setIcon(QMessageBox.Warning)
        # msg.setModal(False)
        # msg.show()
        # msg = TimedQMessageBox(parent=self, text='Mail versturd')


    def onActionImportFromMail(self):


        valid_msgs = self.getNewValidMails()

        if len(valid_msgs) == 0:
            print(f"ha no valid mails, no pupup")
        else:

            dialog = LaserImportFromMailQDialog(self, valid_msgs)

            if dialog.exec_() == QDialog.Accepted:
                pass
                # folder_global_path = dialog.selectFolderButton.folder_global_path
                # project_name = dialog.ProjectNameQLineEdit.text()
                # create_laser_jobs(folder_global_path, project_name)

                # refresh all laser job tabs
                qlist_widgets = self.findChildren(QListWidget)
                for list_widget in qlist_widgets:
                    list_widget.refresh()


    def onActionSelectFileclicked(self):
        dialog = LaserSelectFileQDialog(self)

        if dialog.exec_() == QDialog.Accepted:
            folder_global_path = dialog.selectFolderButton.folder_global_path
            project_name = dialog.ProjectNameQLineEdit.text()
            # TODO: open dialog to collect material, thickness and amount per dxf
            # create_laser_jobs(folder_global_path, project_name)

            # refresh all laser job tabs
            qlist_widgets = self.findChildren(QListWidget)
            for list_widget in qlist_widgets:
                list_widget.refresh()

    def getNewValidMails(self):
        ''' Return new valid mails. '''

        print('searching for new mail...')
        self.mail_manager = MailManager(gv)
        # read unread mails and convert to the email format and mark them as read
        msgs = self.mail_manager.getNewEmails()

        valid_msgs = [msg for msg in msgs if self.mail_manager.isMailAValidJobRequest(msg)]

        if len(msgs) > len(valid_msgs):
            print(f'{len(msgs)-len(valid_msgs)} invalid messages detected, respond to them manually.')

        return valid_msgs

    
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    laser_window = LaserMainWindow()
    laser_window.show()
    app.exec_()
