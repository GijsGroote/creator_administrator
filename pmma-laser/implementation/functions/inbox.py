"""
Loop over unread mail, download all valid laser jobs to a unique folder in WACHTRIJ.
"""

import datetime
import os
import json


from global_variables import gv


from src.create_batch_file import python_to_batch
from src.job_tracker import JobTracker
from src.cmd_farewell_handler import open_wachtrij_folder_cmd_farewell
from src.directory_functions import get_jobs_in_queue
from src.mail_functions import EmailManager
from src.convert_functions import mail_to_name, make_job_name_unique
from src.talk_to_sa import choose_one_option


def create_laser_job(job_name: str, msg) -> str:
    """ Create a 'laser job' or folder in WACHTRIJ and
    put all corresponding files in the laser job. """

    today = datetime.date.today()
    job_folder_name = str(today.strftime('%d')) + '-' + str(today.strftime('%m')) + '_' + job_name

    laser_job_global_path = os.path.join(os.path.join(gv['JOBS_DIR_HOME'], 'WACHTRIJ', job_folder_name))
    os.mkdir(laser_job_global_path)

    # Save the email
    msg.SaveAs(os.path.join(laser_job_global_path, 'mail.msg'))
    email_manager = EmailManager()
    laser_cut_files_dict = {}

    # Save the files
    for attachment in msg.Attachments:
        if attachment.FileName.lower().endswith(gv['ACCEPTED_EXTENSIONS']):
            # print(f'mail from {str(msg.Sender)}:')
            # email_manager.print_mail_content(os.path.join(laser_job_global_path, 'mail.msg'))

            # material = choose_one_option(f'\nWhat material is: {attachment.FileName.lower()}?\n', ['PMMA', 'Wood'], 'something else')
            # if material == 'something else':
            #     material = input(f'type the material of: {attachment.FileName.lower()}?')
            
            # email_manager.print_mail_content(os.path.join(laser_job_global_path, 'mail.msg'))
            # thickness = choose_one_option(f'\nWhat thicness is: {attachment.FileName.lower()}?\n', ['1mm', '2mm', '3mm', '4mm', '5mm', '6mm'], 'something else')
            # if thickness == 'something else':
            #     thickness = input(f'what is the thickness of: {attachment.FileName.lower()} in mm?')

            # email_manager.print_mail_content(os.path.join(laser_job_global_path, 'mail.msg'))
            
            # try:
            #     how_many_str = input('how many (default=1)?')
            #     how_many = int(how_many_str)
            # except Exception as e:
            #     how_many = 1

            # laser_cut_files_dict[attachment.FileName] = {'material': material,
            #                                 'thickness': thickness,
            #                                 'how_many': how_many,
            #                                 'done': False}
            # print(laser_cut_files_dict[attachment.FileName])
 
            material = 'steel'
            thickness = '3'
            how_many =  '4'
            laser_cut_files_dict[attachment.FileName] = {'material': material,
                            'thickness': thickness,
                            'how_many': how_many}



            with open(os.path.join(laser_job_global_path, 'laser_cut_files_log.json'), 'w') as laser_cut_files_log:
                json.dump(laser_cut_files_dict, laser_cut_files_log, indent=4)
            attachment.SaveAsFile(os.path.join(laser_job_global_path, material+'_'+thickness+'mm_'+how_many+'x_'+attachment.FileName)) 

    python_to_batch(gv, os.path.join(gv['FUNCTIONS_DIR_HOME'], 'afgekeurd.py'), job_name)
    python_to_batch(gv, os.path.join(gv['FUNCTIONS_DIR_HOME'], 'laser_klaar.py'), job_name)

    JobTracker(gv).add_job(job_name, "WACHTRIJ")

    return laser_job_global_path

if __name__ == '__main__':

    job_tracker = JobTracker(gv)
    job_tracker.check_health(gv)

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

            email_manager.move_email_to_verwerkt_folder(msg)

            print(f'laser job: {job_name} created\n')

        else:
            print(f'mail from {msg.Sender} is not a valid request '
                  f'because:\n {invalid_reason}, abort!\n')

    if created_laser_jobs:
        open_wachtrij_folder_cmd_farewell()
