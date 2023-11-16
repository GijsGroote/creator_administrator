"""
Global variables specific for the local machine.
"""

import json
import os
import sys

# Detect the computer.
IWS_COMPUTER = False
if any([os.path.exists(r'C:\Users\IWS\.ssh\3D_print_global_variables.json'),
        os.path.exists(r'C:\Users\IWS\.ssh\pmma_laser_global_variables.json'),
        os.path.exists(r'C:\Users\IWS\.ssh\metal_laser_global_variables.json')]):
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

# custom mail templates
RECEIVED_MAIL_TEMPLATE = None
DECLINED_MAIL_TEMPLATE = None
FINISHED_MAIL_TEMPLATE = None

with open(global_variables_path, 'r') as global_variables_file:
    gv_data = json.load(global_variables_file)
    gv['JOBS_DIR_HOME'] = gv_data['JOBS_DIR_HOME']
    gv['REPO_DIR_HOME'] = gv_data['REPO_DIR_HOME']
    gv['TRACKER_FILE_PATH'] = gv_data['TRACKER_FILE_PATH']
    gv['PYTHON_PATH'] = gv_data['PYTHON_PATH']
    gv['OUTLOOK_PATH'] = gv_data['OUTLOOK_PATH']
    gv['IOBIT_UNLOCKER_PATH'] = gv_data['IOBIT_UNLOCKER_PATH']

    if "received_mail_template" in gv_data:
        if os.path.exists(gv_data["received_mail_template"]):
            RECEIVED_MAIL_TEMPLATE = gv_data["received_mail_template"]
        else:
            raise FileNotFoundError(f'could not find file: {gv_data["received_mail_template"]}')

    if "declined_mail_template" in gv_data:
        if os.path.exists(gv_data["declined_mail_template"]):
            DECLINED_MAIL_TEMPLATE = gv_data["declined_mail_template"]
        else:
            raise FileNotFoundError(f'could not find file: {gv_data["declined_mail_template"]}')

    if "finished_mail_template" in gv_data:
        if os.path.exists(gv_data["finished_mail_template"]):
            RECEIVED_MAIL_TEMPLATE = gv_data["finished_mail_template"]
        else:
            raise FileNotFoundError(f'could not find file: {gv_data["finished_mail_template"]}')

gv.update([
    ('RECEIVED_MAIL_TEMPLATE', RECEIVED_MAIL_TEMPLATE),
    ('DECLINED_MAIL_TEMPLATE', DECLINED_MAIL_TEMPLATE),
    ('FINISHED_MAIL_TEMPLATE', FINISHED_MAIL_TEMPLATE),
    ])

# import functions from src
sys.path.append(gv['REPO_DIR_HOME'])

EMAIL_TEMPLATES_DIR_HOME = os.path.join(gv['REPO_DIR_HOME'],
    r'pmma-laser\implementation\email_templates')


FUNCTIONS_DIR_HOME = os.path.join(gv['REPO_DIR_HOME'],
    r'pmma-laser\implementation\functions')

FIGURES_DIR_HOME = os.path.join(gv['REPO_DIR_HOME'], r'figures')

gv['ACCEPTED_EXTENSIONS'] = ('.dxf')

gv['DAYS_TO_KEEP_JOBS'] = 5
