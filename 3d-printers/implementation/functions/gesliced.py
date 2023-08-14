#! /usr/bin/env python3

import os
import sys

from directory_functions import job_name_to_global_path, move_print_job
from executable_functions import read_job_name_file


if __name__ == '__main__':
    """ move print job from WACHTRIJ to GESLICED folder """

    job_name = read_job_name_file()
    job_global_path = job_name_to_global_path(job_name, search_in_main_folder='WACHTRIJ')

    gcode_files = [gcode_file for
                   gcode_file in os.listdir(job_global_path)
                   if gcode_file.lower().endswith('.gcode')]

    if len(gcode_files) == 0:
        print(f'warning! no .gcode files detected, slice .stl files first')
        input("press any key to continue")
        sys.exit(0)

    input("press any key to continue")
    move_print_job(job_name, 'GESLICED', source_main_folder='WACHTRIJ')

    # todo: make the printer_aangezet.exe
