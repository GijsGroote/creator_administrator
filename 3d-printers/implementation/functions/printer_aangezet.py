"""
Move a print job to the folder AFGEKEURD.
"""

import os
import sys

from global_variables import gv
from local_directory_functions import move_job_to_main_folder, move_print_job_partly

from src.directory_functions import job_name_to_global_path

from src.cmd_farewell_handler import remove_directory_and_close_cmd_farewell
from src.talk_to_sa import (
        choose_option,
        yes_or_no)


if __name__ == '__main__':

    job_name = sys.argv[1]
    job_global_path = job_name_to_global_path(gv, job_name, search_in_main_folder="GESLICED")

    # check if there are multiple .gcode files
    gcode_files = [gcode_file for
                   gcode_file in os.listdir(job_global_path)
                   if gcode_file.lower().endswith('.gcode')]

    if len(gcode_files) == 0:
        print('warning! no .gcode files detected, there should .gcode in this folder')
        sys.exit(0)

    elif len(gcode_files) == 1:
        move_job_to_main_folder(job_name, 'AAN_HET_PRINTEN', 'GESLICED')
        remove_directory_and_close_cmd_farewell(gv)

    elif len(gcode_files) > 1:

        print(f'warning! {len(gcode_files)} .gcode files detected')
        if yes_or_no('is the entire print job now printing/printed (Y/n)?'):

            move_job_to_main_folder(job_name, 'AAN_HET_PRINTEN', 'GESLICED')
            remove_directory_and_close_cmd_farewell(gv)
        else:
            gcode_files_to_print_later = choose_option(
                'please select which .gcode files should be printed later', gcode_files)

            move_print_job_partly(job_name, gcode_files_to_print_later)

    # delete old job_folder and stop python thread
    remove_directory_and_close_cmd_farewell(gv,
                            job_name=job_name, search_in_main_folder='AAN_HET_PRINTEN')
