"""
Global variables specific for the local machine managing the PMMA laser.
"""

import json
import os
import sys

# Detect the computer.
IWS_COMPUTER = False
pmma_laser_gv_path = r'C:\Users\PMMA laser\.ssh\pmma_laser_global_variables.json'
gijs_pmma_laser_gv_path = r'C:\Users\gijsg\.ssh\pmma_laser_global_variables.json'
if os.path.exists(pmma_laser_gv_path):
    IWS_COMPUTER = True
    global_variables_path = os.path.abspath(pmma_laser_gv_path)
    
elif os.path.exists(gijs_pmma_laser_gv_path):
    global_variables_path = os.path.abspath(gijs_pmma_laser_gv_path)
    
else:
    raise ValueError('could not find pmma_laser_global_variables.json file')

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

    for mail_template in ['RECEIVED_MAIL_TEMPLATE',
                          'DECLINED_MAIL_TEMPLATE',
                          'FINISHED_MAIL_TEMPLATE']:

        if mail_template in gv_data:
            print('does it exist?/??')
            if os.path.exists(gv_data[mail_template]):
                print(f'hey the mail template {mail_template} exists')
                gv[mail_template] = gv_data[mail_template]
            else:
                raise FileNotFoundError(f'could not find file: {gv_data[mail_template]}')
        else:
            gv[mail_template] = os.path.join(
                    gv['REPO_DIR_HOME'],
                    'pmma-laser/implementation/email_templates', mail_template+'.html')

# import functions from src
sys.path.append(gv['REPO_DIR_HOME'])

gv['FUNCTIONS_DIR_HOME'] = os.path.join(gv['REPO_DIR_HOME'],
    r'pmma-laser\implementation\functions')

gv['FIGURES_DIR_HOME'] = os.path.join(gv['REPO_DIR_HOME'], r'figures')

gv['ACCEPTED_EXTENSIONS'] = ('.dxf')

gv['DAYS_TO_KEEP_JOBS'] = 5

gv['MAIN_FOLDERS'] = {'WACHTRIJ': {'allowed_batch_files': ['laser_klaar.bat', 'afgekeurd.bat']},
                      'VERWERKT': {'allowed_batch_files': []},
                      'AFGEKEURD': {'allowed_batch_files': []}}


from src.cmd_farewell_handler import get_cmd_farewells

gv['CMD_FAREWELLS'] = get_cmd_farewells(gv)