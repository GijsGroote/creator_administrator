from functools import partial

from src.qmessagebox import InfoQMessageBox, WarningQMessageBox, ErrorQMessageBox, TimedMessage
from src.worker import Worker
from src.mail_manager import MailManager
from src.loading_dialog import LoadingQDialog
from src.job_tracker import JobTracker

class ThreadedMailManager():
    ''' 
    Worker specific for threaded mail operations such 
    as sending mail, retrieving mail, or moving mail to a seperate folder. 
    '''

    def __init__(self, parent, gv: dict, dialog=None):
        self.gv = gv
        self.thread_pool = gv['THREAD_POOL']
        self.parent = parent
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

        self.loading_dialog = LoadingQDialog(self.parent, self.gv)
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
                WarningQMessageBox(self.parent, self.gv, text=warning)

        if len(valid_msgs) == 0:
            InfoQMessageBox(parent=self.parent, text='No new valid job request in mail inbox')

        else:
            self.dialog(parent=self.parent, valid_msgs=valid_msgs).exec()
            self.parent.refreshAllWidgets()

            
     # below this point functions: Start <mail_type> MailWorker.

     #    The following mail types exist:
     #    - Recieved, informing the sender that the request was succesfully receieved
     #    - Unclear, asking the sender for more information because the request is unclear
     #    - Finished, asking the sender to pick up the request
     #    - Declined, informing the sender that his request is declinded

    # These MailWorker functions use the send <mail_type> Mail functions
    
    def startMailWorkerFromJobDict(self, job_dict: dict, mail_type: str):
        ''' Start a mail worker from only a job dictionary. '''

        mail_item=MailManager(self.gv).getMailGlobalPathFromFolder(job_dict['job_folder_global_path'])

        if mail_type=='RECEIVED':
            template_content=JobTracker(parent=self.parent, gv=self.gv).getNumberOfJobsWithStatus(['WACHTRIJ'])

        else:
            template_content={}

        if 'sender_mail_adress' in job_dict:
            sender_mail_adress=job_dict['sender_mail_adress']
        else:
            sender_mail_adress=None

        if 'sender_mail_receive_time' in job_dict:
            sender_mail_receive_time=job_dict['sender_mail_receive_time']
        else:
            sender_mail_receive_time=None

        self.startMailWorker(
                sender_name=job_dict['sender_name'],
                mail_type=mail_type,
                mail_item=mail_item,
                template_content=template_content,
                sender_mail_adress=sender_mail_adress,
                sender_mail_receive_time=sender_mail_receive_time)

    def startMailWorker(self,
                        sender_name: str,
                        mail_type: str,
                        mail_item,
                        move_mail_to_verwerkt=False,
                        template_content=None,
                        sender_mail_adress=None,
                        sender_mail_receive_time=None):

        self.sender_mail_adress = sender_mail_adress
        self.sender_mail_receive_time = sender_mail_receive_time

        if mail_type == 'RECEIVED':
            mail_function = self.sendReceivedMail
            mail_type_readable = 'Job Received'

        elif mail_type == 'UNCLEAR':
            mail_function = self.sendUnclearMail
            mail_type_readable = 'Unclear Request'

        elif mail_type == 'FINISHED':
            mail_function = self.sendFinishedMail
            mail_type_readable = 'Job Finished'

        elif mail_type == 'DECLINED':
            mail_function = self.sendDeclinedMail
            mail_type_readable = 'Job Declined'
        else:
            raise ValueError(f'unknown mail_type: {mail_type}')

        self.success_message=f'{mail_type_readable} mail send to {sender_name}'
        self.error_message=f'No {mail_type_readable} mail send to {sender_name}'

        if self.gv['SEND_MAILS_ON_SEPERATE_THREAD']: 

            self.worker = Worker(mail_function,
                                 mail_item=mail_item,
                                 template_content=template_content)

            self.worker.signals.finished.connect(self.displaySuccessMessage)
            self.worker.signals.error.connect(self.handleMailError)

            if move_mail_to_verwerkt:
                self.worker.signals.finished.connect(partial(self.moveMailToVerwerktFolder, mail_item))

            self.thread_pool.start(self.worker)

        else:
            try:
                mail_function(mail_item=mail_item,
                          template_content=template_content)

                if move_mail_to_verwerkt:
                    self.moveMailToVerwerktFolder(mail_item=mail_item)

                self.displaySuccessMessage()

            except Exception as exc:
                self.handleMailError(exc)

    def startDeclinedMailWorker(self,
                            success_message: str,
                            error_message: str,
                            mail_item: str):        

        self.success_message = success_message
        self.error_message = error_message

        self.loading_dialog = LoadingQDialog(self.parent.parent().parent().parent().parent().parent(), 
                                             self.gv, 
                                             text='Send the Outlook popup reply, it can be behind other windows')
        
        self.loading_dialog.show()


        if self.gv['SEND_MAILS_ON_SEPERATE_THREAD']: 
            self.worker = Worker(self.sendDeclinedMail, 
                                 mail_item=mail_item,
                                 template_content={})

            self.worker.signals.finished.connect(self.loading_dialog.accept)
            self.worker.signals.finished.connect(self.displaySuccessMessage)
            self.worker.signals.error.connect(self.loading_dialog.accept)
            self.worker.signals.error.connect(self.handleMailError)
            self.thread_pool.start(self.worker)

        else:
            try:
                self.sendDeclinedMail(mail_item=mail_item,
                                      template_content={})
                self.loading_dialog.accept()
                self.displaySuccessMessage()

            except Exception as exc:
                self.loading_dialog.accept()
                self.handleMailError(exc)


    def sendReceivedMail(self,
                        mail_item,
                        template_content: dict):
        ''' Send a confirmation mail. '''

        # The MailManager object must be made in the scope of this function. 
        # otherwise Outlook raises an attribute error for an open share com object
        mail_manager = MailManager(self.gv)
        mail_manager.replyToEmailFromFileUsingTemplate(
                                mail_item=mail_item,
                                template_file_name='RECEIVED_MAIL_TEMPLATE',
                                template_content=template_content,
                                popup_reply=False)


    def sendUnclearMail(self,
                        mail_item,
                        template_content: dict):

        # The MailManager object must be made in the scope of this function. 
        # otherwise Outlook raises an attribute error for an open share com object
        mail_manager = MailManager(self.gv)
        mail_manager.replyToEmailFromFileUsingTemplate(
                                mail_item=mail_item,
                                template_file_name='UNCLEAR_MAIL_TEMPLATE',
                                template_content=template_content,
                                popup_reply=False)

    def sendFinishedMail(self,
                        mail_item: str,
                        template_content: dict):
        ''' Send a job is finished mail. '''
        
        # The MailManager object must be made in the scope of this function. 
        # otherwise Outlook raises an attribute error for an open share com object
        MailManager(self.gv).replyToEmailFromFileUsingTemplate(
                                mail_item=mail_item,
                                template_file_name='FINISHED_MAIL_TEMPLATE',
                                template_content=template_content,
                                popup_reply=False)
        

    def sendDeclinedMail(self,
                        mail_item,
                        template_content: dict):
        ''' Send a declined mail. '''
        
        # The MailManager object must be made in the scope of this function. 
        # otherwise Outlook raises an attribute error for an open share com object
        MailManager(self.gv).replyToEmailFromFileUsingTemplate(
                                mail_item=mail_item,
                                template_file_name='DECLINED_MAIL_TEMPLATE',
                                template_content=template_content,
                                popup_reply=True)

    def moveMailToVerwerktFolder(self, mail_item):
        ''' Move mail_item to the Verwerkt folder. '''
        MailManager(self.gv).moveEmailToVerwerktFolder(
                                mail_item=mail_item,
                                sender_mail_adress=self.sender_mail_adress,
                                sender_mail_receive_time=self.sender_mail_receive_time)

    def displaySuccessMessage(self):
        ''' Display a confirmation message to the user. '''
        if self.success_message is not None:
            TimedMessage(self.parent, self.gv, self.success_message)

    def handleMailError(self, exc: Exception):
        ''' Handle the mail Error. '''
        assert isinstance(exc, Exception), f'Expected type Exception, received type: {type(exc)}'

        # raise exc
        if isinstance(exc, ConnectionError):
            ErrorQMessageBox(
                    self.parent,
                    text=f'Connection Error {self.error_message}: {str(exc)}')
        else:
            ErrorQMessageBox(
                    self.parent,
                    text=f'Error Occured {self.error_message}: {str(exc)}')
