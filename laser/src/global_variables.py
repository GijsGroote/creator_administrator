"""
Global variables specific for the local machine managing the PMMA laser.
"""

import json
import os
import sys

# Detect the computer.
IWS_COMPUTER = False

if sys.platform == 'linux':
    data_dir_home = os.path.join(os.path.expanduser('~'), '.creator-administrator')
elif sys.platform == 'win32':
    data_dir_home = os.path.join(os.getenv('LOCALAPPDATA'), 'creator-administrator')
else: 
    raise ValueError(f'This software does not work for platform: {sys.platform}')

if not os.path.exists(data_dir_home):
    os.mkdir(data_dir_home)

if 'iws' in data_dir_home.lower():
    IWS_COMPUTER = True
    
global_variables_path = os.path.join(data_dir_home, 'laser_global_variables.json')
jobs_dir_home = os.path.join(data_dir_home, 'laser_jobs')
tracker_file_path = os.path.join(data_dir_home, 'laser_job_log.json')

if not os.path.exists(global_variables_path):
    with open(global_variables_path, 'w') as gv_file:
        json.dump(dict(), gv_file, indent=4)

if not os.path.exists(jobs_dir_home):
    os.mkdir(jobs_dir_home)
    
# Global Variables (gv)
gv = {'IWS_COMPUTER': IWS_COMPUTER,
      'DATA_DIR_HOME': data_dir_home,
      'JOBS_DIR_HOME': jobs_dir_home,
      'TRACKER_FILE_PATH': tracker_file_path}

# TODO: if this is not all in the file, do a setup wizard please
with open(global_variables_path, 'r') as global_variables_file:
    gv_data = json.load(global_variables_file)
    gv['REPO_DIR_HOME'] = gv_data['REPO_DIR_HOME']
    gv['PYTHON_PATH'] = gv_data['PYTHON_PATH']
    gv['OUTLOOK_PATH'] = gv_data['OUTLOOK_PATH']
    gv['IOBIT_UNLOCKER_PATH'] = "there is no IOBIt UNLOCKER Any MOre" # remove this
    gv['ACCEPTED_EXTENSIONS'] = tuple(gv_data['ACCEPTED_EXTENSIONS'].split(', '))
    gv['DAYS_TO_KEEP_JOBS'] = gv_data['DAYS_TO_KEEP_JOBS']
    gv['PASSWORD'] = gv_data['PASSWORD']

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
                    'laser/email_templates', mail_template+'.html')

gv['GLOBAL_SRC_DIR'] = os.path.join(gv['REPO_DIR_HOME'], 'src')
gv['LOCAL_SRC_DIR'] = os.path.join(gv['REPO_DIR_HOME'], 'laser/src')
gv['UI_DIR_HOME'] = os.path.join(gv['REPO_DIR_HOME'], 'laser/ui')

# import functions from src
sys.path.append(gv['REPO_DIR_HOME'])
sys.path.append(gv['GLOBAL_SRC_DIR'])
sys.path.append(gv['LOCAL_SRC_DIR'])
sys.path.append(gv['UI_DIR_HOME'])

gv['FIGURES_DIR_HOME'] = os.path.join(gv['REPO_DIR_HOME'], r'figures')


gv['MAIN_FOLDERS'] = {'WACHTRIJ': {'allowed_batch_files': ['laser_klaar.bat', 'afgekeurd.bat']},
                      'VERWERKT': {'allowed_batch_files': []},
                      'AFGEKEURD': {'allowed_batch_files': []}}

gv['MINOR_FOLDERS'] = {'WACHTRIJ_MATERIAAL': {'allowed_batch_files': ['materiaal_klaar.bat']}}


from src.cmd_farewell_handler import get_cmd_farewells

gv['CMD_FAREWELLS'] = get_cmd_farewells(gv)
