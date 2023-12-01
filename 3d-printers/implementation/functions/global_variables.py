"""
Global variables specific for the local machine managing the 3D printers.
"""

import json
import os
import sys


# Detect the computer.
IWS_COMPUTER = False
if os.path.exists(r'C:\Users\IWS\.ssh\3D_print_global_variables.json'):
    IWS_COMPUTER = True
    global_variables_path = os.path.abspath(
            r'C:\Users\IWS\.ssh\3D_print_global_variables.json')

elif os.path.exists(r'C:\Users\gijsg\.ssh\3D_print_global_variables.json'):
    global_variables_path = os.path.abspath(
            r'C:\Users\gijsg\.ssh\3D_print_global_variables.json')
else:
    raise ValueError('could find 3D_print_global_variables')

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
            if os.path.exists(gv_data[mail_template]):
                gv[mail_template] = gv_data[mail_template]
            else:
                raise FileNotFoundError(f'could not find file: {gv_data[mail_template]}')
        else:
            gv[mail_template] = os.path.join(
                    gv['REPO_DIR_HOME'],
                    '3D-printers/implementation/email_templates', mail_template+'.html')

# import functions from src
print(gv['REPO_DIR_HOME'])
sys.path.append(gv['REPO_DIR_HOME'])

gv['FUNCTIONS_DIR_HOME'] = os.path.join(gv['REPO_DIR_HOME'],
    r'3d-printers\implementation\functions')

gv['FIGURES_DIR_HOME'] = os.path.join(gv['REPO_DIR_HOME'], r'figures')

gv['ACCEPTED_EXTENSIONS'] = ('.stl', '.obj', '.3mf', '.amf', '.zip.amf', '.xml', '.step', '.stp', '.zip')

gv['DAYS_TO_KEEP_JOBS'] = 5

gv['MAIN_FOLDERS'] = {'WACHTRIJ': {'allowed_batch_files': ['gesliced.bat', 'afgekeurd.bat']},
      'GESLICED': {'allowed_batch_files': ['printer_aangezet.bat', 'afgekeurd.bat']},
      'AAN_HET_PRINTEN': {'allowed_batch_files': ['printer_klaar.bat', 'afgekeurd.bat']},
      'VERWERKT': {'allowed_batch_files': []},
      'AFGEKEURD': {'allowed_batch_files': []}}

from src.cmd_farewell_handler import get_cmd_farewells

gv['CMD_FAREWELLS'] = get_cmd_farewells(gv)