"""
Move a print job to the folder GESLICED.
"""

import os
import sys

from global_variables import gv
from local_directory_functions import move_job_to_main_folder

from src.cmd_farewell_handler import remove_directory_and_close_cmd_farewell
from src.directory_functions import job_name_to_global_path

if __name__ == '__main__':

    job_name = sys.argv[1]

    print(f'hey the job name must be {job_name}')
    job_global_path = job_name_to_global_path(gv, job_name, search_in_main_folder='WACHTRIJ')

    gcode_files = [gcode_file for
                   gcode_file in os.listdir(job_global_path)
                   if gcode_file.lower().endswith('.gcode')]

    if len(gcode_files) == 0:
        print('warning! no .gcode files detected, slice .stl files first')
        sys.exit(0)

    # moving print job creates the batch files
    move_job_to_main_folder(job_name, 'GESLICED', 'WACHTRIJ')
    remove_directory_and_close_cmd_farewell(gv)
