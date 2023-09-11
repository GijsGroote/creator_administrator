"""
Global variables specific for the local machine.
"""

import json
import os

global_path = os.path.abspath(r'C:\Users\IWS\.ssh\3D_print_global_variables.json')
# global_path = os.path.abspath(r'C:\Users\levij\.ssh\3D_print_global_variables.json')
# global_path = os.path.abspath(r'C:\Users\gijsg\.ssh\3D_print_global_variables.json')

with open(global_path, 'r') as json_file:
    json_data = json.load(json_file)
    PRINT_DIR_HOME = json_data['PRINT_DIR_HOME']
    REPO_DIR_HOME = json_data['REPO_DIR_HOME']
    CSV_FILE_PATH = json_data['CSV_FILE_PATH']
    PYTHON_PATH = json_data['PYTHON_PATH']
    OUTLOOK_PATH = json_data['OUTLOOK_PATH']
    IOBIT_UNLOCKER_PATH = json_data['IOBIT_UNLOCKER_PATH']

FUNCTIONS_DIR_HOME = os.path.join(
    REPO_DIR_HOME,
    r'3d-printers\implementation\functions')

EMAIL_TEMPLATES_DIR_HOME = os.path.join(
    REPO_DIR_HOME,
    r'3d-printers\implementation\email_templates')

FIGURES_DIR_HOME = os.path.join(
    REPO_DIR_HOME,
    r'3d-printers\implementation\figures')

ACCEPTED_PRINT_EXTENSIONS = ('.stl', '.obj', '.3mf', '.amf', '.zip.amf', '.xml', '.step', '.stp')