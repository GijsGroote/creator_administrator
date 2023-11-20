"""
Global variables specific for the local machine.
"""

import json
import os
import sys

# Detect the computer.
IWS_COMPUTER = False
if os.path.exists(r'C:\Users\IWS\.ssh\pmma_laser_global_variables.json'):
    IWS_COMPUTER = True
    global_variables_path = os.path.abspath(
            r'C:\Users\IWS\.ssh\pmma_laser_global_variables.json')

elif os.path.exists(r'C:\Users\gijsg\.ssh\pmma_laser_global_variables.json'):
    global_variables_path = os.path.abspath(
            r'C:\Users\gijsg\.ssh\pmma_laser_global_variables.json')
else:
    raise ValueError('could find pmma_laser_global_variables')

# Global Variables (gv)
gv = {'IWS_COMPUTER': IWS_COMPUTER}

with open(global_variables_path, 'r') as global_variables_file:
    gv_data = json.load(global_variables_file)
    gv['JOBS_DIR_HOME'] = gv_data['JOBS_DIR_HOME']
    gv['REPO_DIR_HOME'] = gv_data['REPO_DIR_HOME']
    gv['TRACKER_FILE_PATH'] = gv_data['TRACKER_FILE_PATH']
    gv['PYTHON_PATH'] = gv_data['PYTHON_PATH']
    gv['OUTLOOK_PATH'] = gv_data['OUTLOOK_PATH']
    gv['IOBIT_UNLOCKER_PATH'] = gv_data['IOBIT_UNLOCKER_PATH']
    gv['PASSWORD'] = gv_data['PASSWORD']

    for mail_template in ['RECEIVED_MAIL_TEMPLATE', 'DECLINED_MAIL_TEMPLATE', 'FINISHED_MAIL_TEMPLATE']:

        if mail_template in gv_data:
            if os.path.exists(gv_data[mail_template]):
                gv[mail_template] = gv_data[mail_template]
            else:
                raise FileNotFoundError(f'could not find file: {gv_data[mail_template]}')
        else:
            gv[mail_template] = os.path.join(gv['REPO_DIR_HOME'], 'pmma-laser\\implementation\\email_templates', mail_template+'.html')



# import functions from src
sys.path.append(gv['REPO_DIR_HOME'])


gv['EMAIL_TEMPLATES_DIR_HOME'] = os.path.join(gv['REPO_DIR_HOME'],
    r'pmma-laser\implementation\email_templates')

gv['FUNCTIONS_DIR_HOME'] = os.path.join(gv['REPO_DIR_HOME'],
    r'pmma-laser\implementation\functions')

gv['FIGURES_DIR_HOME'] = os.path.join(gv['REPO_DIR_HOME'], r'figures')

gv['ACCEPTED_EXTENSIONS'] = ('.dxf')

gv['DAYS_TO_KEEP_JOBS'] = 5

gv['MAIN_FOLDERS'] = {'WACHTRIJ': 
                      {'allowed_batch_files': ['afgekeurd.bat', 'laser_klaar.bat']},
                      'VERWERKT': 
                      {'allowed_batch_files': []},
                      'AFGEKEURD': 
                      {'allowed_batch_files': []}}

