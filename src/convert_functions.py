"""
Extract information from input.
"""

import re

def job_folder_name_to_job_name(job_folder_name: str) -> str:
    """ get the job name from a job folder name. """

    folder_name_without_date = re.sub(r'^\d+-\d+_', '', job_folder_name)
    return re.sub(r'^\d+h\d+m\.', '', folder_name_without_date)

def job_folder_name_to_date(job_folder_name: str) -> str:
    """ Return date from job folder name. """

    match = re.search(r'.*(\d{2}-\d{2}_).*', job_folder_name)
    if match:
        return match.group(1)
    return ""

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
