"""
Move a laser job to the folder AFGEKEURD.
"""

import sys
import glob
from global_variables import gv

from src.mail_functions import EmailManager
from local_directory_functions import move_job_to_main_folder
from src.directory_functions import job_name_to_global_path


# from src.job_tracker import JobTracker

if __name__ == '__main__':

    job_name = sys.argv[1]
    job_global_path = job_name_to_global_path(gv, job_name)

    # send response mail
    msg_file_paths = list(glob.glob(job_global_path + "/*.msg"))

    if len(msg_file_paths) > 0:

        email_manager = EmailManager()

        print('latest mail message:')
        email_manager.laser_mail_content(msg_file_paths[0])
        declined_reason = input("Why is the laser job rejected?")
        if len(msg_file_paths) > 1:
            print(f'Warning! more than one: {len(msg_file_paths)} .eml files detected')
            input('press enter to send response mail. . .')

        email_manager.reply_to_email_from_file_using_template(gv,
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

    # JobTracker().update_job_main_folder(job_name, "AFGEKEURD")
    move_job_to_main_folder(job_name, "AFGEKEURD")
    
