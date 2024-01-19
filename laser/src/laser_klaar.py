"""
Move a laser job to the folder VERWERKT.
"""

import glob
import sys

from global_variables import gv
from laser_directory_functions import move_job_to_main_folder

from src.mail_manager import create_mail_manager


from directory_functions import (
    job_name_to_global_path)

from talk_to_sa import yes_or_no
from cmd_farewell_handler import (
    remove_directory_and_close_cmd_farewell)
from laser_job_tracker import LaserJobTracker

if __name__ == '__main__':

    job_name = sys.argv[1]
    job_global_path = job_name_to_global_path(gv,
        job_name, search_in_main_folder='WACHTRIJ')

    # send response mail
    msg_file_paths = list(glob.glob(job_global_path + "/*.msg"))

    if len(msg_file_paths) > 0:

        mail_manager = create_mail_manager()

        mail_manager.reply_to_email_from_file_using_template(gv,
                                                msg_file_paths[0],
                                                "FINISHED_MAIL_TEMPLATE",
                                                {},
                                                popup_reply=False)
    else:
        print(f'folder: {job_global_path} does not contain any .msg files,'\
                f'no response mail can be send')
    
    job_tracker = LaserJobTracker(self)
    
    job_tracker.remove_job_from_wachtrij_material(job_name)
    job_tracker.update_job_main_folder(job_name, 'VERWERKT')

    move_job_to_main_folder(job_name, 'VERWERKT')
