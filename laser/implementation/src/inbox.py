"""
Loop over unread mail, download all valid laser jobs to a unique folder in WACHTRIJ.
"""

import datetime
import os
from typing import Tuple

from global_variables import gv
from job_tracker import JobTracker
from pmma_talk_to_ta import enter_material_thickness_amount

from create_batch_file import python_to_batch, python_to_batch_in_folder
from cmd_farewell_handler import open_wachtrij_folder_cmd_farewell
from directory_functions import get_jobs_in_queue, get_prefix_of_subfolders
from mail_functions import EmailManager
from convert_functions import mail_to_name, make_job_name_unique
from talk_to_sa import choose_one_option, yes_or_no


def enter_laser_file_details(msg, attachment) -> Tuple[str, str, str]:
    """ Return the material, thickness and amount of a laser file. """
    while True:
        if attachment.FileName.lower().endswith(gv['ACCEPTED_EXTENSIONS']):
            print(f'mail from {str(msg.Sender)}:')
            email_manager.print_mail_body(msg)

            material, thickness, amount = enter_material_thickness_amount(attachment.FileName)
 
        if yes_or_no(f'File {attachment.FileName}: \n   material: {material}'\
                            f'\n   thickness: {thickness}\n   amount: {amount}\n'\
                            'is this correct (Y/n)?\n'):
            return material, thickness, amount
        elif yes_or_no(f'Enter laser request details again for {attachment.FileName} (Y/n)?'):
            continue
        else:
            raise ValueError('this is not yet implemented, oh boy')                 

def save_attachments(attachments, laser_job_global_path: str) -> dict:
    """ Save all attachments on file system and logs. """
    laser_cut_files_dict = {}

    # Find materials, thickness and amount should cut
    for attachment in attachments:
        if attachment.FileName.lower().endswith(gv['ACCEPTED_EXTENSIONS']):

            material, thickness, amount = enter_laser_file_details(msg, attachment)

            if material is None and thickness is None and amount is None:
                pass  # TODO: send supply information mail and move this mail
                # send decline mail here please
            
            file_global_path = os.path.join(laser_job_global_path,
                                     material+'_'+thickness+'_'+amount+'x_'+'_'+attachment.FileName)

            laser_cut_files_dict[job_name + '_' + attachment.FileName] = {
                                'file_name': attachment.FileName,
                                'file_global_path': file_global_path,
                                'material': material,
                                'thickness': thickness,
                                'amount': amount,
                                'done': False}
            
            attachment.SaveAsFile(file_global_path)
       
    return laser_cut_files_dict

def create_laser_job(job_name: str, msg) -> str:
    """ Create a 'laser job' or folder in WACHTRIJ and
    put all corresponding files in the laser job. """

    today = datetime.date.today()
    job_folder_name = str(today.strftime('%d')) + '-' + str(today.strftime('%m')) + '_' + job_name

    laser_job_global_path = os.path.join(os.path.join(gv['JOBS_DIR_HOME'], 'WACHTRIJ', job_folder_name))
   
    # Save the email      
    os.mkdir(laser_job_global_path)   
    msg.SaveAs(os.path.join(laser_job_global_path, 'mail.msg')) 

    files_dict = save_attachments(msg.Attachments, laser_job_global_path)
            
    python_to_batch(gv, os.path.join(gv['FUNCTIONS_DIR_HOME'], 'afgekeurd.py'), job_name, 'WACHTRIJ')
    python_to_batch(gv, os.path.join(gv['FUNCTIONS_DIR_HOME'], 'laser_klaar.py'), job_name, 'WACHTRIJ')

    JobTracker().add_job(job_name, "WACHTRIJ", files_dict)

    return laser_job_global_path

if __name__ == '__main__':

    JobTracker().check_health()
    
    print('searching for new mail...')
    email_manager = EmailManager()

    # read unread mails and convert to the email format and mark them as read
    msgs = email_manager.get_new_emails(gv)
    created_laser_jobs = False

    # loop over all mails, check if they are valid and create laser jobs
    for msg in msgs:
        print(f'processing incoming mail from: {msg.Sender}')

        (is_valid, invalid_reason) = email_manager.is_mail_a_valid_job_request(gv, msg)

        if is_valid:
            created_laser_jobs = True

            sender_name = mail_to_name(str(msg.Sender))
            job_name = make_job_name_unique(gv, sender_name)

            print(f'mail from: {email_manager.get_email_address(msg)} is valid request,'
                  f' create laser job: {job_name}')

            laser_job_global_path = create_laser_job(job_name, msg)

            # send a confirmation mail
            msg_file_path = os.path.join(laser_job_global_path, "mail.msg")
            email_manager.reply_to_email_from_file_using_template(gv,
                                    msg_file_path,
                                    "RECEIVED_MAIL_TEMPLATE",
                                    {"{jobs_in_queue}": get_jobs_in_queue(gv)},
                                    popup_reply=False)

            email_manager.move_email_to_verwerkt_folder(gv, msg)

            print(f'laser job: {job_name} created\n')

        else:
            print(f'mail from {msg.Sender} is not a valid request '
                  f'because:\n {invalid_reason}, abort!\n')

    if created_laser_jobs:
        open_wachtrij_folder_cmd_farewell()
