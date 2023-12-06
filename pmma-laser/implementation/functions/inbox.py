"""
Loop over unread mail, download all valid laser jobs to a unique folder in WACHTRIJ.
"""

import datetime
import os
import json
import re
from typing import Tuple

from global_variables import gv


from src.create_batch_file import python_to_batch, python_to_batch_in_folder
# from src.job_tracker import JobTracker
from src.cmd_farewell_handler import open_wachtrij_folder_cmd_farewell
from src.directory_functions import get_jobs_in_queue, get_prefix_of_subfolders
from src.mail_functions import EmailManager
from src.convert_functions import mail_to_name, make_job_name_unique
from src.talk_to_sa import choose_one_option, yes_or_no

def enter_laser_file_details(msg, attachment) -> Tuple[str, str, str]:
    """ Return the material, thickness and amount of a laser file. """
    while True:
        if attachment.FileName.lower().endswith(gv['ACCEPTED_EXTENSIONS']):
            print(f'mail from {str(msg.Sender)}:')
            email_manager.print_mail_body(msg)
            
            material = choose_one_option(f'What material is: {attachment.FileName}?',
                        get_prefix_of_subfolders(os.path.join(gv['JOBS_DIR_HOME'], 'WACHTRIJ_MATERIAAL')),
                        options_type='material')

            thickness = ''
            while True:
                thickness = choose_one_option(f'\nWhat thickness is: {attachment.FileName}?',
                            [], options_type='thickness')
                if not thickness.endswith('mm'):
                    thickness = thickness+'mm'
                thickness = thickness.replace(',', '.')
                
                if re.search(r'^[0-9]*[.]{0,1}[0-9]*mm$', thickness):
                    break
                else:
                    print(f'could not convert {thickness} to a decimal number, try again')

            try:
                amount = input('amount (default=1)?')
                amount = str(int(amount))
            except Exception as e:
                amount = '1'

            correct = yes_or_no(f'File {attachment.FileName}: \n   material: {material}'\
                                    f'\n   thickness: {thickness}\n   amount: {amount}\n'\
                                    'is this correct (Y/n)?\n')
            if correct:
                material_dir_global_path = os.path.join(gv['JOBS_DIR_HOME'],
                                                        'WACHTRIJ_MATERIAAL', 
                                                        material+'_'+thickness)
                if not os.path.exists(material_dir_global_path):
                    os.mkdir(material_dir_global_path)
                    python_to_batch_in_folder(gv, 
                                os.path.join(gv['FUNCTIONS_DIR_HOME'], 'materiaal_klaar.py'),
                                material_dir_global_path,
                                pass_parameter=material_dir_global_path)

                return material, thickness, amount
            else:
                if yes_or_no(f'Enter laser request details again for {attachment.FileName} (Y/n)?'):
                    continue
                elif yes_or_no(f'Enter laser request details again for {attachment.FileName} (Y/n)?'):
                    return None, None, None                   
                    

def create_laser_job(job_name: str, msg) -> str:
    """ Create a 'laser job' or folder in WACHTRIJ and
    put all corresponding files in the laser job. """

    today = datetime.date.today()
    job_folder_name = str(today.strftime('%d')) + '-' + str(today.strftime('%m')) + '_' + job_name

    laser_job_global_path = os.path.join(os.path.join(gv['JOBS_DIR_HOME'], 'WACHTRIJ', job_folder_name))
    
    email_manager = EmailManager()
    laser_cut_files_dict = {}

    # Find materials, thickness and amount should cut
    for attachment in msg.Attachments:

        material, thickness, amount = enter_laser_file_details(msg, attachment)

        if material is None and thickness is None and amount is None:
            pass  # TODO: send supply information mail and move this mail

        laser_cut_files_dict[job_name + '_' + attachment.FileName] = {'material': material,
                            'thickness': thickness,
                            'amount': amount,
                            'done': False,
                            'path_to_file_in_material_folder': os.path.join(
                                gv['JOBS_DIR_HOME'], 'WACHTRIJ_MATERIAAL',
                                material+'_'+'thickness',
                                job_name + '_' + attachment.FileName)}
    # Save the email      
    os.mkdir(laser_job_global_path)   
    msg.SaveAs(os.path.join(laser_job_global_path, 'mail.msg')) 

    # Save all attachments
    for attachment in msg.Attachments:
        if attachment.FileName.lower().endswith(gv['ACCEPTED_EXTENSIONS']):
            att_key = job_name+'_'+attachment.FileName
            attachment_name = laser_cut_files_dict[att_key]['material']+'_'+\
                                    laser_cut_files_dict[att_key]['thickness']+'_'+\
                                    laser_cut_files_dict[att_key]['amount']+'x_'+\
                                    attachment.FileName
            
            attachment.SaveAsFile(os.path.join(laser_job_global_path, attachment_name))

            wachtrij_materiaal_global_path = os.path.join(gv['JOBS_DIR_HOME'], 'WACHTRIJ_MATERIAAL',
                                    laser_cut_files_dict[att_key]['material']+'_'+\
                                    laser_cut_files_dict[att_key]['thickness'])
            
            laser_file_material_folder_global_path = os.path.join(
                wachtrij_materiaal_global_path,
                job_name + '_' + attachment.FileName)
            
            attachment.SaveAsFile(laser_file_material_folder_global_path)
            material_log_global_path = os.path.join(wachtrij_materiaal_global_path, 'materiaal_log.json')

            # create materiaal_log if it does not exist
            if not os.path.exists(material_log_global_path):
                with open(material_log_global_path, 'w') as material_log_file:
                    json.dump(dict(), material_log_file, indent=4)

            with open(material_log_global_path, 'r') as material_log_file:
                material_log_dict = json.load(material_log_file)

            material_log_dict[att_key] = {
                    'file_name': attachment.FileName,
                    'job_name': job_name,
                    'material': laser_cut_files_dict[att_key]['material'],
                    'thickness': laser_cut_files_dict[att_key]['thickness'],
                    'amount': laser_cut_files_dict[att_key]['amount'],
                    'path_to_file_in_material_folder': laser_file_material_folder_global_path
                }
            with open(material_log_global_path, 'w') as material_log_file:
                json.dump(material_log_dict, material_log_file, indent=4)

    with open(os.path.join(laser_job_global_path, 'laser_job_log.json'), 'w') as laser_job_log:
        json.dump(laser_cut_files_dict, laser_job_log, indent=4)
            
    python_to_batch(gv, os.path.join(gv['FUNCTIONS_DIR_HOME'], 'afgekeurd.py'), job_name, 'WACHTRIJ')
    python_to_batch(gv, os.path.join(gv['FUNCTIONS_DIR_HOME'], 'laser_klaar.py'), job_name, 'WACHTRIJ')

    # JobTracker(gv).add_job(job_name, "WACHTRIJ")

    return laser_job_global_path

if __name__ == '__main__':

    # job_tracker = JobTracker(gv)
    # job_tracker.check_health(gv)

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
