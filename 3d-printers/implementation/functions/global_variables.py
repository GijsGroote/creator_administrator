import json
import os

####################################
#### EDIT/CHECK THESE VARIABLES ####
####################################
# absolute path to the repository
REPO_DIR_HOME = r'C:\Users\IWS\Documents\laserhok-workflow'
PRINT_DIR_HOME = r'C:\Users\IWS\Desktop\test'
OUTLOOK_PATH = r'C:\Program Files\Microsoft Office\root\Office16\OUTLOOK.EXE'
LOCKHUNTER_PATH = r'C:\Program Files\LockHunter\LockHunter.exe'
PYTHON_DIR_HOME = r'C:\Users\<user>\AppData\Local\Programs\Python\Python311\python.exe'

# email login info
global_path = os.path.abspath(r'C:\Users\IWS\.ssh\mail_credentials.json')
with open(global_path, 'r') as json_file:
    json_data = json.load(json_file)
    EMAIL_ADDRESS = json_data['email']
    EMAIL_PASSWORD = json_data['password']
####################################
#### EDIT/check THESE VARIABLES ####
####################################

FUNCTIONS_DIR_HOME = os.path.join(
    REPO_DIR_HOME,
    r'3d-printers\implementation\functions')

FIGURES_DIR_HOME = os.path.join(
    REPO_DIR_HOME,
    r'3d-printers\implementation\figures')

# email imap server
IMAP_SERVER = 'outlook.office365.com'
