#! /usr/bin/env python3

import sys
import glob

from mail_functions import send_response_mail
from directory_functions import (
    job_name_to_global_path,
    copy_print_job)
from executable_functions import (
    unlock_and_delete_folder)


if __name__ == '__main__':
    """ move print job from current folder to AFGEKEURD folder and popup a email response """

    job_name = sys.argv[1]
    job_global_path = job_name_to_global_path(job_name)

    # send response mail
    afgekeurd_reason = input("Why is the print job rejected?")
    eml_file_paths = [eml_file for eml_file in glob.glob(job_global_path + "/*.eml")]

    if len(eml_file_paths) > 1:
        print(f'Warning! more than one: {len(eml_file_paths)} .eml files detected')
        input('press enter to send response mail...')

    if len(eml_file_paths) > 0:
        send_response_mail(eml_file_paths[0], afgekeurd_reason)
        # TODO: this could be more robust I think
        # todo now you MUST first send response mail, then press enter
        input('press enter (after sending mail) to move print job to AFGEKEURD folder')
    else:
        print(f'folder: {job_global_path} does not contain any .eml files, no response mail can be send')

    copy_print_job(job_name, "AFGEKEURD")
    unlock_and_delete_folder(job_global_path)

