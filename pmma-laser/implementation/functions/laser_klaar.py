"""
Move a laser job to the folder VERWERKT.
"""

import glob
import sys

from mail_functions import EmailManager

from directory_functions import (
    job_name_to_global_path,
    copy_laser_job,
    does_job_exist_in_main_folder,
    job_name_to_job_folder_name)
from talk_to_sa import yes_or_no
from cmd_farewell_handler import (
    open_gesliced_folder_cmd_farewell,
    remove_directory_and_close_cmd_farewell)
from job_tracker import JobTracker

if __name__ == '__main__':

    job_name = sys.argv[1]
    job_global_path = job_name_to_global_path(
        job_name, search_in_main_folder='AAN_HET_PRINTEN')

    if does_job_exist_in_main_folder(job_name, "GESLICED"):
        job_name_folder = {job_name_to_job_folder_name(
            job_name, search_in_main_folder="GESLICED")}
        print(f'Warning! found GESLICED/{job_name_folder}, the laser job is not yet ready')
        if yes_or_no('do you want to open GESLICED/ (Y/n)?'):
            open_gesliced_folder_cmd_farewell()

        elif not yes_or_no('you are really sure this laser job is done (Y/n)?'):
            laser('aborting...')
            sys.exit(0)

    # send response mail
    msg_file_paths = list(glob.glob(job_global_path + "/*.msg"))

    if len(msg_file_paths) > 1:
        print(f'Warning! more than one: {len(msg_file_paths)} .msg files detected')
        input('press enter to send response mail...')

    if len(msg_file_paths) > 0:
        email_manager = EmailManager()
        email_manager.reply_to_email_from_file_using_template(msg_file_paths[0],
                                                              "finished.html",
                                                               {},
                                                              popup_reply=False)
    else:
        print(f'folder: {job_global_path} does not contain any .msg files,'\
                f'no response mail can be send')

    job_tracker = JobTracker()
    job_tracker.set_split_job_to(job_name, False)
    job_tracker.update_job_main_folder(job_name, "VERWERKT")

    copy_laser_job(job_name, "VERWERKT", source_main_folder='AAN_HET_PRINTEN')
    remove_directory_and_close_cmd_farewell()
