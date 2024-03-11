"""
Global variables specific for the local machine managing the 3D printers.
"""

import json
import os
import sys

# Detect the computer.
IWS_COMPUTER = False

iws_data_dir_home = r'C:\Users\IWS\.ssh\printer_global_variables.json'
gijs_windows_data_dir_home = r'C:\Users\gijsg\AppData\creator_administrator'
gijs_linux_data_dir_home = r'/home/gijs/.creator_administrator'

if os.path.exists(iws_data_dir_home):
    IWS_COMPUTER = True
    data_dir_home = os.path.abspath(iws_data_dir_home)
    
elif os.path.exists(gijs_windows_data_dir_home):
    data_dir_home = os.path.abspath(gijs_windows_data_dir_home)

elif os.path.exists(gijs_linux_data_dir_home):
    data_dir_home = os.path.abspath(gijs_linux_data_dir_home)
else:
    raise ValueError('could not find data_dir_home')

global_variables_path = os.path.join(data_dir_home, 'printer_global_variables.json')
jobs_dir_home = os.path.join(data_dir_home, 'printer_jobs')
tracker_file_path = os.path.join(data_dir_home, 'printer_job_log.json')

assert os.path.exists(global_variables_path), f'Could not find file: {global_variables_path}'
assert os.path.exists(jobs_dir_home), f'Could not find folder: {data_dir_home}'

# Global Variables (gv)
gv = {'IWS_COMPUTER': IWS_COMPUTER,
      'DATA_DIR_HOME': data_dir_home,
      'JOBS_DIR_HOME': jobs_dir_home,
      'TRACKER_FILE_PATH': tracker_file_path}

with open(global_variables_path, 'r') as global_variables_file:
    gv_data = json.load(global_variables_file)
    gv['REPO_DIR_HOME'] = gv_data['REPO_DIR_HOME']
    gv['ACCEPTED_EXTENSIONS'] = tuple(gv_data['ACCEPTED_EXTENSIONS'].split(', '))
    gv['DAYS_TO_KEEP_JOBS'] = gv_data['DAYS_TO_KEEP_JOBS']

    for mail_template in ['RECEIVED_MAIL_TEMPLATE',
                          'DECLINED_MAIL_TEMPLATE',
                          'FINISHED_MAIL_TEMPLATE']:

        if mail_template in gv_data:
            if os.path.exists(gv_data[mail_template]):
                gv[mail_template] = gv_data[mail_template]
            else:
                raise FileNotFoundError(f'could not find file: {gv_data[mail_template]}')
        else:
            gv[mail_template] = os.path.join(
                    gv['REPO_DIR_HOME'],
                    'printer/email_templates', mail_template+'.html')

gv['GLOBAL_SRC_DIR'] = os.path.join(gv['REPO_DIR_HOME'], r'src')
gv['LOCAL_SRC_DIR'] = os.path.join(gv['REPO_DIR_HOME'],
    r'printer/src')
gv['UI_DIR_HOME'] = os.path.join(gv['REPO_DIR_HOME'],
    r'printer/ui')

# import functions from src
sys.path.append(gv['REPO_DIR_HOME'])
sys.path.append(gv['GLOBAL_SRC_DIR'])
sys.path.append(gv['LOCAL_SRC_DIR'])
sys.path.append(gv['UI_DIR_HOME'])

gv['FIGURES_DIR_HOME'] = os.path.join(gv['REPO_DIR_HOME'], r'figures')

gv['MAIN_FOLDERS'] = {'WACHTRIJ': {'allowed_batch_files': ['gesliced.bat', 'afgekeurd.bat']},
      'GESLICED': {'allowed_batch_files': ['printer_aangezet.bat', 'afgekeurd.bat']},
      'AAN_HET_PRINTEN': {'allowed_batch_files': ['printer_klaar.bat', 'afgekeurd.bat']},
      'VERWERKT': {'allowed_batch_files': []},
      'AFGEKEURD': {'allowed_batch_files': []}}

from src.cmd_farewell_handler import get_cmd_farewells

gv['CMD_FAREWELLS'] = get_cmd_farewells(gv)
