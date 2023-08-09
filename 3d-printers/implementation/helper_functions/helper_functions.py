import os
import re
import shutil
from global_variables import *
import PyInstaller.__main__
import email
import subprocess
from email import generator
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def get_print_job_absolute_paths():
    """ return full path for all print jobs """

    print_job_absolute_paths = []

    for main_folder in os.listdir(PRINT_DIR_HOME):
        temp_folders = [os.path.join(PRINT_DIR_HOME+"/"+main_folder+"/", print_job_folder) for print_job_folder in os.listdir(os.path.join(PRINT_DIR_HOME, main_folder))]

        if len(temp_folders) > 0:
            print_job_absolute_paths.extend(temp_folders)

    return print_job_absolute_paths

def get_print_job_folder_names():
    """ collect all print job folder names """

    print_job_folders = []

    for main_folder in os.listdir(PRINT_DIR_HOME):
        temp_folders = [print_job_folder for print_job_folder in os.listdir(os.path.join(PRINT_DIR_HOME, main_folder))]

        if len(temp_folders) > 0:
            print_job_folders.extend(temp_folders)

    return print_job_folders

def find_print_job_folder_from_name(print_job_name: str) -> str:
    """ return absolute path of print job folder with print_job_name """

    for print_job_folder in get_print_job_absolute_paths():
        if print_job_name in print_job_folder:
            return print_job_folder

    raise ValueError(f"no print job folder found for folder name {print_job_name}")


def mail_to_name(mail_name: str):
    """ convert mail in form first_name lastname <mail@adres.com> to a more friendly name """

    matches = re.match(r"(.*?)\s*<(.*)>", mail_name)

    if matches:
        if len(matches.group(1)) > 0:
            name = matches.group(1)
        elif len(matches.group(2)):
            name = matches.group(2).split('@')[0]
        else:
            name = mail_name

    return name


def make_local_folder(local_path: str):
    """ make a new folder"""

    assert local_path.split("/")[0] in ["AFGEKEURD", "WACHTRIJ", "GESLICED", "AAN_HET_PRINTEN", "VERWERKT"], \
        f"path {local_path} does not meet the requirements"

    unique_local_path = local_path
    if os.path.exists(os.path.join(PRINT_DIR_HOME, local_path)):
        existing_paths = [local_path]
        unique_local_path = local_path + "_(" + str(len(existing_paths)) + ")"

        while os.path.exists(os.path.join(PRINT_DIR_HOME, unique_local_path)):
            existing_paths.append(unique_local_path)
            unique_local_path = local_path + "_(" + str(len(existing_paths)) + ")"

        if len(existing_paths) == 1:
            print(f" Warning! Folder {existing_paths[0]} already exist, create folder: {unique_local_path}")
        else:
            print(f" Warning! Folders {existing_paths} already exist, create folder: {unique_local_path}")

    os.mkdir(os.path.join(PRINT_DIR_HOME, unique_local_path))

    return unique_local_path


def python_to_exe(python_path: str, local_path: str, arguments=None):
    """ convert a python file to an executable file an move to local_path. """

    assert os.path.isfile(python_path), f"file {python_path} does not exist."
    global_path = os.path.join(PRINT_DIR_HOME, local_path)
    assert os.path.exists(global_path), f"path {global_path} does not exist."

    try:
        PyInstaller.__main__.run([
            python_path,
            '--onefile',
            '--console',
            f'--distpath={global_path}',
            f'--icon={os.path.join(FIG_DIR_HOME, "download.ico")}',
            f'--python-option={arguments}',
        ])

    except FileExistsError as exc:
        print(exc)


def send_response_mail(incoming_mail_path, response_text):
    """ send a response to incoming mail """

    # Load the original email
    with open(incoming_mail_path, 'r') as file:
        original_email = email.message_from_file(file)

    subject = 'Re: ' + original_email['Subject']

    body = f"""Dear {mail_to_name(original_email['From'])},

{response_text}

Kind Regards,

The IWS
    """

    compose = '/c ipm.note'
    recipients = f'/m "{original_email["from"]}?Subject={subject}&Body={body}"'
    # attachment = f'/a {incoming_mail_path}'

    command = ' '.join([OUTLOOK_PATH, compose, recipients])
    process = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE)

def move_print_job(source_dir, target_dir):
    """ move print job from source_dir to target_dir """

    # TODO: check if source dir exist
    # check if target dir does not yet exist, and create it

    for item in os.listdir(source_dir):
        source_item = os.path.join(source_dir, item)
        target_item = os.path.join(target_dir, item)

        if os.path.isdir(source_item):
            shutil.move(source_item, target_item)
            move_print_job(source_item, target_item)
        else:
            shutil.move(source_item, target_dir)

    shutil.rmtree(source_dir)

