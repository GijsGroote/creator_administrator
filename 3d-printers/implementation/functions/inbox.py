# ! /usr/bin/env python3

import datetime
import os
import re
import email
from email.header import decode_header
from typing import Tuple
import imaplib
import win32com.client

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import tempfile

from global_variables import (
    FUNCTIONS_DIR_HOME,
    PRINT_DIR_HOME)

from directory_functions import (
    get_print_job_folder_names)

from executable_functions import python_to_batch
from mail_functions import mail_to_name
from talk_to_sa import yes_or_no


def is_print_job_name_unique(job_name: str) -> bool:
    """ check if the print job name is unique, return boolean """

    # TODO (AGAIN): job A_B is creatd, A_B_(1) is created,  A_B is removed. Using this function
    # the job called A_B will return job A_B_(1), which IS A DIFFERENT JOB
    # edit this function so that it raises a valueError('no job found')
    # when A_B is searched but only A_B_(1) is present

    for folder_name in get_print_job_folder_names():
        if job_name in folder_name:
            return False

    return True


def mail_to_print_job_name(msg: [email.message.Message, str]) -> str:
    """ extract senders from mail and convert to a print job name """

    print(type(msg))
    if isinstance(msg, email.message.Message):
        from_field = msg.get("From")
        # Decode the "From" field
        decoded_sender, charset = decode_header(from_field)[0]

        # If the sender's name is bytes, decode it using the charset
        if isinstance(decoded_sender, bytes):
            decoded_sender = decoded_sender.decode(charset)
            
    elif isinstance(msg, email.mime.multipart.MIMEMultipart):
        decoded_sender = msg.get("From")
    elif isinstance(msg, str):
        decoded_sender = msg
    else:
        raise ValueError(f"could not convert {msg} to a job name")

    job_name = re.sub(r'[^\w\s]', '', mail_to_name(decoded_sender)).replace(" ", "_")
    print(job_name)

    # check if print job name is unique
    unique_job_name = job_name
    if not is_print_job_name_unique(unique_job_name):
        existing_job_names = [job_name]
        unique_job_name = job_name + "_(" + str(len(existing_job_names)) + ")"

        while not is_print_job_name_unique(unique_job_name):
            existing_job_names.append(unique_job_name)
            unique_job_name = job_name + "_(" + str(len(existing_job_names)) + ")"

        if len(existing_job_names) == 1:
            print(f" Warning! print job name {existing_job_names[0]} already exist, create name: {unique_job_name}")
        else:
            print(f" Warning! print job names {existing_job_names} already exist, create name: {unique_job_name}")

    return unique_job_name


def is_valid_print_job_request(msg: email.message.Message) -> Tuple[bool, str]:
    """ check if the requirements are met for a valid print job """

    # Initialize a counter for attachments with .stl extension
    stl_attachment_count = 0

    if msg.get_content_maintype() == "multipart":
        for part in msg.walk():
            if part.get_content_maintype() == "multipart" or part.get("Content-Disposition") is None:
                continue
            filename = part.get_filename()
            if filename:
                decoded_filename = decode_header(filename)[0][0]
                if decoded_filename.lower().endswith(".stl"):
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


def create_print_job(msg: email.message.Message, raw_email: bytes):
    """ create a 'print job' or folder in WACHTRIJ and put all corresponding files in the print job """

    job_name = mail_to_print_job_name(msg)

    today = datetime.date.today()
    job_folder_name = str(today.strftime("%d")) + "-" + str(today.strftime('%m')) + "_" + job_name

    print_job_global_path = os.path.join(os.path.join(PRINT_DIR_HOME, "WACHTRIJ", job_folder_name))
    os.mkdir(print_job_global_path)

    # Save the email as a .eml file
    with open(os.path.join(print_job_global_path, "mail.eml"), "wb") as eml_file:
        eml_file.write(raw_email)

    # Save the .stl files
    if msg.get_content_maintype() == "multipart":
        for part in msg.walk():
            if part.get_content_maintype() == "multipart" or part.get("Content-Disposition") is None:
                continue
            filename = part.get_filename()
            if filename and filename.lower().endswith(".stl"):
                decoded_filename = decode_header(filename)[0][0]
                file_path = os.path.join(print_job_global_path, decoded_filename)
                with open(file_path, "wb") as f:
                    f.write(part.get_payload(decode=True))
                print("Saved attachment:", decoded_filename)

    # create afgekeurd.exe
    python_to_batch(os.path.join(FUNCTIONS_DIR_HOME, 'afgekeurd.py'), job_name)

    # create gesliced.exe
    python_to_batch(os.path.join(FUNCTIONS_DIR_HOME, 'gesliced.py'), job_name)


def convert_win32_msg_to_email_msg(win32_msg):
    email_msg = MIMEMultipart()
    email_msg['From'] = win32_msg.SenderEmailAddress
    email_msg['To'] = win32_msg.To
    email_msg['Subject'] = win32_msg.Subject
    # email_msg['Date'] = win32_msg.SentOn
    
    email_body = MIMEText(message.Body, _charset="utf-8")
    email_msg.attach(email_body)
    for attachment in message.Attachments:
        # Save attachment to a temporary file
        temp_dir = tempfile.gettempdir()
        temp_filename = os.path.join(temp_dir, attachment.FileName)
        attachment.SaveAsFile(temp_filename)

        # Read attachment content and create MIMEApplication object
        with open(temp_filename, "rb") as attachment_file:
            attachment_content = attachment_file.read()

        mime_attachment = MIMEApplication(attachment_content)
        mime_attachment.add_header('content-disposition', 'attachment', filename=attachment.FileName)

        # Attach the attachment to the email
        email_msg.attach(mime_attachment)

        # Remove the temporary file
        os.remove(temp_filename)
    return email_msg



if __name__ == '__main__':
    """
    Loop over inbox, download all valid 3D print jobs to a unique folder in WACHTRIJ.
    """

    # open outlook
    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    inbox = outlook.GetDefaultFolder(6)

    # read unread mails and convert to the email format and mark them as read
    msgs = []
    new_print_job = False
    for message in inbox.Items:
        if message.UnRead:
            converted_email = convert_win32_msg_to_email_msg(message)
            msgs.append(converted_email)
            message.UnRead = False
            message.Save()

    # print how many mails are processed
    if len(msgs) == 0:
        print('no unread mails found')
    else:
        print(f'processing {len(msgs)} new mails')

    # loop over all mails, check if they are valid and create print jobs
    for msg in msgs:
        print(f'processing incoming mail from: {msg.get("From")}')

        (is_valid, invalid_reason) = is_valid_print_job_request(msg)
        
        if is_valid:
            new_print_job = True
            print_job_name = mail_to_print_job_name(msg)
            print(f'mail from: {msg.get("From")} is valid request, create print job: {print_job_name}')
            create_print_job(msg, msg.as_bytes())
            print(f'print job: {print_job_name} created\n')

        else:
            print(f'mail from {msg.get("From")} is not a valid request because:\n {invalid_reason}, abort!\n')
        
    # open the 'WACHTRIJ' folder if new print jobs are created
    if new_print_job:
        os.startfile(os.path.join(PRINT_DIR_HOME, 'WACHTRIJ'))
