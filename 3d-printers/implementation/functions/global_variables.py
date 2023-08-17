import json
import os

# global_path = os.path.abspath(r'C:\Users\iws\.ssh\global_variables.json')
global_path = os.path.abspath(r'C:\Users\gijsg\.ssh\global_variables.json')

with open(global_path, 'r') as json_file:
    json_data = json.load(json_file)
    REPO_DIR_HOME = json_data['REPO_DIR_HOME']
    PRINT_DIR_HOME = json_data['PRINT_DIR_HOME']
    OUTLOOK_PATH = json_data['OUTLOOK_PATH']
    LOCKHUNTER_PATH = json_data['LOCKHUNTER_PATH']
    PYTHON_PATH = json_data['PYTHON_PATH']

FUNCTIONS_DIR_HOME = os.path.join(
    REPO_DIR_HOME,
    r'3d-printers\implementation\functions')

FIGURES_DIR_HOME = os.path.join(
    REPO_DIR_HOME,
    r'3d-printers\implementation\figures')