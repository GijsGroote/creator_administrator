import sys
from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import traceback
from src.qmessagebox import InfoQMessageBox, WarningQMessageBox, ErrorQMessageBox, TimedMessage


class MailWorker():
    ''' 
    Worker specific for threaded mail operations such 
    as sending mail, retrieving mail, or moving mail to a seperate folder. 
    '''

    def __init__(self, fn_name: str, parent_widget, gv:dict, *args, **kwargs):

        if fn_name == 'SEND_CONFIRMATION_MAIL':
            self.fn = self.sendConfirmationMail
        else:
            raise ValueError(f'no function defined for {fn_name}')

        self.gv=gv
        self.thread_pool = gv['THREAD_POOL']
        self.parent_widget = parent_widget
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.worker = None

    def start(self):
        ''' start thread. '''
        if self.worker is None:
            raise ValueError('self.fn not initialised')
        self.thread_pool.start(self.worker)

    def sendConfirmationMail(self,
                             success_message: str,
                             error_message: str,
                             job_folder_global_path: str,
                             template_content: dict,
                             msg):
        """ Send a confirmation mail. """
        self.success_message = success_message
        self.error_message = error_message

        self.worker = Worker(self.sendConfirmationMail, gv=self.gv,
                                    job_folder_global_path=job_folder_global_path,
                                    template_content=template_content,
                                    msg=msg)

        # self.signals.finished.connect(self.confirmationMailSendMessage)
        self.worker.signals.result.connect(self.confirmationMailSendMessage)
        self.worker.signals.error.connect(self.handleMailError)

    def confirmationMailSendMessage(self, data):
        ''' Display a confirmation message to the user. '''
        TimedMessage(self.gv, parent=self.parent_widget, text=f'Confimation mail send to {data}')

    def handleMailError(self, exc: Exception):
        ''' Handle the mail Error. '''
        assert isinstance(exc, Exception), f'Expected type Exception, received type: {type(exc)}'

        if isinstance(exc, ConnectionError):
            ErrorQMessageBox(self.parent_widget, text=f'Connection Error {self.error_message}: {str(exc)}')
        else:
            ErrorQMessageBox(self.parent_widget, text=f'Error Occured: {str(exc)}')



class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        self.worker = Worker(fn, *args, **kwargs)


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        Exception

    result
        object data returned from processing, anything

    '''
    finished = pyqtSignal()
    error = pyqtSignal(Exception)
    result = pyqtSignal(object)
