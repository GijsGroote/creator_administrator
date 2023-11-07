"""
Extract information from input.
"""

from typing import List
import re


def print_job_folder_name_to_print_job_name(print_job_folder_name: str) -> str:
    """ get the print job name from a print job folder name. """

    folder_name_without_date = re.sub(r'^\d+-\d+_', '', print_job_folder_name)
    return re.sub(r'^\d+h\d+m\.', '', folder_name_without_date)

def gcode_files_to_max_print_time(gcode_files: List[str]) -> str:
    """ Get the maximum print time from list of gcode files. """
    max_print_time = ""
    max_print_hours = 0
    max_print_minutes = 0

    for gcode_file in gcode_files:

        match_days_hour_minute = re.search(r'_(\d+)d(\d+)h(\d+)m\.gcode$', gcode_file)
        match_hour_minute = re.search(r'_(\d+)h(\d+)m\.gcode$', gcode_file)
        match_minute = re.search(r'_(\d+)m\.gcode$', gcode_file)

        if match_days_hour_minute:
            temp_days = int(match_days_hour_minute.group(1))
            temp_hours = int(match_days_hour_minute.group(2)) + temp_days * 24
            temp_minutes = int(match_days_hour_minute.group(3))
        elif match_hour_minute:
            temp_hours = int(match_hour_minute.group(1))
            temp_minutes = int(match_hour_minute.group(2))
        elif match_minute:
            temp_hours = 0
            temp_minutes = int(match_minute.group(1))
        else:
            continue

        if (temp_hours > max_print_hours or
                temp_hours == max_print_hours and
                temp_minutes > max_print_minutes):
            max_print_time = str(temp_hours).zfill(2) + 'h' + \
                             str(temp_minutes).zfill(2) + 'm_'
            max_print_hours = temp_hours
            max_print_minutes = temp_minutes

    return max_print_time


def job_folder_name_to_date(job_folder_name: str) -> str:
    """ Return date from job folder name. """

    match = re.search(r'.*(\d{2}-\d{2}_).*', job_folder_name)
    if match:
        return match.group(1)
    else:
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
