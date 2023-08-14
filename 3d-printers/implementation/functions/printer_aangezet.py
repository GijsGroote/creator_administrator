#! /usr/bin/env python3

import glob
import os
import sys
from pathlib import Path

from mail_functions import send_response_mail
from directory_functions import (
    job_name_to_global_path,
    move_print_job,
    move_print_job_partly)

from talk_to_sa import choose_option, yes_or_no
from executable_functions import read_job_name_file


if __name__ == '__main__':
    """ move print job from current folder to PRINTER_AANGEZET """

    job_name = read_job_name_file()
    job_name = "Gijs_Groote"
    job_global_path = job_name_to_global_path(job_name, search_in_main_folder="GESLICED")

    # check if there multiple .gcode files
    gcode_files = [gcode_file for
                   gcode_file in os.listdir(job_global_path)
                   if gcode_file.lower().endswith('.gcode')]

    if len(gcode_files) == 0:
        print('warning! no .gcode files detected, there should .gcode in this folder')
        input('press any key to continue...')
        sys.exit(0)
    elif len(gcode_files) == 1:
        move_print_job(job_name, 'AAN_HET_PRINTEN', source_main_folder='GESLICED')
    elif len(gcode_files) > 1:
        # TODO: the following is quite annoying if there
        # TODO: are more than 5 .gcode files in a single print job

        print(f'warning! {len(gcode_files)} .gcode files detected')
        if yes_or_no('is the entire print job now printing/printed (Y/n)?'):
            move_print_job(job_name, "AAN_HET_PRINTEN")
        else:
            gcode_files_to_print_later = choose_option(
                "please select which .gcode files should be printed later", gcode_files)

            # move everything except gcode_files_to_print_later
            move_print_job_partly(job_name, gcode_files_to_print_later)

            # update both print jobs folder names
            print(gcode_files_to_print_later)

            # split the print job for the moment
            input("press any key to continue")

