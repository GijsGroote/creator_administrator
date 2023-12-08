"""
Material has been made and is thus done, mark files as made and remove from the file system.
"""

import os
import sys
import re
import subprocess

from global_variables import gv
from job_tracker import JobTracker



from src.cmd_farewell_handler import remove_directory_and_close_cmd_farewell
from src.talk_to_sa import choose_option
from src.cmd_farewell_handler import remove_directory_cmd_farewell
from src.directory_functions import (
    delete,
    job_name_to_global_path,
    read_json_file, write_json_file)
from src.talk_to_sa import yes_or_no


if __name__ == '__main__':

    material_dir_global_path = sys.argv[1]
    files_global_paths = os.path.basename(material_dir_global_path)
    all_file_keys = [re.sub(r'^\d+x_', '', file_key) for file_key in os.listdir(material_dir_global_path) if file_key.lower().endswith(gv['ACCEPTED_EXTENSIONS'])]

    if yes_or_no(f'Have all files in folder {os.path.basename(material_dir_global_path)} been cut (Y/n)?'):
        files_done_keys = all_file_keys
    else:
        files_done_keys = choose_option('Which files are done?', all_file_keys)
    
    JobTracker().remove_files_from_wachtrij_material(files_done_keys, call_fake_laser_klaar=True)

    # remove the material folder if all material is cut / doen / klaar
    if len(all_file_keys)-len(files_done_keys) <= 0:
        remove_directory_cmd_farewell(gv)


      





                                       


