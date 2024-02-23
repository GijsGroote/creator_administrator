from PyQt6 import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from src.qmessagebox import InfoQMessageBox, WarningQMessageBox, ErrorQMessageBox, TimedMessage
from src.worker import Worker, WorkerSignals
from src.mail_manager import MailManager
from src.loading_dialog import LoadingQDialog
from src.job_tracker import JobTracker



class ThreadedMailManager():
    ''' 
    Worker specific for threaded mail operations such 
    as sending mail, retrieving mail, or moving mail to a seperate folder. 
    '''

    def __init__(self, parent_widget, gv: dict, dialog=None):
        self.gv=gv
        self.thread_pool = gv['THREAD_POOL']
        self.parent_widget = parent_widget
        self.dialog = dialog # dialog to open with data retrieved on another thread
        self.worker = None

    def getValidMailsFromInbox(self):
        ''' Get mails from inbox.

        show loading screen on main thread, 
        get mails on a seperate thread
        remove loading screen and handle incoming mails.
        '''
        self.success_message = None
        self.error_message = ''

        self.loading_dialog = LoadingQDialog(self.parent_widget, self.gv)
        self.loading_dialog.show()
        
        get_mail_worker = Worker(self.getNewMails)
        get_mail_worker.signals.finished.connect(self.loading_dialog.accept)

        get_mail_worker.signals.error.connect(self.loading_dialog.accept)
        get_mail_worker.signals.error.connect(self.handleMailError)
        get_mail_worker.signals.result.connect(self.openImportFromMailDialog)
        self.thread_pool.start(get_mail_worker)

    def getNewMails(self):
        return MailManager(self.gv).getNewValidMails()
    
    def openImportFromMailDialog(self, data):
        ''' open import from mail dialog. '''

        valid_msgs, warnings = data

        if len(warnings) != 0:
            for warning in warnings:
                WarningQMessageBox(self.gv, self.parent_widget, text=warning)

        if len(valid_msgs) == 0:
            InfoQMessageBox(parent=self.parent_widget, text='No new valid job request in mail inbox')

        else:
            self.dialog(self.parent_widget, valid_msgs).exec()
            self.parent_widget.refreshAllWidgets()

            

    def handleMailError(self, exc: Exception):
        ''' Handle the mail error. '''
        assert isinstance(exc, Exception), f'Expected type Exception, received type: {type(exc)}'

        if isinstance(exc, ConnectionError):
            ErrorQMessageBox(self,
                    text=f'Error: {str(exc)}')
        else:
            ErrorQMessageBox(self, text=f'Error Occured: {str(exc)}')

    ''' below this point functions: Start <mail_type> MailWorker.

        The following mail types exist:
        - Recieved, informing the sender that the request was succesfully receieved
        - Unclear, asking the sender for more information because the request is unclear
        - Finished, asking the sender to pick up the request
        - Declined, informing the sender that his request is declinded

    These MailWorker functions use the send <mail_type> Mail functions
    '''

    def startMailWorker(self,
                        success_message: str,
                        error_message: str,
                        mail_type: str,
                        mail_item,
                        template_content: dict,
                        sender_mail_adress=None,
                        sender_mail_receive_time=None):

        self.success_message = success_message
        self.error_message = error_message
        self.sender_mail_adress = sender_mail_adress
        self.sender_mail_receive_time = sender_mail_receive_time

        if mail_type == 'RECEIVED':
            mail_function = self.sendReceivedMail
        elif mail_type == 'UNCLEAR':
            mail_function = self.sendUnclearMail
        elif mail_type == 'FINISHED':
            mail_function = self.sendFinishedMail
        elif mail_type == 'DECLINED':
            mail_function = self.sendDeclinedMail
        else:
            raise ValueError(f'unknown mail_type: {mail_type}')


        if self.gv['SEND_MAILS_ON_SEPERATE_THREAD']: 

            self.worker = Worker(mail_function,
                                 mail_item=mail_item,
                                 template_content=template_content)

            self.worker.signals.finished.connect(self.displaySuccessMessage)
            self.worker.signals.error.connect(self.handleMailError)

            self.thread_pool.start(self.worker)

        else:
            try:
                mail_function(mail_item=mail_item,
                          template_content=template_content)
                self.displaySuccessMessage()

            except Exception as exc:
                self.handleMailError(exc)

    def startDeclinedMailWorker(self,
                            success_message: str,
                            error_message: str,
                            mail_item: str):        

        # TODO: make this threaded or not threaded.
        self.success_message = success_message
        self.error_message = error_message

        self.loading_dialog = LoadingQDialog(self.parent_widget.parent().parent().parent().parent().parent(), 
                                             self.gv, 
                                             text='Send the Outlook popup reply, it can be behind other windows')
        
        self.loading_dialog.show()
        self.worker = Worker(self.sendDeclinedMail, 
                             mail_item=mail_item,
                             template_content={})

        self.worker.signals.finished.connect(self.loading_dialog.accept)
        self.worker.signals.finished.connect(self.displaySuccessMessage)
        self.worker.signals.error.connect(self.loading_dialog.accept)
        self.worker.signals.error.connect(self.handleMailError)
        self.thread_pool.start(self.worker)

    def sendReceivedMail(self,
                        mail_item,
                        template_content: dict):
        """ Send a confirmation mail. """

        # The MailManager object must be made in the scope of this function. 
        # otherwise Outlook raises an attribute error for an open share com object
        mail_manager = MailManager(self.gv)
        mail_manager.replyToEmailFromFileUsingTemplate(
                                mail_item=mail_item,
                                template_file_name="RECEIVED_MAIL_TEMPLATE",
                                template_content=template_content,
                                popup_reply=False)

        job_tracker = JobTracker(self.gv, self.parent_widget)


        mail_manager.moveEmailToVerwerktFolder(sender_mail_adress=self.sender_mail_adress,
                                               sender_mail_receive_time=self.sender_mail_receive_time)


    def sendUnclearMail(self,
                        mail_item,
                        template_content: dict):

        # The MailManager object must be made in the scope of this function. 
        # otherwise Outlook raises an attribute error for an open share com object
        mail_manager = MailManager(self.gv)
        mail_manager.replyToEmailFromFileUsingTemplate(
                                mail_item=mail_item,
                                template_file_name="UNCLEAR_MAIL_TEMPLATE",
                                template_content=template_content,
                                popup_reply=False)
        mail_manager.moveEmailToVerwerktFolder(sender_mail_adress=self.sender_mail_adress,
                                               sender_mail_receive_time=self.sender_mail_receive_time)

    def sendFinishedMail(self,
                        mail_item: str,
                        template_content: dict):
        """ Send a job is finished mail. """
        
        # The MailManager object must be made in the scope of this function. 
        # otherwise Outlook raises an attribute error for an open share com object
        MailManager(self.gv).replyToEmailFromFileUsingTemplate(
                                mail_item=mail_item,
                                template_file_name="FINISHED_MAIL_TEMPLATE",
                                template_content=template_content,
                                popup_reply=False)
        

    def sendDeclinedMail(self,
                        mail_item,
                        template_content: dict):
        """ Send a declined mail. """
        
        # The MailManager object must be made in the scope of this function. 
        # otherwise Outlook raises an attribute error for an open share com object
        MailManager(self.gv).replyToEmailFromFileUsingTemplate(
                                mail_item=mail_item,
                                template_file_name="DECLINED_MAIL_TEMPLATE",
                                template_content=template_content,
                                popup_reply=True)

    def displaySuccessMessage(self):
        ''' Display a confirmation message to the user. '''
        if self.success_message is not None:
            TimedMessage(self.gv, parent=self.parent_widget, text=self.success_message)

    def handleMailError(self, exc: Exception):
        ''' Handle the mail Error. '''
        assert isinstance(exc, Exception), f'Expected type Exception, received type: {type(exc)}'
        
        if isinstance(exc, ConnectionError):
            ErrorQMessageBox(self.parent_widget, text=f'Connection Error {self.error_message}: {str(exc)}')
        else:
            ErrorQMessageBox(self.parent_widget, text=f'Error Occured {self.error_message}: {str(exc)}')

