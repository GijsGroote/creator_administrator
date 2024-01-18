"""
Global variables specific for the local machine managing the PMMA laser.
"""

import json
import os
import sys
from PyQt5.QtCore import QThreadPool

if sys.platform == 'linux':
    data_dir_home = os.path.join(os.path.expanduser('~'), '.creator-administrator')
elif sys.platform == 'win32':
    data_dir_home = os.path.join(os.getenv('LOCALAPPDATA'), 'creator-administrator')
else: 
    raise ValueError(f'This software does not work for platform: {sys.platform}')

if not os.path.exists(data_dir_home):
    os.mkdir(data_dir_home)
    
global_variables_path = os.path.join(data_dir_home, 'laser_global_variables.json')
jobs_dir_home = os.path.join(data_dir_home, 'laser_jobs')
tracker_file_path = os.path.join(data_dir_home, 'laser_job_log.json')

if not os.path.exists(global_variables_path):
    with open(global_variables_path, 'w') as gv_file:
        json.dump(dict(), gv_file, indent=4)

if not os.path.exists(jobs_dir_home):
    os.mkdir(jobs_dir_home)
    
# Global Variables (gv)
gv = {'DATA_DIR_HOME': data_dir_home,
      'JOBS_DIR_HOME': jobs_dir_home,
      'TRACKER_FILE_PATH': tracker_file_path}
print(data_dir_home)
# TODO: if this is not all in the file, do a setup wizard please
with open(global_variables_path, 'r') as global_variables_file:
    gv_data = json.load(global_variables_file)
    gv['REPO_DIR_HOME'] = gv_data['REPO_DIR_HOME']
    gv['PYTHON_PATH'] = gv_data['PYTHON_PATH']
    gv['OUTLOOK_PATH'] = gv_data['OUTLOOK_PATH']
    gv['ACCEPTED_EXTENSIONS'] = tuple(gv_data['ACCEPTED_EXTENSIONS'].split(', '))
    gv['ACCEPTED_MATERIALS'] = tuple(gv_data['ACCEPTED_MATERIALS'].split(', '))
    gv['DAYS_TO_KEEP_JOBS'] = gv_data['DAYS_TO_KEEP_JOBS']
    gv['ONLY_UNREAD_MAIL'] = gv_data['ONLY_UNREAD_MAIL']
    


    # TODO: these should be checked, because if MAIL_NAME is not in gv, errors
    if 'MAIL_NAME' in gv_data:
        gv['MAIL_NAME'] = gv_data['MAIL_NAME']
    if 'MAIL_ADRESS' in gv_data:
        gv['MAIL_ADRESS'] = gv_data['MAIL_ADRESS']
    if 'MAIL_PASSWORD' in gv_data:
        gv['MAIL_PASSWORD'] = gv_data['MAIL_PASSWORD']

    if 'MAIL_INBOX_NAME' in gv_data:
        gv['MAIL_INBOX_NAME'] = gv_data['MAIL_INBOX_NAME']
    else:
        gv['MAIL_INBOX_NAME'] = 'Inbox'

    gv['MOVE_MAILS_TO_VERWERKT_FOLDER'] = gv_data['MOVE_MAILS_TO_VERWERKT_FOLDER']
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

gv['THREAD_POOL'] = QThreadPool() # the one and only threadpool
