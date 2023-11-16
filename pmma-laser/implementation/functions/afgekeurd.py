"""
Move a laser job to the folder AFGEKEURD.
"""

import sys
import glob

from mail_functions import EmailManager
from directory_functions import (
    job_name_to_global_path,
    copy_laser_job)
from cmd_farewell_handler import remove_directory_and_close_cmd_farewell
from job_tracker import JobTracker

if __name__ == '__main__':

    job_name = sys.argv[1]
    job_global_path = job_name_to_global_path(job_name)

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

        email_manager.reply_to_email_from_file_using_template(msg_file_paths[0],
                                                        "declined.html",
                                                        {'{declined_reason}': declined_reason},
                                                        popup_reply=True)

        # save reason for rejection to file so others can read it later
        with open("afgekeurd_reden.txt", 'w') as file:
            file.write(declined_reason)

    else:
        print(f'folder: {job_global_path} does not contain any '\
              '.eml files, no response mail can be send')

    JobTracker().update_job_main_folder(job_name, "AFGEKEURD")
    copy_laser_job(job_name, "AFGEKEURD")
    remove_directory_and_close_cmd_farewell()
