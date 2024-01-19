import sys
from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

if sys.platform == 'win32':
    import win32com.client
    import pythoncom


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
        super().__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        data = self.fn(*self.args, **self.kwargs)
        self.signals.result.emit(data)
        self.signals.finished.emit()



# class MailWorker(QRunnable):
#     '''

#     '''

#     def __init__(self, fn, marshalled_outlook, *args, **kwargs):
#         super().__init__()
#         # Store constructor arguments (re-used for processing)
#         self.fn = fn
#         self.marshalled_outlook = marshalled_outlook
#         self.args = args
#         self.kwargs = kwargs
#         self.signals = WorkerSignals()

#     @pyqtSlot()
#     def run(self):
#         '''
#         Initialise the runner function with passed args, kwargs.
#         '''

#         pythoncom.CoInitialize ()

#         outlook = win32com.client.Dispatch (
#             pythoncom.CoGetInterfaceAndReleaseStream (
#                 self.marshalled_outlook, 
#                 pythoncom.IID_IDispatch
#             )
#         )
        
#         print("worker Threaded LocationURL:", outlook)

#         print("worker Threaded marshalled LocationURL:", self.marshalled_outlook)


#         data = self.fn(*self.args, **self.kwargs)
#         self.signals.result.emit(data)
#         self.signals.finished.emit()

#         pythoncom.CoUninitialize ()

class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
