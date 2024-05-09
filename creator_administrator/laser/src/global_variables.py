'''
Global variables / Settings specific for the computer managing the laser machine.
'''

import json
import os
import sys
import shutil

# sys.path.append(os.path.abspath('../email_templates'))

from PyQt6.QtCore import QThreadPool

if sys.platform == 'linux':
    data_dir_home = os.path.join(os.path.expanduser('~'), '.creator_administrator')
elif sys.platform == 'win32':
    data_dir_home = os.path.join(os.getenv('LOCALAPPDATA'), 'Creator Administrator')
else: 
    raise ValueError(f'This software does not work for platform: {sys.platform}')

if not os.path.exists(data_dir_home):
    os.mkdir(data_dir_home)

jobs_dir_home = os.path.join(data_dir_home, 'laser_jobs')
tracker_file_path = os.path.join(data_dir_home, 'laser_job_log.json')

if not os.path.exists(jobs_dir_home):
    os.mkdir(jobs_dir_home)

temp_dir_home = os.path.join(data_dir_home, 'TEMP')
if not os.path.exists(temp_dir_home):
    os.mkdir(temp_dir_home)

for temp_item in os.listdir(temp_dir_home):
    try:
        shutil.rmtree(os.path.join(temp_dir_home, temp_item))

    except NotADirectoryError:
        os.remove(os.path.join(temp_dir_home, temp_item))

    except PermissionError:
        pass

    
settings_file_path = os.path.join(data_dir_home, 'laser_settings.json')

# Create default settings file 
if not os.path.exists(settings_file_path):

    this_file_path = os.path.dirname(os.path.realpath(__file__))
    if sys.platform == 'win32':
        repo_folder_name = r'creator_administrator\creator_administrator'
    elif sys.platform == 'linux':
        repo_folder_name = 'creator_administrator/creator_administrator'
    else:
        raise ValueError(f'Software not intended for platform {sys.platform}')
    
    if repo_folder_name in this_file_path:
        root, _ = this_file_path.split(repo_folder_name)
        repo_dir_home = os.path.join(root, repo_folder_name)
    else:
        raise ValueError(f'could not find folder {repo_folder_name}')

    desktop_dir_home = os.path.join(os.path.expanduser('~'), 'Desktop')
    if os.path.exists(desktop_dir_home):
        todo_dir_home = os.path.join(desktop_dir_home, 'Laser TODO')

    elif os.path.exists(os.path.expanduser('~')):
        todo_dir_home = os.path.join(os.path.expanduser('~'), 'Print TODO')

    else:
        raise ValueError('Could not create TODO directory')

    default_settings_dict = {
        "REPO_DIR_HOME": repo_dir_home,
        "TODO_DIR_HOME": todo_dir_home,
        "DATA_DIR_HOME": data_dir_home,
        "ACCEPTED_EXTENSIONS": ".dxf, .dwg",
        "ACCEPTED_MATERIALS": "steel, alu",
        "DAYS_TO_KEEP_JOBS": "15",
        "DARK_THEME": "true",
        "DISPLAY_TEMP_MESSAGES": "true",
        "DISPLAY_WARNING_MESSAGES": "true",
        "EMPTY_TODO_DIR_BEFORE_EXPORT": "true",
        "ONLY_UNREAD_MAIL": "false",
        "MOVE_MAILS_TO_VERWERKT_FOLDER": "true",
        "SEND_MAILS_ON_SEPERATE_THREAD": "false",
        "RECEIVED_MAIL_TEMPLATE": os.path.join(repo_dir_home, "laser/email_templates/DEFAULT_RECEIVED_MAIL_TEMPLATE.html"),
        "UNCLEAR_MAIL_TEMPLATE": os.path.join(repo_dir_home, "laser/email_templates/DEFAULT_UNCLEAR_MAIL_TEMPLATE.html"),
        "FINISHED_MAIL_TEMPLATE": os.path.join(repo_dir_home, "laser/email_templates/DEFAULT_FINISHED_MAIL_TEMPLATE.html"),
        "DECLINED_MAIL_TEMPLATE": os.path.join(repo_dir_home, "laser/email_templates/DEFAULT_DECLINED_MAIL_TEMPLATE.html")
    }

    if sys.platform == 'linux':
        default_settings_dict["MAIL_NAME"] = "Fill in Your Name"
        default_settings_dict["MAIL_INBOX_NAME"] = "Inbox"
        default_settings_dict["MAIL_ADRESS"] = "Fill in Your Mail Adress"

        default_settings_dict["MAIL_PASSWORD"]= "Fill in Your Mail Password"

    with open(os.path.join(data_dir_home, 'laser_settings.json'), 'w') as settings_file:
        json.dump(default_settings_dict, settings_file, indent=4)

    
# Global Variables (gv)
gv = {'SETTINGS_FILE_PATH': settings_file_path,
      'DATA_DIR_HOME': data_dir_home,
      'JOBS_DIR_HOME': jobs_dir_home,
      'TRACKER_FILE_PATH': tracker_file_path}

