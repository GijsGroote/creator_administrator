"""
Loop over unread mail, download all valid 3D print jobs to a unique folder in WACHTRIJ.
"""

import datetime
import os
import re
from typing import Tuple

from global_variables import (
    FUNCTIONS_DIR_HOME,
    PRINT_DIR_HOME)

from create_batch_file import python_to_batch
from mail_functions import mail_to_name
from talk_to_sa import yes_or_no

from convert_functions import convert_win32_msg_to_email_msg
from cmd_farewell_handler import open_wachtrij_folder_cmd_farewell
from mail_functions import (
    is_mail_a_valid_print_job_request,
    mail_to_print_job,
    mail_to_print_job_name)
from directory_functions import (
    get_print_job_folder_names,
)

from email_manager import EmailManager

def is_print_job_name_unique(job_name: str) -> bool:
    """ Check if the print job name is unique, return boolean. """

    # TODO (AGAIN): job A_B is creatd, A_B_(1) is created,  A_B is removed.
    # Using this function
    # the job called A_B will return job A_B_(1), which IS A DIFFERENT JOB
    # edit this function so that it raises a valueError('no job found')
    # when A_B is searched but only A_B_(1) is present

    for folder_name in get_print_job_folder_names():
        if job_name in folder_name:
            return False

    return True


def mail_to_print_job_name(msg) -> str:
    """ Extract senders from mail and convert to a print job name. """

    sender = str(msg.Sender)

    job_name = re.sub(r'[^\w\s]', '', mail_to_name(sender)).replace(' ', '_')

    # check if print job name is unique
    unique_job_name = job_name
    if not is_print_job_name_unique(unique_job_name):
        existing_job_names = [job_name]
        unique_job_name = job_name + '_(' + str(len(existing_job_names)) + ')'

        while not is_print_job_name_unique(unique_job_name):
            existing_job_names.append(unique_job_name)
            unique_job_name = job_name + '_(' + str(len(existing_job_names)) + ')'

        if len(existing_job_names) == 1:
            print(f'Warning! print job name {existing_job_names[0]} already exist,'\
                    f'create name: {unique_job_name}')
        else:
            print(f'Warning! print job names {existing_job_names} already exist,'\
                f'create name: {unique_job_name}')

    return unique_job_name


def is_valid_print_job_request(msg) -> Tuple[bool, str]:
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

if __name__ == '__main__':

    print('searching for new mail...')

    # open outlook
    email_manager = EmailManager()

    # read unread mails and convert to the email format and mark them as read
    msgs = email_manager.get_unread_emails()
    created_print_jobs = False

    # print how many mails are processed
    if len(msgs) == 0:
        print('no unread mails found')
    else:
        print(f'processing {len(msgs)} new mails')

    # loop over all mails, check if they are valid and create print jobs
    for msg in msgs:
        print(f'processing incoming mail from: {msg.Sender}')

        (is_valid, invalid_reason) = is_mail_a_valid_print_job_request(msg)

        if is_valid:
            created_print_jobs = True
            print_job_name = mail_to_print_job_name(msg)
            print(f'mail from: {msg.Sender} is valid request,'
                  f' create print job: {print_job_name}')

            mail_to_print_job(msg, msg.as_bytes())

            print(f'print job: {print_job_name} created\n')

        else:
            print(f'mail from {msg.Sender} is not a valid request '
                  f'because:\n {invalid_reason}, abort!\n')

    # open the 'WACHTRIJ' folder if new print jobs are created
    if created_print_jobs:
        open_wachtrij_folder_cmd_farewell()
