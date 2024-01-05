"""
Loop over unread mail, download all valid laser jobs to a unique folder in WACHTRIJ.
"""

import datetime
import os
from typing import Tuple

from global_variables import gv
from laser_job_tracker import LaserJobTracker
from pmma_talk_to_ta import enter_material_thickness_amount

from src.mail_manager import MailManager 
from src.convert_functions import mail_to_name, make_job_name_unique
from src.talk_to_sa import yes_or_no


def enter_laser_file_details(mail_manager, msg, job_folder_global_path: str) -> Tuple[dict, dict]:
    """ Return the material, thickness and amount of a laser file. """

    laser_cut_files_dict = {}
    attachments_dict = {}

    for attachment in mail_manager.getAttachments(msg):
        attachment_name = mail_manager.getAttachmentFileName(attachment)

        if attachment_name.lower().endswith(gv['ACCEPTED_EXTENSIONS']):

            mail_manager.printMailBody(msg)

            material, thickness, amount = enter_material_thickness_amount(attachment_name)

            file_global_path = os.path.join(job_folder_global_path,
                                     material+'_'+thickness+'_'+amount+'x_'+'_'+attachment_name)

            laser_cut_files_dict[job_name + '_' + attachment_name] = {
                                'file_name': attachment_name,
                                'file_global_path': file_global_path,
                                'material': material,
                                'thickness': thickness,
                                'amount': amount,
                                'done': False}
            attachments_dict[attachment_name] = {'attachment': attachment,
                                                 'file_global_path': file_global_path}
        else:
            file_global_path = os.path.join(job_folder_global_path, attachment_name)
            attachments_dict[attachment_name] = {'attachment': attachment,
                                                 'file_global_path': file_global_path}


    return laser_cut_files_dict, attachments_dict


def create_laser_job(mail_manager: MailManager, job_name: str, msg) -> str:
    """ Create a 'laser job' or folder in WACHTRIJ and
    put all corresponding files in the laser job. """

    job_folder_name = str(datetime.date.today().strftime('%d-%m'))+'_'+job_name
    job_folder_global_path = os.path.join(os.path.join(gv['JOBS_DIR_HOME'], job_folder_name))

    # find material, thickness and amount
    files_dict, attachments_dict = enter_laser_file_details(mail_manager, msg, job_folder_global_path)

    LaserJobTracker().addJob(job_name, "WACHTRIJ", files_dict)

    os.mkdir(job_folder_global_path)
    mail_manager.saveMail(msg, job_folder_global_path)

    # save the attachments
    for attachment_dict in attachments_dict.values():

        mail_manager.saveAttachment(attachment_dict['attachment'], attachment_dict['file_global_path'])


    return job_folder_global_path
            

if __name__ == '__main__':

    # LaserJobTracker().checkHealth()
    
    print('searching for new mail...')
    mail_manager = MailManager(gv)

    # read unread mails and convert to the email format and mark them as read
    msgs = mail_manager.getNewEmails()

    if len(msgs) == 0:
        print('no new unread emails')

    created_laser_jobs = False

    # loop over all mails, check if they are valid and create laser jobs
    for msg in msgs:
        print(f'processing incoming mail from: {mail_manager.getEmailAddress(msg)}')

        (is_valid, invalid_reason) = mail_manager.isMailAValidJobRequest(msg)

        if is_valid:
            created_laser_jobs = True

            sender_name = mail_to_name(mail_manager.getEmailAddress(msg))
            job_name = make_job_name_unique(gv, sender_name)

            print(f'mail from: {mail_manager.getEmailAddress(msg)} is valid request,'
                  f' create laser job: {job_name}')

            job_folder_global_path = create_laser_job(mail_manager, job_name, msg)

            # send a confirmation mail
            msg_file_path = mail_manager.getMailGlobalPathFromFolder(job_folder_global_path)
            mail_manager.replyToEmailFromFileUsingTemplate(msg_file_path,
                                    "RECEIVED_MAIL_TEMPLATE",
                                    {"{jobs_in_queue}": LaserJobTracker().getNumberOfJobsInQueue()},
                                    popup_reply=False)

            # mail_manager.moveEmailToVerwerktFolder(msg)

            print(f'laser job: {job_name} created\n')

        else:
            print(f'mail from {mail_manager.getEmailAddress(msg)} is not a valid request '
                  f'because:\n {invalid_reason}, abort!\n')