# Load settings into global variables (gv)
with open(settings_file_path, 'r') as settings_file:
    gv_data = json.load(settings_file)
    gv['REPO_DIR_HOME'] = gv_data['REPO_DIR_HOME']

    if 'MAIL_NAME' in gv_data and\
        'MAIL_ADRESS' in gv_data and\
        'MAIL_PASSWORD' in gv_data:

        gv['MAIL_NAME'] = gv_data['MAIL_NAME']
        gv['MAIL_ADRESS'] = gv_data['MAIL_ADRESS']
        gv['MAIL_PASSWORD'] = gv_data['MAIL_PASSWORD']
    
    gv['TODO_DIR_HOME'] = gv_data['TODO_DIR_HOME']

    gv['ACCEPTED_EXTENSIONS'] = tuple(gv_data['ACCEPTED_EXTENSIONS'].split(', '))
    gv['ACCEPTED_MATERIALS'] = tuple(gv_data['ACCEPTED_MATERIALS'].split(', '))

    gv['DAYS_TO_KEEP_JOBS'] = int(gv_data['DAYS_TO_KEEP_JOBS'])
    gv['DARK_THEME'] = gv_data['DARK_THEME'] == 'true'


    gv['ONLY_UNREAD_MAIL'] = gv_data['ONLY_UNREAD_MAIL'] == 'true'
    gv['MOVE_MAILS_TO_VERWERKT_FOLDER'] = gv_data['MOVE_MAILS_TO_VERWERKT_FOLDER'] == 'true'
    gv['SEND_MAILS_ON_SEPERATE_THREAD'] = gv_data['SEND_MAILS_ON_SEPERATE_THREAD'] == 'true'
    gv['EMPTY_TODO_DIR_BEFORE_EXPORT'] =  gv_data['EMPTY_TODO_DIR_BEFORE_EXPORT'] == 'true'
    gv['DISPLAY_TEMP_MESSAGES'] = gv_data['DISPLAY_TEMP_MESSAGES'] == 'true'
    gv['DISPLAY_WARNING_MESSAGES'] = gv_data['DISPLAY_WARNING_MESSAGES'] == 'true'



    if 'MAIL_INBOX_NAME' in gv_data:
        gv['MAIL_INBOX_NAME'] = gv_data['MAIL_INBOX_NAME']
    else:
        gv['MAIL_INBOX_NAME'] = 'Inbox'


    for mail_template in ('RECEIVED_MAIL_TEMPLATE',
                          'DECLINED_MAIL_TEMPLATE',
                          'FINISHED_MAIL_TEMPLATE',
                          'UNCLEAR_MAIL_TEMPLATE'):

        if mail_template in gv_data:
            print(f"found mail template in data")
            if os.path.exists(gv_data[mail_template]):
                print(f"mail template {mail_template} exists!")
                gv[mail_template] = gv_data[mail_template]
            else:

                print(f"NOOOO mail template {mail_template} exists!")
                raise FileNotFoundError(f'does Files {os.listdir(os.path.dirname(gv_data[mail_template]))} exist? {os.path.exists(os.listdir(os.path.dirname(gv_data[mail_template])))}'\
                        f'does this: {os.listdir(os.path.dirname(os.path.dirname(gv_data[mail_template])))} exist? {os.path.exists(os.path.dirname(os.path.dirname(gv_data[mail_template])))}'\
'{os.listdir(os.path.dirname(os.path.dirname(gv_data[mail_template])))}  gv_data[could not find file: {gv_data[mail_template]}')

        else:
            gv[mail_template] = os.path.join(
                    gv['REPO_DIR_HOME'],
                    'laser/email_templates', 'DEFAULT_'+mail_template+'.html')

if not os.path.exists(gv["TODO_DIR_HOME"]):
    os.mkdir(gv["TODO_DIR_HOME"])

if gv['DARK_THEME']:
    gv['GOOD_COLOR_HEX'] = '#3F643F'
    gv['BAD_COLOR_HEX'] = '#165a72'
    gv['GOOD_COLOR_RGBA'] = 'rgba(0, 255, 0, 0.7)'
    gv['BAD_COLOR_RGBA'] = 'rgba(255, 0, 0, 0.7)'
else: 
    # light theme 
    gv['GOOD_COLOR_HEX'] = '#7fc97f'
    gv['BAD_COLOR_HEX'] = '#add8e5'
    gv['GOOD_COLOR_RGBA'] = 'rgba(0, 255, 0, 0.4)'
    gv['BAD_COLOR_RGBA'] = 'rgba(255, 0, 0, 0.4)'


gv['GLOBAL_SRC_DIR'] = os.path.join(gv['REPO_DIR_HOME'], 'src')
gv['LOCAL_SRC_DIR'] = os.path.join(gv['REPO_DIR_HOME'], 'laser/src')
gv['GLOBAL_UI_DIR'] = os.path.join(gv['REPO_DIR_HOME'], 'ui')
gv['LOCAL_UI_DIR'] = os.path.join(gv['REPO_DIR_HOME'], 'laser/ui')

# import functions from src
sys.path.append(gv['REPO_DIR_HOME'])
sys.path.append(gv['GLOBAL_SRC_DIR'])
sys.path.append(gv['LOCAL_SRC_DIR'])
sys.path.append(gv['GLOBAL_UI_DIR'])
sys.path.append(gv['LOCAL_UI_DIR'])

gv['FIGURES_DIR_HOME'] = os.path.join(gv['REPO_DIR_HOME'], 'figures')

gv['THREAD_POOL'] = QThreadPool() # the one and only threadpool

# pylint: disable=consider-using-namedtuple-or-dataclass
gv['TAB_QSTACK_POSITIONS'] = {'WACHTRIJ': {'QStackedWidget': 'wachtrijQStackedWidget', 
                                   'tab_widget_position': 1},
                              'VERWERKT':
                                  {'QStackedWidget': 'verwerktQStackedWidget',
                                   'tab_widget_position': 3},
                              'AFGEKEURD':
                                  {'QStackedWidget': 'afgekeurdQStackedWidget',
                                   'tab_widget_position': 4}}
