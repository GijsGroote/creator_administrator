#! /usr/bin/env python3

import sys
import glob

from global_variables import *
from directory_functions import *
from mail_functions import *


def create_afgekeurd(job_name):
    """ move print job from current folder to AFGEKEURD folder and popup a email response """

    # TODO: make a find folder function
    print_job_path = find_print_job_folder_from_name(job_name)

    print("the print job path")
    print(print_job_path)

    # send response mail
    afgekeurd_reason = input("Waarom is dit afgekeurd?")
    eml_file_paths = [eml_file for eml_file in glob.glob(print_job_path + "/*.eml")]

    if len(eml_file_paths) == 1:
        send_response_mail(eml_file_paths[0], afgekeurd_reason)
    elif len(eml_file_paths) > 1:
        print('more than one!')
        # TODO: which mail to respond to?
    else:
        print(f'folder: {print_job_path} does not contain any .eml files, no response mail is send')

    print(print_job_path)
    print(os.path.join(PRINT_DIR_HOME + "/AFGEKEURD/", job_name))
    move_print_job(print_job_path, os.path.join(PRINT_DIR_HOME, "AFGEKEURD", job_name))

    input("press any key to continue")


if __name__ == '__main__':
    create_afgekeurd(sys.argv[1])
