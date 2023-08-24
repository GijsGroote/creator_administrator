"""
Handle mail functionality.
"""

import os
import re
from email_manager import EmailManager

import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import tempfile
import subprocess
import re
import email
from email.header import decode_header
from typing import Tuple

from global_variables import (
    OUTLOOK_PATH,
    PRINT_DIR_HOME,
    FUNCTIONS_DIR_HOME)
from create_batch_file import python_to_batch
from directory_functions import (
    make_print_job_unique)
from talk_to_sa import yes_or_no



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


def is_mail_a_valid_print_job_request(msg: email.message.Message) -> Tuple[bool, str]:
    """ Check if the requirements are met for a valid print job. """

    # Initialize a counter for attachments with .stl extension
    stl_attachment_count = 0

    if msg.get_content_maintype() == 'multipart':
        for part in msg.walk():
            if part.get_content_maintype() == 'multipart' or part.get('Content-Disposition') is None:
                continue
            filename = part.get_filename()
            if filename:
                decoded_filename = decode_header(filename)[0][0]
                if decoded_filename.lower().endswith('.stl'):
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


def convert_win32_msg_to_email_msg(win32_msg) -> email.mime.multipart.MIMEMultipart:
    """ Convert a win32 message to an email message. """
    # create a new email message and copy the win32 message fields to the email message
    email_msg = MIMEMultipart()
    email_msg['From'] = win32_msg.SenderEmailAddress
    email_msg['To'] = win32_msg.To
    email_msg['Subject'] = win32_msg.Subject

    email_body = MIMEText(win32_msg.Body, _charset='utf-8')
    email_msg.attach(email_body)

    # Loop over attachments and add them to the email message
    for attachment in win32_msg.Attachments:
        # Save attachment to a temporary file
        temp_dir = tempfile.gettempdir()
        temp_filename = os.path.join(temp_dir, attachment.FileName)
        attachment.SaveAsFile(temp_filename)

        # Read attachment content and create MIMEApplication object
        with open(temp_filename, 'rb') as attachment_file:
            attachment_content = attachment_file.read()

        mime_attachment = MIMEApplication(attachment_content)
        mime_attachment.add_header('content-disposition', 'attachment', filename=attachment.FileName)

        # Attach the attachment to the email
        email_msg.attach(mime_attachment)

        # Remove the temporary file
        os.remove(temp_filename)
    return email_msg


def mail_to_print_job(msg: email.message.Message, raw_email: bytes):
    """ Create a 'print job' or folder in WACHTRIJ and
    put all corresponding files in the print job. """

    job_name = mail_to_print_job_name(msg)

    today = datetime.date.today()
    job_folder_name = str(today.strftime('%d')) + '-' + str(today.strftime('%m')) + '_' + job_name

    print_job_global_path = os.path.join(os.path.join(PRINT_DIR_HOME, 'WACHTRIJ', job_folder_name))
    os.mkdir(print_job_global_path)

    # Save the email as a .eml file
    with open(os.path.join(print_job_global_path, 'mail.eml'), 'wb') as eml_file:
        eml_file.write(raw_email)

    # Save the .stl files
    if msg.get_content_maintype() == 'multipart':
        for part in msg.walk():
            if part.get_content_maintype() == 'multipart' or part.get('Content-Disposition') is None:
                continue
            filename = part.get_filename()
            if filename and filename.lower().endswith('.stl'):
                decoded_filename = decode_header(filename)[0][0]
                file_path = os.path.join(print_job_global_path, decoded_filename)
                with open(file_path, 'wb') as f:
                    f.write(part.get_payload(decode=True))
                print('Saved attachment: ', decoded_filename)

    python_to_batch(os.path.join(FUNCTIONS_DIR_HOME, 'afgekeurd.py'), job_name=job_name)
    python_to_batch(os.path.join(FUNCTIONS_DIR_HOME, 'gesliced.py'), job_name=job_name)

