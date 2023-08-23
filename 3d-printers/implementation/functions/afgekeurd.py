"""
Move a print job to the folder AFGEKEURD.
"""

import sys
import glob

from mail_functions import send_response_mail
from directory_functions import (
    job_name_to_global_path,
    copy_print_job)
from cmd_farewell_handler import remove_directory_and_close_cmd_farewell

if __name__ == '__main__':

    job_name = sys.argv[1]
    job_global_path = job_name_to_global_path(job_name)

    # send response mail
    msg_file_paths = list(glob.glob(job_global_path + "/*.msg"))

    if len(msg_file_paths) > 0:
        afgekeurd_reason = input("Why is the print job rejected?")
        if len(msg_file_paths) > 1:
            print(f'Warning! more than one: {len(msg_file_paths)} .eml files detected')
            input('press enter to send response mail. . .')

        send_response_mail(msg_file_paths[0], "standard_response.html", {'{response_text}': afgekeurd_reason})
        input('press enter to continue. . .')

    else:
        print(f'folder: {job_global_path} does not contain any '\
              '.eml files, no response mail can be send')

    copy_print_job(job_name, "AFGEKEURD")
    remove_directory_and_close_cmd_farewell()
