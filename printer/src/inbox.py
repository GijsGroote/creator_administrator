"""
Loop over unread mail, download all valid 3D print jobs to a unique folder in WACHTRIJ.
"""

import datetime
import os


from global_variables import gv
from local_cmd_farewell_handler import open_wachtrij_folder_cmd_farewell

from create_batch_file import python_to_batch
from directory_functions import get_jobs_in_queue
from src.mail_manager import create_mail_manager

from convert_functions import mail_to_name, make_job_name_unique
from job_tracker import JobTracker


def create_print_job(job_name: str, msg) -> str:
    """ Create a 'print job' or folder in WACHTRIJ and
    put all corresponding files in the print job. """

    today = datetime.date.today()
    job_folder_name = str(today.strftime('%d')) + '-' + str(today.strftime('%m')) + '_' + job_name

    print_job_global_path = os.path.join(os.path.join(gv['JOBS_DIR_HOME'], 'WACHTRIJ', job_folder_name))
    os.mkdir(print_job_global_path)

    # Save the email
    msg.SaveAs(os.path.join(print_job_global_path, 'mail.msg'))

    # Save the .stl files
    for attachment in msg.Attachments:
        print(f'Downloaded file: {attachment.FileName.lower()}')
        if attachment.FileName.lower().endswith(gv['ACCEPTED_EXTENSIONS']):
            attachment.SaveAsFile(os.path.join(print_job_global_path, attachment.FileName))

    python_to_batch(gv, os.path.join(gv['FUNCTIONS_DIR_HOME'], 'afgekeurd.py'), job_name)
    python_to_batch(gv, os.path.join(gv['FUNCTIONS_DIR_HOME'], 'gesliced.py'), job_name)

    JobTracker(gv).add_job(job_name, "WACHTRIJ")

    return print_job_global_path

if __name__ == '__main__':

    job_tracker = JobTracker(gv)
    job_tracker.checkHealth(gv)

    print('searching for new mail...')
    mail_manager = create_mail_manager()
    msgs = mail_manager.getNewEmails(gv)
    created_print_jobs = False

    # loop over all mails, check if they are valid and create print jobs
    for msg in msgs:
        print(f'processing incoming mail from: {msg.Sender}')

        (is_valid, invalid_reason) = mail_manager.is_mail_a_valid_job_request(gv, msg)

        if is_valid:
            created_print_jobs = True

            sender_name = mail_to_name(str(msg.Sender))
            job_name = make_job_name_unique(gv, sender_name)

            print(f'mail from: {mail_manager.get_email_address(msg)} is valid request,'
                  f' create print job: {job_name}')

            print_job_global_path = create_print_job(job_name, msg)

            # send a confirmation mail
            msg_file_path = os.path.join(print_job_global_path, "mail.msg")
            mail_manager.reply_to_email_from_file_using_template(gv,
                                      msg_file_path,
                                      "RECEIVED_MAIL_TEMPLATE",
                                      {"{jobs_in_queue}": get_jobs_in_queue(gv)},
                                      popup_reply=False)

            mail_manager.move_email_to_verwerkt_folder(gv, msg)

            print(f'print job: {job_name} created\n')

        else:
            print(f'mail from {msg.Sender} is not a valid request '
                  f'because:\n {invalid_reason}, abort!\n')

    if created_print_jobs:
        open_wachtrij_folder_cmd_farewell()
