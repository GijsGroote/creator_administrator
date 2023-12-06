"""
Material has been made and is thus done, mark files as made and remove from the file system.
"""

import os
import sys
import subprocess

from global_variables import gv
from src.cmd_farewell_handler import remove_directory_and_close_cmd_farewell
from src.talk_to_sa import choose_option
from src.directory_functions import (
    job_name_to_global_path,
    read_json_file, write_json_file)
from src.talk_to_sa import yes_or_no


if __name__ == '__main__':

    material_dir_global_path = sys.argv[1]

    material_log_dict = read_json_file(os.path.join(material_dir_global_path, 'materiaal_log.json'))

    if yes_or_no(f'Have all files in folder {os.path.basename(material_dir_global_path)} been cut (Y/n)?'):
        files_done_keys = material_log_dict.keys()
    else:
        files_done_keys = choose_option('Which files are done?', material_log_dict.keys())
    
    # remove laser files that are done
    for file_done_key in files_done_keys:

        file_dict = material_log_dict[file_done_key]

        job_global_path = job_name_to_global_path(gv, file_dict['job_name'])
        
        # set laser file is done in laser job log
        job_log_dict = read_json_file(os.path.join(job_global_path, 'laser_job_log.json'))
        job_log_dict[file_done_key]['done'] = True
        write_json_file(job_log_dict, os.path.join(job_global_path, 'laser_job_log.json'))

        # call laser_klaar.bat if all laser files in a laser job are done 
        if all(laser_file['done'] for laser_file in job_log_dict.values()):

            print(f'laser job {os.path.basename(job_global_path)} is done, place it in the uitgifte rek')
            print(f'{os.path.basename(job_global_path)} contains:')
            for file in os.listdir(job_global_path):
                if file.endswith(gv['ACCEPTED_EXTENSIONS']):
                    print(f'    {file}')
                    
            subprocess.run([f'{os.path.join(job_global_path, "laser_klaar.bat")}'])

        # remove that file from the material folder
        os.remove(material_log_dict[file_done_key]['path_to_file_in_material_folder'])


    if len(files_done_keys) == len(material_log_dict):
        # remove material log, all files are done for this material
        remove_directory_and_close_cmd_farewell(gv)
   
    else:
        # remove laser files from material log that are done
        [material_log_dict.pop(key) for key in files_done_keys]
        write_json_file(material_log_dict, os.path.join(material_dir_global_path, 'materiaal_log.json'))

      





                                       


