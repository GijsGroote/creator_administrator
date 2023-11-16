"""
Global variables specific for the local machine.
"""

import json
import os
import sys

# Detect the computer.
IWS_PMMA_LASER_COMPUTER = False
if os.path.exists(r'C:\Users\IWS\.ssh\pmma_laser_global_variables.json'):
    IWS_PMMA_LASER_COMPUTER = True
    global_variables_path = os.path.abspath(
            r'C:\Users\IWS\.ssh\pmma_laser_global_variables.json')

elif os.path.exists(r'C:\Users\gijsg\.ssh\pmma_laser_global_variables.json'):
    global_variables_path = os.path.abspath(
            r'C:\Users\gijsg\.ssh\pmma_laser_global_variables.json')

else:
    raise ValueError('could find pmma_laser_global_variables')


# custom mail templates
RECEIVED_MAIL_TEMPLATE = None
DECLINED_MAIL_TEMPLATE = None
FINISHED_MAIL_TEMPLATE = None

with open(global_variables_path, 'r') as global_variables_file:
    gv_data = json.load(global_variables_file)
    LASER_DIR_HOME = gv_data['PMMA_LASER_DIR_HOME']
    REPO_DIR_HOME = gv_data['REPO_DIR_HOME']
    TRACKER_FILE_PATH = gv_data['TRACKER_FILE_PATH']
    PYTHON_PATH = gv_data['PYTHON_PATH']
    OUTLOOK_PATH = gv_data['OUTLOOK_PATH']
    IOBIT_UNLOCKER_PATH = gv_data['IOBIT_UNLOCKER_PATH']

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

# import functions from src
sys.path.append(os.path.join(REPO_DIR_HOME, 'src'))

FUNCTIONS_DIR_HOME = os.path.join(
    REPO_DIR_HOME,
    r'pmma-laser\implementation\functions')

EMAIL_TEMPLATES_DIR_HOME = os.path.join(
    REPO_DIR_HOME,
    r'pmma-laser\implementation\email_templates')

FIGURES_DIR_HOME = os.path.join(
    REPO_DIR_HOME,
    r'figures')

ACCEPTED_LASER_EXTENSIONS = ('.dxf')

DAYS_TO_KEEP_JOBS = 5
