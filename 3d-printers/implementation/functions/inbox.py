"""
Loop over unread mail, download all valid 3D print jobs to a unique folder in WACHTRIJ.
"""

import datetime
import os
import re
from typing import Tuple

from global_variables import (
    FUNCTIONS_DIR_HOME,
    PRINT_DIR_HOME,
    ACCEPTED_PRINT_EXTENSIONS)
from create_batch_file import python_to_batch
from talk_to_sa import yes_or_no
from cmd_farewell_handler import open_wachtrij_folder_cmd_farewell
from directory_functions import make_print_job_name_unique, get_print_jobs_in_queue
from mail_functions import EmailManager 
from csv_job_tracker import JobTrackerCSV, check_health_folders
from convert_functions import mail_to_name


def create_print_job(job_name, msg) -> str:
    """ Create a 'print job' or folder in WACHTRIJ and
    put all corresponding files in the print job. """


    today = datetime.date.today()
    job_folder_name = str(today.strftime('%d')) + '-' + str(today.strftime('%m')) + '_' + job_name

    print_job_global_path = os.path.join(os.path.join(PRINT_DIR_HOME, 'WACHTRIJ', job_folder_name))
    os.mkdir(print_job_global_path)

    # Save the email as a .eml file
    msg.SaveAs(os.path.join(print_job_global_path, 'mail.msg'))

    # Save the .stl files
    for attachment in msg.Attachments:
        print(f'attachment.FileName i {attachment.FileName.lower()}')
        if attachment.FileName.lower().endswith(ACCEPTED_PRINT_EXTENSIONS):
            attachment.SaveAsFile(os.path.join(print_job_global_path, attachment.FileName))

    python_to_batch(os.path.join(FUNCTIONS_DIR_HOME, 'afgekeurd.py'), job_name)
    python_to_batch(os.path.join(FUNCTIONS_DIR_HOME, 'gesliced.py'), job_name)

    return print_job_global_path

if __name__ == '__main__':

    # open outlook
    email_manager = EmailManager()
    
    # open/create csv log
    # job_tracker = JobTrackerCSV()

    # check if all folders exist
    # print("checking and repairing printer workflow")
    # check_health_folders()

    print('searching for new mail...')

    # open outlook
    email_manager = EmailManager()
    
    # read unread mails and convert to the email format and mark them as read
    msgs = email_manager.get_new_emails()
    created_print_jobs = False


    # print how many mails are processed
    if len(msgs) == 0:
        print('no unread mails found')
    else:
        print(f'processing {len(msgs)} new mails')

    # loop over all mails, check if they are valid and create print jobs
    for msg in msgs:
        print(f'processing incoming mail from: {msg.Sender}')

        (is_valid, invalid_reason) = email_manager.is_mail_a_valid_print_job_request(msg)

        if is_valid:
            created_print_jobs = True

            sender_name = mail_to_name(str(msg.Sender))
            job_name = make_print_job_name_unique(sender_name)

            print(f'mail from: {email_manager.get_email_address(msg)} is valid request,'
                  f' create print job: {job_name}')

            print_job_global_path = create_print_job(job_name, msg)
    

            # send a confirmation mail with, "we've downloaded your mail."            
            msg_file_path = os.path.join(print_job_global_path, "mail.msg")
            email_manager.reply_to_email_from_file_using_template(msg_file_path, 
                                                                  "bijlage_gedownload.html", 
                                                                  {"{print_jobs_in_queue}": get_print_jobs_in_queue()}, 
                                                                  popup_reply=False)
            email_manager.move_email_to_verwerkt_folder(msg)

            print(f'print job: {job_name} created\n')

            # job_tracker.add_job(print_job_name=print_job_name,
            #                     sender=msg.Sender,
            #                     subject=msg.Subject,
            #                     date_sent=msg.SentOn.strftime("%Y-%m-%d"),
            #                     current_state="WACHTRIJ")
        else:
            print(f'mail from {msg.Sender} is not a valid request '
                  f'because:\n {invalid_reason}, abort!\n')

    if created_print_jobs:
        open_wachtrij_folder_cmd_farewell()
