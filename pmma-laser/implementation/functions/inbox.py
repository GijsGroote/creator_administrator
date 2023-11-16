"""
Loop over unread mail, download all valid laser jobs to a unique folder in WACHTRIJ.
"""

import datetime
import os

from global_variables import *
from job_tracker import JobTracker

from src.batch import python_to_batch
from src.cmd_farewell_handler import open_wachtrij_folder_cmd_farewell
from src.directory_functions import make_laser_job_name_unique, get_laser_jobs_in_queue
from src.mail_functions import EmailManager
from src.convert_functions import mail_to_name


def create_laser_job(job_name: str, msg) -> str:
    """ Create a 'laser job' or folder in WACHTRIJ and
    put all corresponding files in the laser job. """

    today = datetime.date.today()
    job_folder_name = str(today.strftime('%d')) + '-' + str(today.strftime('%m')) + '_' + job_name

    laser_job_global_path = os.path.join(os.path.join(PMMA_LASER_DIR_HOME, 'WACHTRIJ', job_folder_name))
    os.mkdir(laser_job_global_path)

    # Save the email
    msg.SaveAs(os.path.join(laser_job_global_path, 'mail.msg'))

    # Save the files
    for attachment in msg.Attachments:
        print(f'Downloaded file: {attachment.FileName.lower()}')
        if attachment.FileName.lower().endswith(ACCEPTED_LASER_EXTENSIONS):
            attachment.SaveAsFile(os.path.join(laser_job_global_path, attachment.FileName))

    python_to_batch(os.path.join(FUNCTIONS_DIR_HOME, 'afgekeurd.py'), job_name)
    python_to_batch(os.path.join(FUNCTIONS_DIR_HOME, 'laser_klaar.py'), job_name)

    JobTracker().add_job(job_name, "WACHTRIJ")

    return laser_job_global_path

if __name__ == '__main__':

    job_tracker = JobTracker()
    job_tracker.check_health()

    print('searching for new mail...')
    email_manager = EmailManager()

    # read unread mails and convert to the email format and mark them as read
    msgs = email_manager.get_new_emails()
    created_laser_jobs = False

    # laser how many mails are processed
    if len(msgs) == 0:
        print('no unread mails found')
    else:
        print(f'processing {len(msgs)} new mails')

    # loop over all mails, check if they are valid and create laser jobs
    for msg in msgs:
        print(f'processing incoming mail from: {msg.Sender}')

        (is_valid, invalid_reason) = email_manager.is_mail_a_valid_laser_job_request(msg)

        if is_valid:
            created_laser_jobs = True

            sender_name = mail_to_name(str(msg.Sender))
            job_name = make_laser_job_name_unique(sender_name)

            print(f'mail from: {email_manager.get_email_address(msg)} is valid request,'
                  f' create laser job: {job_name}')

            laser_job_global_path = create_laser_job(job_name, msg)

            # send a confirmation mail
            msg_file_path = os.path.join(laser_job_global_path, "mail.msg")
            email_manager.reply_to_email_from_file_using_template(msg_file_path,
                                      "received.html",
                                      {"{laser_jobs_in_queue}": get_laser_jobs_in_queue()},
                                      popup_reply=False)

            # email_manager.move_email_to_verwerkt_folder(msg)

            print(f'laser job: {job_name} created\n')

        else:
            print(f'mail from {msg.Sender} is not a valid request '
                  f'because:\n {invalid_reason}, abort!\n')

    if created_laser_jobs:
        open_wachtrij_folder_cmd_farewell()
