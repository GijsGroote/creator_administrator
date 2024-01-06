"""
Extract information from input.
"""

import re
import os
from unidecode import unidecode


def mail_to_name(mail_name: str):
    """ Convert mail in form first_name last_name <mail@adres.com> to a more friendly name. """

    matches = re.match(r"(.*?)\s*<(.*)>", mail_name)

    if matches:
        if len(matches.group(1)) > 0:
            return matches.group(1)
        if len(matches.group(2)):
            return matches.group(2).split('@')[0]
    else:
        if '@' in mail_name:
            return mail_name.split('@')[0]
    return mail_name
    
# TODO: Update make_job_name_unique 
def make_job_name_unique(gv: dict, job_name: str) -> str:
    """ Make the job name unique.

    if the job name already exists append _(NUMBER) to job name to make it unique
    if the job_name is unique but job_name_(NUMBER) exist then return job_name_(NUMBER+1).
    """
    job_name = unidecode(job_name)

    max_job_number = 0
    for folder_name in os.listdir(gv['JOBS_DIR_HOME']):

        match_job_number= re.search(rf'.*{job_name}_\((\d+)\)$', folder_name)

        if match_job_number:
            job_number = int(match_job_number.group(1))
            if job_number > max_job_number:
                max_job_number = job_number

    if max_job_number == 0:
        if does_job_name_exist(gv, job_name):
            return job_name + '_(1)'
        return job_name
    return job_name + '_(' + str(max_job_number + 1) + ')'

# TODO: This functions belongs to the job tracker
def does_job_name_exist(gv, job_name):
    return False

# def job_folder_name_to_job_name(job_folder_name: str) -> str:
#     """ get the job name from a job folder name. """

#     folder_name_without_date = re.sub(r'^\d+-\d+_', '', job_folder_name)
#     return re.sub(r'^\d+h\d+m\.', '', folder_name_without_date)

# def job_folder_name_to_date(job_folder_name: str) -> str:
#     """ Return date from job folder name. """

#     match = re.search(r'.*(\d{2}-\d{2}_).*', job_folder_name)
#     if match:
#         return match.group(1)
#     return ""


