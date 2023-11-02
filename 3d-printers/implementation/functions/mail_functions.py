"""
Handle mail functionality.
"""

import os
import datetime
import re
import win32com.client
import email
from email.header import decode_header
from typing import Tuple

from global_variables import (
    EMAIL_TEMPLATES_DIR_HOME,
    PRINT_DIR_HOME,
    ACCEPTED_PRINT_EXTENSIONS,
    IWS_3D_PRINT_COMPUTER,
    FUNCTIONS_DIR_HOME)
from create_batch_file import python_to_batch
from directory_functions import make_print_job_name_unique
from talk_to_sa import yes_or_no
from convert_functions import mail_to_name

class EmailManager:
    """
    Class for managing emails using win32com.client
    """
    def __init__(self):
        self.outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
        self.inbox = self.outlook.GetDefaultFolder(6)
        try:
            self.verwerkt_folder = self.inbox.Parent.Folders.Item("Verwerkt")
        except:
            self.verwerkt_folder = self.inbox.Parent.Folders.Add("Verwerkt")
            
    def get_new_emails(self):
        """ return emails from inbox. """
        emails = []
        for message in self.inbox.Items:
            # the IWS computer appends every mail in the inbox
            if IWS_3D_PRINT_COMPUTER:
                emails.append(message)
            # other than the IWS computer only appends unread mails
            elif message.UnRead:
                emails.append(message)
            
            message.UnRead = False
            message.Save()

        return emails

    def move_email_to_verwerkt_folder(self, msg):
        """ move email to verwerkt folder. """
        msg.Move(self.verwerkt_folder)

    def print_mail_content(self, mail_path: str):
        """ Print the content of an .msg file. """
        outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
        msg = outlook.OpenSharedItem(mail_path)

        print(msg.Body)

    def msg_to_email(self, msg: [email.message.Message, str]) -> str:
        """ Extract email adress from email.msg or string. """

        if isinstance(msg, email.message.Message):
            from_field = msg.get('From')
            # Decode the "From" field
            decoded_sender, charset = decode_header(from_field)[0]

            # If the sender's name is bytes, decode it using the charset
            if isinstance(decoded_sender, bytes):
                decoded_sender = decoded_sender.decode(charset)

        elif isinstance(msg, email.mime.multipart.MIMEMultipart):
            decoded_sender = msg.get('From')
        elif isinstance(msg, str):
            decoded_sender = msg
        else:
            raise ValueError(f'could not convert {msg} to a job name')
        
        return decoded_sender

    def reply_to_email_from_file_using_template(self, file_path: str,
                                                template_file_name: str,
                                                template_content: dict,
                                                popup_reply=True):
        """ Reply to .msg file using template. """
        msg = self.outlook.OpenSharedItem(file_path)
        template_path = os.path.join(EMAIL_TEMPLATES_DIR_HOME, template_file_name)
        
        with open(template_path, "r") as file:
            html_content = file.read()
        
        # load content in template
        template_content["{recipient_name}"] = msg.SenderName
        for key, value in template_content.items():
            html_content = html_content.replace(key, value)

        reply = msg.Reply()
        reply.HTMLBody = html_content + "\n" + reply.HTMLBody
        reply.Display(popup_reply)


    def is_mail_a_valid_print_job_request(self, msg) -> Tuple[bool, str]:
        """ Check if the requirements are met for a valid print job. """

        # Initialize a counter for attachments with .stl extension
        print_file_count = 0

        attachments = msg.Attachments
        
        for attachment in attachments:
            if attachment.FileName.lower().endswith(ACCEPTED_PRINT_EXTENSIONS):
                print_file_count += 1

        if print_file_count == 0:
            return False, 'no .stl attachment found'

        elif print_file_count > 5 and print_file_count <= 10:
            print(f'warning! there are: {print_file_count} .stl files in the mail')

        elif print_file_count > 10:
            if yes_or_no(f'{print_file_count} .stl files found do '
                        f'you want to create an print job (Y/n)?'):
                return True, f'you decided that: {print_file_count} .stl is oke'
            else:
                return False, f'you decided that: {print_file_count} .stl files are to much'

        return True, ' '


