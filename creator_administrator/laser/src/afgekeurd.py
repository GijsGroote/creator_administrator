"""
Move a laser job to the folder AFGEKEURD.
"""

import sys
import glob
from global_variables import gv
from laser_job_tracker import LaserJobTracker
from laser_directory_functions import move_job_to_main_folder

from src.mail_manager import create_mail_manager

from directory_functions import job_name_to_global_path




if __name__ == '__main__':

    job_name = sys.argv[1]
    job_global_path = job_name_to_global_path(gv, job_name)

    # send response mail
    msg_file_paths = list(glob.glob(job_global_path + "/*.msg"))

    if len(msg_file_paths) > 0:

        mail_manager = create_mail_manager()

        print('latest mail message:')
        mail_manager.print_mail_body_from_path(msg_file_paths[0])
        declined_reason = input("Why is the laser job rejected?")
        if len(msg_file_paths) > 1:
            print(f'Warning! more than one: {len(msg_file_paths)} .eml files detected')
            input('press enter to send response mail. . .')

        mail_manager.reply_to_email_from_file_using_template(gv,
                                        msg_file_paths[0],
                                        "DECLINED_MAIL_TEMPLATE",
                                        {'{declined_reason}': declined_reason},
                                        popup_reply=True)

        # save reason for rejection to file so others can read it later
        with open("afgekeurd_reden.txt", 'w') as file:
            file.write(declined_reason)

    else:
        print(f'folder: {job_global_path} does not contain any '\
              '.eml files, no response mail can be send')
        
    job_tracker = LaserJobTracker(gv)
    job_tracker.remove_job_from_wachtrij_material(job_name)
    job_tracker.update_job_main_folder(job_name, 'AFGEKEURD')

    move_job_to_main_folder(job_name, "AFGEKEURD")
    
