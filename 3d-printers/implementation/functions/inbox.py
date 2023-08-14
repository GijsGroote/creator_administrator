# ! /usr/bin/env python3

import datetime
import os
import re
import email
from email.header import decode_header
from typing import Tuple
import imaplib

from global_variables import (
    FUNCTIONS_DIR_HOME,
    PRINT_DIR_HOME,
    IMAP_SERVER,
    EMAIL_PASSWORD,
    EMAIL_ADDRESS)

from directory_functions import (
    get_print_job_folder_names)

from executable_functions import python_to_exe
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

    if isinstance(msg, email.message.Message):
        from_field = msg.get("From")
        # Decode the "From" field
        decoded_sender, charset = decode_header(from_field)[0]

        # If the sender's name is bytes, decode it using the charset
        if isinstance(decoded_sender, bytes):
            decoded_sender = decoded_sender.decode(charset)

    elif isinstance(msg, str):
        decoded_sender = msg
    else:
        raise ValueError(f"could not convert {msg} to a job name")

    job_name = re.sub(r'[^\w\s]', '', mail_to_name(decoded_sender)).replace(" ", "_")

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
    python_to_exe(os.path.join(FUNCTIONS_DIR_HOME, 'afgekeurd.py'), job_name)

    # create gesliced.exe
    python_to_exe(os.path.join(FUNCTIONS_DIR_HOME, 'gesliced.py'), job_name)


if __name__ == '__main__':
    """
    Loop over inbox, download all valid 3D print jobs to a unique folder in WACHTRIJ.
    """

    # Connect to the IMAP server
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    mail.select("inbox")

    # Loop over all new mails
    status, email_ids = mail.search(None, "UNSEEN")
    if status != "OK":
        raise Exception("Searching for unseen mails did not return 'OK' status")

    email_ids = email_ids[0].split()

    new_print_job = False
    if len(email_ids) == 0:
        # todo: this line below can be printed if there are email found
        print('no unread mails found')
    else:
        print(f'processing {len(email_ids)} new mails')

    # Loop over email IDs and fetch emails
    for email_id in email_ids:

        status, msg_data = mail.fetch(email_id, '(RFC822)')

        if status != 'OK':
            raise Exception(f'fetching mail with id: {email_id} did not return "OK" status')

        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        print(f'processing incoming mail from: {msg.get("From")}')

        (is_valid, invalid_reason) = is_valid_print_job_request(msg)

        if is_valid:
            new_print_job = True
            print_job_name = mail_to_print_job_name(msg)
            print(f'mail from: {msg.get("From")} is valid request, create print job: {print_job_name}')
            create_print_job(msg, raw_email)
            print(f'print job: {print_job_name} created\n')

        else:
            print(f'mail from {msg.get("From")} is not a valid request because:\n {invalid_reason}, abort!\n')

    # Logout and close the connection
    mail.logout()

    if new_print_job:
        input('press ENTER to open WACHTRIJ directory')
        os.startfile(os.path.join(PRINT_DIR_HOME, 'WACHTRIJ'))
    else:
        input('press ENTER to continue...')


