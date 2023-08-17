#! /usr/bin/env python3

import os
import sys

from directory_functions import (
    close_python_process_and_cmd,
    job_name_to_global_path,
    copy_print_job,
    move_print_job_partly)

from talk_to_sa import choose_option, yes_or_no
from executable_functions import (
    unlock_and_delete_folder,
    python_to_batch)
from global_variables import FUNCTIONS_DIR_HOME


if __name__ == '__main__':
    """ move print job from current folder to PRINTER_AANGEZET """

    job_name = sys.argv[1]
    job_global_path = job_name_to_global_path(job_name, search_in_main_folder="GESLICED")

    # check if there multiple .gcode files
    gcode_files = [gcode_file for
                   gcode_file in os.listdir(job_global_path)
                   if gcode_file.lower().endswith('.gcode')]

    if len(gcode_files) == 0:
        print('warning! no .gcode files detected, there should .gcode in this folder')
        sys.exit(0)

    elif len(gcode_files) == 1:
        copy_print_job(job_name, 'AAN_HET_PRINTEN', source_main_folder='GESLICED')
        # create the printer_klaar.exe
        python_to_batch(os.path.join(FUNCTIONS_DIR_HOME, 'printer_klaar.py'), job_name)
        unlock_and_delete_folder(job_global_path)
        close_python_process_and_cmd()
    elif len(gcode_files) > 1:

        print(f'warning! {len(gcode_files)} .gcode files detected')
        if yes_or_no('is the entire print job now printing/printed (Y/n)?'):

            copy_print_job(job_name, 'AAN_HET_PRINTEN', source_main_folder='GESLICED')
            # create print_klaar.exe
            python_to_batch(os.path.join(FUNCTIONS_DIR_HOME, 'printer_klaar.py'), job_name)
            unlock_and_delete_folder(job_global_path)
        else:
            gcode_files_to_print_later = choose_option(
                'please select which .gcode files should be printed later', gcode_files)

            # move everything except gcode_files_to_print_later
            move_print_job_partly(job_name, gcode_files_to_print_later)
            # TODO: check if the printer_klaar.exe goes to the ./AAN_HET_PRINTEN/job_folder_name
            # TODO: and not to ./GESLICED/job_folder_name
            python_to_batch(os.path.join(FUNCTIONS_DIR_HOME, 'printer_klaar.py'), job_name)






