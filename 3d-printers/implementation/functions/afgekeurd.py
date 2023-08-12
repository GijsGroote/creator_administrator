#! /usr/bin/env python3

import sys
import glob

from directory_functions import *
from mail_functions import *


def create_afgekeurd(job_name):
    """ move print job from current folder to AFGEKEURD folder and popup a email response """

    # # send response mail
    # afgekeurd_reason = input("Why is the print job rejected?")
    # eml_file_paths = [eml_file for eml_file in glob.glob(print_job_path + "/*.eml")]
    #
    # if len(eml_file_paths) == 1:
    #     send_response_mail(eml_file_paths[0], afgekeurd_reason)
    # elif len(eml_file_paths) > 1:
    #     print(f'Warning! more than one: {len(eml_file_paths)} .eml files detected, respond to {eml_file_paths[0]}')
    #     send_response_mail(eml_file_paths[0], afgekeurd_reason)
    # else:
    #     print(f'folder: {print_job_path} does not contain any .eml files, no response mail can be send')

    # move_print_job(job_name, "WACHTRIJ")
    # move_print_job(job_name, "AFGEKEURD")
    move_print_job(job_name, "GESLICED")
    # move_print_job(job_name, "AAN_HET_PRINTEN")

    # input("press any key to continue")


if __name__ == '__main__':
    create_afgekeurd(sys.argv[1])
