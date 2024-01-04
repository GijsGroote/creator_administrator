"""

Handle mail functionality.
"""

import os
import sys
from typing import Tuple


if sys.platform == 'linux':
    import imaplib
    import email
    import smtplib
    import ssl
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.image import MIMEImage
    from email.mime.application import MIMEApplication
    from email.utils import formatdate, parseaddr, formataddr 
    from email.parser import BytesParser
    from email.policy import default
    from email.header import decode_header

elif sys.platform == 'win32':
    import win32com.client
else:
    raise ValueError(f'This software does not work for platform: {sys.platform}')

from talk_to_sa import yes_or_no
from convert_functions import mail_to_name

class MailManager():

    def __init__(self, gv: dict):
        self.gv = gv

        if sys.platform == 'win32':
            self.outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
            self.inbox = self.outlook.GetDefaultFolder(6)
            try:
                self.verwerkt_folder = self.inbox.Parent.Folders.Item("Verwerkt")
            except:
                self.verwerkt_folder = self.inbox.Parent.Folders.Add("Verwerkt")

        if sys.platform == 'linux':

            with open('/home/gijs/Documents/email_password.txt', 'r') as file:
                # Read the content of the file
                password = file.read()
            self.username = 'gijsgroote@hotmail.com'
            self.password = password

            # specific to gmail and outlook
            self.smtp_server = 'smtp-mail.outlook.com'
            self.smtp_port = 587 
            self.imap_server = 'outlook.office365.com'
            self.imap_mail_server_running = False

    def imapLogin(self):
        ''' Login to the IMAP server to download mails. '''
        if not self.imap_mail_server_running:
            self.imap_mail = imaplib.IMAP4_SSL(self.imap_server)
            self.imap_mail.login(self.username, self.password)

            self.imap_mail.select('inbox')
            self.imap_mail_server_running = True

        # create Verwerkt folder
        status, mailboxes = self.imap_mail.list()
        if status == 'OK':
            if not any('Verwerkt' in mbox.decode() for mbox in mailboxes):
                self.imap_mail.create('Verwerkt')

    def imapLogout(self):
        ''' Logout of the IMAP server. '''
        self.imap_mail.close()
        self.imap_mail.logout()
        self.imap_mail_server_running = False

    def smtpSendMessage(self, msg):
        if self.imap_mail_server_running:
            self.imapLogout()

        context = ssl.create_default_context()

        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls(context=context)
            server.login(self.username, self.password)
            server.sendmail(self.username, self.username, msg)

    def getUnreadEmails(self) -> list:
        """ Return emails from Outlook inbox. """
        if sys.platform == 'win32':
            msgs = []
            for message in self.inbox.Items:
                # the IWS computer appends every mail in the inbox
                if self.gv['IWS_COMPUTER']:
                    msgs.append(message)
                # other than the IWS computer only appends unread mails
                elif message.UnRead:
                    msgs.append(message)

                if self.gv["IWS_COMPUTER"]:
                    message.UnRead = False
                    message.Save()

            # print how many mails are processed
            if len(msgs) == 0:
                print('no unread mails found')
            else:
                print(f'processing {len(msgs)} new mails')
            return msgs


        if sys.platform == 'linux':
            self.imapLogin()

            status, response = self.imap_mail.search(None, 'UNSEEN')
            if status != 'OK':
                return []

            msgs = []
            for mail_id in response[0].split():
                print(f"mail id yo {mail_id}")
                status, msg_data = self.imap_mail.fetch(mail_id, "(RFC822)")
                msgs.append(msg_data)

            self.imapLogout()

            return msgs

    
    def moveEmailToVerwerktFolder(self, msg):
        """ Move email to verwerkt folder. """
        if sys.platform == 'win32':
            msg.Move(self.verwerkt_folder)
        if sys.platform == 'linux':
            self.imapLogin()

            # find UID of mail
            msg_uid = msg[0][0][0:5]
            print(f"from verwerk f {msg_uid}")
            self.imap_mail.copy(msg_uid, 'Verwerkt')
            self.imap_mail.store(msg_uid, '+FLAGS', r'(\Deleted)')

            self.imapLogout()

    def isMailAValidJobRequest(self, msg) -> Tuple[bool, str]:
        """ Check if the requirements are met for a valid job request. """

        if sys.platform == 'win32':
            attachments = msg.Attachments

            for attachment in attachments:
                if attachment.FileName.lower().endswith(self.gv['ACCEPTED_EXTENSIONS']):

                    return True, ' '

            return False, f'no {self.gv["ACCEPTED_EXTENSIONS"]} attachment found'

        if sys.platform == 'linux':
            attachments = self.getAttachments(msg)
            for attachment in attachments:
                file_name = attachment.get_filename()        
                print(f'hey file {file_name} detected')
                if bool(file_name):
                    if file_name.lower().endswith(self.gv['ACCEPTED_EXTENSIONS']):

                        return True, ' '

            return False, f'no {self.gv["ACCEPTED_EXTENSIONS"]} attachment found'


    def printMailBody(self, msg):
        """ Print mail body. """
        if sys.platform == 'win32':
            print(msg.Body)
        if sys.platform == 'linux':
            msg = email.message_from_bytes(msg[0][1])
            content_type = msg.get_content_maintype()

            if content_type == 'multipart':
                for part in msg.walk():
                    if part.get_content_maintype() == 'text':
                        print(part.get_payload(decode=True).decode(part.get_content_charset()))
            elif content_type == 'text':
                 print(msg.get_payload(decode=True).decode(msg.get_content_charset()))

    def printMailBodyFromPath(self, msg_file_path: str):
        """ Print the content of an .msg file. """

        if sys.platform == 'win32':
            outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
            msg = outlook.OpenSharedItem(msg_file_path)

            print(msg.Body)

        if sys.platform == 'linux':

            with open(msg_file_path, 'rb') as f:
                msg = BytesParser(policy=default).parse(f)

            self.printMailBody(msg)

    def getEmailAddress(self, msg) -> str:
        """ Return the email adress. """
        if sys.platform == 'win32':
            if msg.Class==43:
                if msg.SenderEmailType=='EX':
                    if msg.Sender.GetExchangeUser() is not None:
                        return msg.Sender.GetExchangeUser().PrimarySmtpAddress
                    return msg.Sender.GetExchangeDistributionList().PrimarySmtpAddress
                return msg.SenderEmailAddress

            raise ValueError("Could not get email adress")

        if sys.platform == 'linux':
            return email.message_from_bytes(msg[0][1]).get('From')

    def getMailGlobalPathFromFolder(self, job_folder_global_path: str) -> str:
        ''' Return the global path toward a mail file in a folder. '''

        if sys.platform == 'win32':
            return os.path.join(job_folder_global_path, 'mail.msg')

        if sys.platform == 'linux':
            return os.path.join(job_folder_global_path, 'mail.eml')

    def getAttachments(self, msg) -> list:
        ''' Return a list with attachment names. '''

        if sys.platform == 'win32':
            return msg.Attachments
        if sys.platform == 'linux':
           attachments = []
           for part in email.message_from_bytes(msg[0][1]).walk():
                # Check if the part is an attachment
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Content-Disposition') is None:
                    continue

                if not part.get_filename():
                    continue
                else:
                    attachments.append(part)

           return attachments

    def getAttachmentFileName(self, attachment) -> str:
        ''' Return the attachment filename. '''
        if sys.platform == 'win32':
            return attachment.FileName
        if sys.platform == 'linux':
            return attachment.get_filename()


    def saveMail(self, msg, job_folder_global_path: str):
        ''' Save mail in a folder. '''
        if sys.platform == 'win32':
            msg.saveAs(os.path.join(laser_job_global_path, 'mail.msg'))

        if sys.platform == 'linux':
            with open(os.path.join(job_folder_global_path, 'mail.eml'), 'wb') as mail_file:
                mail_file.write(msg[0][1])

    def saveAttachment(self, attachment, file_name_global_path: str):
        ''' Save mail in a folder. '''

        if sys.platform == 'win32':
            attachment.SaveAsFile(file_name_global_path)

        if sys.platform == 'linux':

            with open(file_name_global_path, 'w') as file:
                file.write(attachment)


    def replyToEmailFromFileUsingTemplate(self,
                                                msg_file_path: str,
                                                template_file_name: str,
                                                template_content: dict,
                                                popup_reply=True):
        """ Reply to .msg file using a template. """


        with open(self.gv[template_file_name], "r") as file:
            html_content = file.read()


        for key, value in template_content.items():
            html_content = html_content.replace(key, str(value))


        if sys.platform == 'win32':
            msg = self.outlook.OpenSharedItem(msg_file_path)

            # load recipient_name in template
            template_content["{recipient_name}"] = mail_to_name(str(msg.Sender))

            reply = msg.Reply()
            reply.HTMLBody = html_content

            if popup_reply:
                print('Send the Outlook popup reply, it can be behind other windows')
                reply.Display(True)
            else:
                reply.Send()

        if sys.platform == 'linux':


            with open(msg_file_path, 'rb') as file:
                msg = email.message_from_binary_file(file, policy=default)
                original_sender_mail_long = msg.get('From')
                original_sender_mail = parseaddr(original_sender_mail_long)[1]

            # load recipient_name in template
            template_content['{recipient_name}'] = mail_to_name(str(original_sender_mail_long))

            # Create the reply messageI
            reply_msg = MIMEMultipart("alternative")
            reply_msg["Subject"] = "Re: " + msg.get("Subject", "")
            reply_msg["From"] = formataddr(('Your Name', self.username))
            reply_msg["To"] = original_sender_mail
            # reply_msg["In-Reply-To"] = msg.get('Message-ID')
            reply_msg.attach(MIMEText(html_content, "html"))

            self.smtpSendMessage(reply_msg)
            print("Email sent successfully!")


