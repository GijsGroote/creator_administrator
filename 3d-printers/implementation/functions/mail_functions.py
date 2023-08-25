"""
Handle mail functionality.
"""

import os
import re
import datetime
import tempfile
import re
import win32com.client
import email
from email.header import decode_header
from typing import Tuple

from global_variables import (
    EMAIL_TEMPLATES_DIR_HOME,
    PRINT_DIR_HOME,
    FUNCTIONS_DIR_HOME)
from create_batch_file import python_to_batch
from directory_functions import make_print_job_unique
from talk_to_sa import yes_or_no

class EmailManager:
    """
    Class for managing emails using win32com.client
    can be used to:
    - get unread emails
    - save emails to file
    - reply to emails
    - reply to emails from file
    """
    def __init__(self):
        self.outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
        self.inbox = self.outlook.GetDefaultFolder(6)


    def get_unread_emails(self):
        """get all unread emails from inbox"""
        unread_emails = []
        for message in self.inbox.Items:
            if message.UnRead:
                unread_emails.append(message)
                message.UnRead = False
                message.Save()
        return unread_emails


    def save_emails(self, emails, folder):
        """save list of emails to file"""
        for email in emails:
            self.save_email(email, folder, filename=f"{email.Sender}.msg")


    def save_email(self, email, folder, filename="email.msg"):
        """save email to file"""
        email.SaveAs(os.path.join(folder, filename))

    def reply_to_email(self, email, reply_body=""):
        """reply to email that is in mailitem format"""
        reply = email.Reply()
        reply.HTMLBody = reply_body + "\n" + reply.HTMLBody
        reply.Display(True)

    def reply_to_email_from_file(self, file_path, reply_body=""):
        """reply to email that is saved to .msg file"""
        msg = self.outlook.OpenSharedItem(file_path)
        self.reply_to_email(msg, reply_body=reply_body)
        
    def reply_to_email_from_file_using_template(self, file_path, template_file_name, template_content):
        """reply to email that is saved to .msg file"""
        template_path = os.path.join(EMAIL_TEMPLATES_DIR_HOME, template_file_name)
        msg = self.outlook.OpenSharedItem(file_path)
        sender_name = msg.SenderName
        
        with open(template_path, "r") as file:
            html_content = file.read()
        
        html_content = html_content.replace("{recipient_name}", sender_name)
        
        for key, value in template_content.items():
            html_content = html_content.replace(key, value)
        
        self.reply_to_email(msg, reply_body=html_content)


def send_response_mail(incoming_mail_path: str, template: str, template_content: dict):
    """ Send a response to incoming mail. """
    email_manager = EmailManager()
    email_manager.reply_to_email_from_file_using_template(
        incoming_mail_path,
        template,
        template_content)


def mail_to_name(mail_name: str):
    """ Convert mail in form first_name last_name <mail@adres.com> to a more friendly name. """

    matches = re.match(r"(.*?)\s*<(.*)>", mail_name)

    if matches:
        if len(matches.group(1)) > 0:
            return matches.group(1)
        if len(matches.group(2)):
            return matches.group(2).split('@')[0]
    else:
        if '@' in mail_name:
            return mail_name.split('@')[0]
    return mail_name


def mail_to_print_job_name(msg: [email.message.Message, str]) -> str:
    """ Extract senders from mail and convert to a print job name. """

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

    job_name = re.sub(r'[^\w\s]', '', mail_to_name(decoded_sender)).replace(' ', '_')

    # check if print job name is unique
    return make_print_job_unique(job_name)


def is_mail_a_valid_print_job_request(msg) -> Tuple[bool, str]:
    """ Check if the requirements are met for a valid print job. """

    # Initialize a counter for attachments with .stl extension
    stl_attachment_count = 0

    attachments = msg.Attachments
    
    for attachment in attachments:
        if attachment.FileName.lower().endswith('.stl'):
            stl_attachment_count += 1

    if stl_attachment_count == 0:
        return False, 'no .stl attachment found'

    elif stl_attachment_count > 5 and stl_attachment_count <= 10:
        print(f'warning! there are: {stl_attachment_count} .stl files in the mail')

    elif stl_attachment_count > 10:
        if yes_or_no(f'{stl_attachment_count} .stl files found do '
                     f'you want to create an print job (Y/n)?'):
            return True, f'you decided that: {stl_attachment_count} .stl is oke'
        else:
            return False, f'you decided that: {stl_attachment_count} .stl files are to much'

    return True, ' '


def mail_to_print_job(msg):
    """ Create a 'print job' or folder in WACHTRIJ and
    put all corresponding files in the print job. """

    job_name = mail_to_print_job_name(msg)

    today = datetime.date.today()
    job_folder_name = str(today.strftime('%d')) + '-' + str(today.strftime('%m')) + '_' + job_name

    print_job_global_path = os.path.join(os.path.join(PRINT_DIR_HOME, 'WACHTRIJ', job_folder_name))
    os.mkdir(print_job_global_path)

    # Save the email as a .eml file
    msg.SaveAs(os.path.join(print_job_global_path, 'mail.msg'))

    # Save the .stl files
    for attachment in msg.Attachments:
        if attachment.FileName.lower().endswith('.stl'):
            attachment.SaveAsFile(os.path.join(print_job_global_path, attachment.FileName))

    python_to_batch(os.path.join(FUNCTIONS_DIR_HOME, 'afgekeurd.py'), job_name)
    python_to_batch(os.path.join(FUNCTIONS_DIR_HOME, 'gesliced.py'), job_name)

