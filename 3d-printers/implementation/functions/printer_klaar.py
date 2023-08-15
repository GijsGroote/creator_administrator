#! /usr/bin/env python3

import glob
import sys
import os


from mail_functions import send_response_mail
from directory_functions import (
    job_name_to_global_path,
    copy_print_job,
    does_job_exist_in_main_folder,
    job_name_to_job_folder_name)
from executable_functions import (
    read_job_name_file,
    unlock_and_delete_folder)
from talk_to_sa import yes_or_no


if __name__ == '__main__':
    """ move print to VERWERKT and send response mail """

    job_name = read_job_name_file()
    job_global_path = job_name_to_global_path(
        job_name, search_in_main_folder='AAN_HET_PRINTEN')

    if does_job_exist_in_main_folder(job_name, "GESLICED"):
        job_name_folder = {job_name_to_job_folder_name(
            job_name, search_in_main_folder="GESLICED")}
        print(f'Warning! found GESLICED/{job_name_folder}, the print job is not yet ready')
        if yes_or_no(f'do you want to open GESLICED/{job_name_folder} (Y/n)?'):
            os.startfile(job_name_to_global_path(job_name, search_in_main_folder='GESLICED'))
            sys.exit(0)
        elif not yes_or_no('you are really sure this print job is done (Y/n)?'):
            input('aborting, press enter to close...')
            sys.exit(0)

    # send response mail
    eml_file_paths = [eml_file for eml_file in glob.glob(job_global_path + "/*.eml")]

    if len(eml_file_paths) > 1:
        print(f'Warning! more than one: {len(eml_file_paths)} .eml files detected')
        input('press enter to send response mail...')

    if len(eml_file_paths) > 0:
        # TODO: this is not a proper response mail bro, fix that
        send_response_mail(eml_file_paths[0], "Your print is finito, you can pick it up")
    else:
        print(f'folder: {job_global_path} does not contain any .eml files, no response mail can be send')

    input('press enter if the print is ready mail has been sent')
    copy_print_job(job_name, "VERWERKT", source_main_folder='AAN_HET_PRINTEN')
    unlock_and_delete_folder(job_global_path)


