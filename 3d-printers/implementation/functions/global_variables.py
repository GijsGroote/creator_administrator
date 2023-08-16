import json
import os

# global paths
REPO_DIR_HOME = r'C:\Users\gijsg\Documents\laserhok-workflow'
FUNCTIONS_DIR_HOME = os.path.join(
    REPO_DIR_HOME,
    r'3d-printers\implementation\functions')

FIGURES_DIR_HOME = os.path.join(
    REPO_DIR_HOME,
    r'3d-printers\implementation\figures')

PRINT_DIR_HOME = r'C:\Users\gijsg\Desktop\3d-print-test-env'
OUTLOOK_PATH = r'C:\Program Files\Microsoft Office\root\Office16\OUTLOOK.EXE'
LOCKHUNTER_PATH = r'C:\Program Files\LockHunter\LockHunter.exe'
PYTHON_DIR_HOME = r'C:\Users\gijsg\AppData\Local\Programs\Python\Python311\python.exe'

# email login info
IMAP_SERVER = 'outlook.office365.com'
global_path = os.path.abspath(r'C:\Users\gijsg\.ssh\mail_credentials.json')
with open(global_path, 'r') as json_file:
    json_data = json.load(json_file)
    EMAIL_ADDRESS = json_data['email']
    EMAIL_PASSWORD = json_data['password']

