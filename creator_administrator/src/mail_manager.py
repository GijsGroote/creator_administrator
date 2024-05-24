'''

Handle mail functionality.

mail_item: openen .msg file or .eml file, or a string (directory path, dir containing .msg or .eml, or full path toward .msg or .eml)

'''

import os
import sys
import re
import shutil
import time
import http.client as httplib
from unidecode import unidecode

from src.directory_functions import  delete_directory_content

if sys.platform == 'linux':
    import imaplib
    import email
    import smtplib
    import ssl
    from email.header import decode_header
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.utils import parseaddr, formataddr
    from email.policy import default

elif sys.platform == 'win32':
    from pywintypes import com_error
    from win32com import client
else:
    raise ValueError(f'This software does not work for platform: {sys.platform}')

class MailManager():

    def __init__(self, gv: dict):
        self.gv = gv

        if sys.platform == 'win32':

            self.outlook =  client.Dispatch("Outlook.Application").GetNamespace('MAPI') # pylint: disable=used-before-assignment

            if 'MAIL_ADRESS' in gv.keys():
                mail_adress = gv['MAIL_ADRESS']
            else:
                mail_adress = self.outlook.Session.Accounts.Item(1).DeliveryStore.DisplayName
                        

            if gv['MAIL_INBOX_NAME'] == 'Inbox':
                self.inbox = self.outlook.Folders[mail_adress].Folders('Inbox')
            else:
                
                self.inbox = self.outlook.Folders[mail_adress].Folders[gv['MAIL_INBOX_NAME']]

            try:
                self.verwerkt_folder = self.inbox.Parent.Folders.Item("Verwerkt")
            except com_error: # pylint: disable=used-before-assignment
                self.verwerkt_folder = self.inbox.Parent.Folders.Add("Verwerkt")

        if sys.platform == 'linux':
            # specific to gmail and outlook
            self.smtp_server = 'smtp-mail.outlook.com'
            self.smtp_port = 587
            self.imap_server = 'outlook.office365.com'

        # TODO: check folder 'Verwerkt" exists, if not create it.

    def imapLogin(self):
        ''' Login to the IMAP server to download mails. '''
        self.imap_mail = imaplib.IMAP4_SSL(self.imap_server)
        self.imap_mail.login(self.gv['MAIL_ADRESS'], self.gv['MAIL_PASSWORD'])
        self.imap_mail.select(self.gv['MAIL_INBOX_NAME'])

        status, mailboxes = self.imap_mail.list()
        if status == 'OK':
            if not any('Verwerkt' in mbox.decode() for mbox in mailboxes):
                self.imap_mail.create('Verwerkt')

    def imapLogout(self):
        ''' Logout of the IMAP server. '''
        self.imap_mail.close()
        self.imap_mail.logout()


    def getNewValidMails(self) -> tuple[list, list]:
        ''' Return emails from Outlook inbox. '''

        warnings = []

        if not self.isThereInternet():
            warnings.append('No internet connection detected')

        if sys.platform == 'win32':
            n_invalid_mails, valid_msgs, warnings = self.getNewValidMailsWin32(warnings)

        elif sys.platform == 'linux':
            n_invalid_mails, valid_msgs, warnings = self.getNewValidMailsLinux(warnings)

        else:
            raise ValueError(f'software not applicable to platform {sys.platform}')

        if n_invalid_mails > 0:
            it_or_them = 'it' if n_invalid_mails == 1 else 'them'
            warnings.append(f'{n_invalid_mails} invalid mails detected (no or invalid attachments)\n Respond to {it_or_them} manually.')

        return valid_msgs, warnings


    def getNewValidMailsWin32(self, warnings: list) -> tuple[int, list, list]:
        
        valid_msgs = []
        n_invalid_mails = 0

        temp_folder_global_path = os.path.join(self.gv['DATA_DIR_HOME'], 'TEMP')
        delete_directory_content(None, self.gv, temp_folder_global_path)


        for message in self.inbox.Items:
            if self.gv['ONLY_UNREAD_MAIL']:
                if message.UnRead:
                    if self.isMailAValidJobRequest(message):
                        valid_msgs.append(self.saveMsgAndAttachmentsInTempFolder(message))
                    else:
                        n_invalid_mails += 1
            elif self.isMailAValidJobRequest(message):


                    valid_msgs.append(self.saveMsgAndAttachmentsInTempFolder(message))
            else:
                n_invalid_mails += 1

        return n_invalid_mails, valid_msgs, warnings


    def getNewValidMailsLinux(self, warnings: list) -> tuple[int, list, list]:

        valid_msgs = []
        n_invalid_mails = 0

        self.imapLogin()

        if self.gv['ONLY_UNREAD_MAIL']:
            status, response = self.imap_mail.search(None, 'UNSEEN')
        else:
            status, response = self.imap_mail.search(None, 'ALL')

        if status != 'OK':
            raise ValueError('Received status: {status} from mail server')

        for mail_id in response[0].split():
            status, msg_data = self.imap_mail.fetch(mail_id, "(RFC822)")
            if self.isMailAValidJobRequest(msg_data):
                valid_msgs.append(msg_data)
            else:
                n_invalid_mails += 1

        self.imapLogout()

        return n_invalid_mails, valid_msgs, warnings


    def saveMsgAndAttachmentsInTempFolder(self, msg) -> str:
        ''' Save Outlook msg and attachments in a temperary folder. '''

        assert sys.platform == 'win32', f'This function is only for win32, not for {sys.platform}'

        unique_mail_code = unidecode(self.getEmailAddress(msg)+'_'+str(msg.Size))+'_'+str(time.time())

        temp_folder_global_path = os.path.join(self.gv['DATA_DIR_HOME'], 'TEMP', unique_mail_code)

        assert not os.path.exists(temp_folder_global_path), f'{temp_folder_global_path} should not yet exist'

        os.mkdir(temp_folder_global_path)

        # save the msg file
        msg.saveAs(os.path.join(temp_folder_global_path, 'mail.msg'))

        # save attachments
        for attachment in msg.Attachments:
            attachment.SaveAsFile(os.path.join(temp_folder_global_path, unidecode(attachment.FileName)))

        return temp_folder_global_path


    def moveEmailToVerwerktFolder(self,
                                  mail_item=None,
                                  sender_mail_adress=None,
                                  sender_mail_receive_time=None):
        ''' Move email to verwerkt folder. '''

        if self.gv['MOVE_MAILS_TO_VERWERKT_FOLDER']:
            if sys.platform == 'win32':
                assert sender_mail_adress is not None, 'sender_mail_adress is None'
                assert sender_mail_receive_time is not None, 'sender_mail_receive_time is None'

                for message in self.inbox.Items:
                    if sender_mail_adress == self.getEmailAddress(message) and\
                        sender_mail_receive_time == str(message.ReceivedTime):
                            message.UnRead = False
                            message.Move(self.verwerkt_folder)

            elif sys.platform == 'linux':
                if not self.isThereInternet():
                    raise ConnectionError('Not connected to the internet')

                self.imapLogin()
                assert isinstance(mail_item, list), f'mail_item should be of type list and is of type {type(mail_item)}'

                # Extract the mail UID using regular expression
                match = re.search(rb'\b(\d+)\b', mail_item[0][0])

                if match:
                    uid_msg_set = (match.group(1))
                    self.imap_mail.copy(uid_msg_set, 'Verwerkt')
                    self.imap_mail.store(uid_msg_set, '+FLAGS', r'(\Deleted)')

                self.imapLogout()

            else:
                raise ValueError(f'software not applicable to platform {sys.platform}')

    def isMailAValidJobRequest(self, msg) -> bool:
        ''' Check if the requirements are met for a valid job request. '''

        if sys.platform == 'win32':

            # msg is a temp_folder_global_path toward a temperary storage
            if msg.Attachments:
                for attachment in msg.Attachments:
                    if attachment.FileName.lower().endswith(self.gv['ACCEPTED_EXTENSIONS']):
                        return True

            return False

        if sys.platform == 'linux':
            attachments = self.getAttachments(msg)
            for attachment in attachments:
                file_name = self.getAttachmentFileName(attachment)
                if bool(file_name):
                    if file_name.lower().endswith(self.gv['ACCEPTED_EXTENSIONS']):
                        return True

            return False

        raise ValueError(f'software not applicable to platform {sys.platform}')

    def getMailBody(self, mail_item):
        ''' Return mail body. '''

        mail_file = self.mailItemToMailFile(mail_item)

        if sys.platform == 'win32':
            return mail_file.Body

        if sys.platform == 'linux':

            # Check if the email is multipart
            mail_body = None
            if mail_file.is_multipart():
                for part in mail_file.walk():
                    # Check each part for HTML content
                    if part.get_content_type() == 'text/html':
                        mail_body = part.get_payload(decode=True)

                    if part.get_content_type() == 'text/plain':
                        mail_body = part.get_payload(decode=True)

            elif mail_file.get_content_type() == 'text/html':
                mail_body = mail_file.get_payload(decode=True)

            if isinstance(mail_body, bytes):
                mail_body = mail_body.decode('utf-8')

            if mail_body is not None:
                return mail_body

            raise ValueError(f'Could not get mail Body from mail file type {type(mail_file)}')
        raise ValueError(f'software not applicable to platform {sys.platform}')


    def getEmailAddress(self, mail_item) -> str:
        ''' Return the email adress. '''
        mail_file = self.mailItemToMailFile(mail_item)

        if sys.platform == 'win32':

            if mail_file.Class==43:
                if mail_file.SenderEmailType=='EX':
                    if mail_file.Sender.GetExchangeUser() is not None:
                        return mail_file.Sender.GetExchangeUser().PrimarySmtpAddress
                    return mail_file.Sender.GetExchangeDistributionList().PrimarySmtpAddress
                return mail_file.SenderEmailAddress

            raise ValueError("Could not get email adress")

        if sys.platform == 'linux':

            mail_name_long = mail_file.get('From')
            match = re.search(r'<(.*?)>', mail_name_long)
            if match:
                return str(match.group(1))
            raise ValueError(f'Could not convert {mail_name_long} to mail adress')

        raise ValueError(f'software not applicable to platform {sys.platform}')


    def getSenderMailReceiveTime(self, mail_item) -> str:
        ''' Return the time a mail was received. '''

        mail_file = self.mailItemToMailFile(mail_item)

        if sys.platform == 'win32':
            return str(mail_file.ReceivedTime)

        if sys.platform == 'linux':
            return str(mail_file['date'])

        raise ValueError(f'software not applicable to platform {sys.platform}')

    def getSenderName(self, mail_item) -> str:
        ''' Return the senders name. '''

        mail_file = self.mailItemToMailFile(mail_item)

        if sys.platform == 'win32':
            return str(mail_file.Sender)

        if sys.platform == 'linux':
            return self.mailToName(mail_file.get('From'))

        raise ValueError(f'software not applicable to platform {sys.platform}')

    def getMailSubject(self, mail_item) -> str:
        ''' Return the subject from mail file. '''

        mail_file = self.mailItemToMailFile(mail_item)

        if sys.platform == 'win32':
            return str(mail_file.Subject)

        if sys.platform == 'linux':
            return mail_file.get('Subject')

        raise ValueError(f'software not applicable to platform {sys.platform}')

    def mailItemToMailFile(self, mail_item):
        ''' Return Msg from global path to mail.msg. '''

        if sys.platform == 'win32':
            if isinstance(mail_item, client.CDispatch):
                return mail_item

            if isinstance(mail_item, str):
                return self.outlook.OpenSharedItem(self.getMailGlobalPathFromFolder(mail_item))

        if sys.platform == 'linux':
            if isinstance(mail_item, email.message.Message):
                return mail_item

            if isinstance(mail_item, list):
                return email.message_from_bytes(mail_item[0][1])

            if isinstance(mail_item, str):
                with open(self.getMailGlobalPathFromFolder(mail_item), 'rb') as file:
                    return email.message_from_binary_file(file, policy=default)

            raise ValueError('Could not parse mail_item of type {type(mail_item)} to a mail_file')

        raise ValueError(f'software not applicable to platform {sys.platform}')


    def getMailGlobalPathFromFolder(self, folder_global_path: str) -> str:
        ''' Return the global path toward a mail file in a folder. '''
        mail_file_global_path = ''

        if sys.platform == 'win32':
            if folder_global_path.lower().endswith('mail.msg'):
                mail_file_global_path = folder_global_path
            else:
                mail_file_global_path = os.path.join(folder_global_path, 'mail.msg')

        if sys.platform == 'linux':
            if folder_global_path.lower().endswith('mail.eml'):
                mail_file_global_path = folder_global_path
            else:
                mail_file_global_path = os.path.join(folder_global_path, 'mail.eml')

        if os.path.exists(mail_file_global_path):
            return mail_file_global_path

        raise ValueError(f'software not applicable to platform {sys.platform}')

    def getAttachments(self, msg) -> list:
        ''' Return a list with attachment names. '''

        if sys.platform == 'win32':
            assert os.path.exists(msg), f'could not find directory {msg}'
            return [os.path.abspath(os.path.join(msg, file)) for file in os.listdir(msg) if not file.lower().endswith('.msg')]

        if sys.platform == 'linux':
            attachments = []
            for part in email.message_from_bytes(msg[0][1]).walk():

                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Content-Disposition') is None:
                    continue

                encoded_filename = part.get_filename()

                if encoded_filename is None:
                   continue

                attachments.append(part)

            return attachments

        raise ValueError(f'software not applicable to platform {sys.platform}')

    def getAttachmentFileName(self, attachment) -> str:
        ''' Return the attachment filename. '''
        if sys.platform == 'win32':
            return os.path.basename(attachment)

        if sys.platform == 'linux':
            encoded_filename = attachment.get_filename()
            filename, encoding = decode_header(encoded_filename)[0]

            if(encoding is None):
                return filename

            return filename.decode(encoding)

        raise ValueError(f'software not applicable to platform {sys.platform}')

    def saveMail(self, msg, job_folder_global_path: str):
        ''' Save mail in a folder. '''
        if sys.platform == 'win32':
            msg = self.mailItemToMailFile(msg)
            msg.saveAs(os.path.join(job_folder_global_path, 'mail.msg'))

        elif sys.platform == 'linux':
            with open(os.path.join(job_folder_global_path, 'mail.eml'), 'wb') as mail_file:
                mail_file.write(msg[0][1])

        else: 
            raise ValueError(f'software not applicable to platform {sys.platform}')

    def saveAttachment(self, attachment, file_name_global_path: str):
        ''' Save mail in a folder. '''

        if sys.platform == 'win32':
            shutil.copy(attachment, file_name_global_path)

        elif sys.platform == 'linux':
            with open(file_name_global_path, 'wb') as file:
                file.write(attachment.get_payload(decode=True))

        else:
            raise ValueError(f'software not applicable to platform {sys.platform}')

    def replyToEmailFromFileUsingTemplate(self,
                    mail_item, # mail file, path toward folder containing mail file or mail file global path
                    template_file_name: str,
                    template_content: dict,
                    popup_reply=True):
        ''' Reply to .msg file using a template. '''
        if not self.isThereInternet():
            raise ConnectionError('Not connected to the internet')

        if template_content is None:
            template_content = {}

        if sys.platform == 'win32':
            msg = self.mailItemToMailFile(mail_item)

            # load recipient_name in template
            template_content["{sender_name}"] = msg.Sender

            with open(self.gv[template_file_name], 'r') as file:
                html_content = file.read()

            for key, value in template_content.items():
                html_content = html_content.replace(key, str(value))

            reply = msg.Reply()
            reply.HTMLBody = html_content

            if popup_reply:
                reply.Display(True)
            else:
                reply.Send()

        elif sys.platform == 'linux':

            eml = self.mailItemToMailFile(mail_item)

            original_sender_mail_long = eml.get('From')
            original_sender_mail = parseaddr(original_sender_mail_long)[1]
            sender_name = self.mailToName(str(original_sender_mail_long))

            # load template content into html template
            template_content['{sender_name}'] =  sender_name
            with open(self.gv[template_file_name], "r") as file:
                html_content = file.read()

            for key, value in template_content.items():
                html_content = html_content.replace(key, str(value))

            # Create the reply messageI
            reply_mail = MIMEMultipart("alternative")
            reply_mail["Subject"] = "Re: " + eml.get("Subject", "")
            reply_mail["From"] = formataddr((self.gv['MAIL_NAME'], self.gv['MAIL_ADRESS']))
            reply_mail["To"] = original_sender_mail
            reply_mail["In-Reply-To"] = eml.get('Message-ID')
            reply_mail.attach(MIMEText(html_content, "html"))

            context = ssl.create_default_context()


            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.gv['MAIL_ADRESS'], self.gv['MAIL_PASSWORD'])
                server.send_message(reply_mail)
        else:
            raise ValueError(f'software not applicable to platform {sys.platform}')

    def mailToName(self, mail_name: str) -> str:
        ''' Convert mail in form first_name last_name <mail@adres.com> to a more friendly name. '''

        matches = re.match(r"(.*?)\s*<(.*)>", mail_name)

        if matches:
            if len(matches.group(1)) > 0:
                return matches.group(1)
            if len(matches.group(2)):
                return matches.group(2).split('@')[0]
        elif '@' in mail_name:
            return mail_name.split('@')[0]
        return mail_name

    def isThereInternet(self) -> bool:
        conn = httplib.HTTPSConnection("8.8.8.8", timeout=5)
        try:
            conn.request("HEAD", "/")
            return True
        except Exception:
            return False
        finally:
            conn.close()
