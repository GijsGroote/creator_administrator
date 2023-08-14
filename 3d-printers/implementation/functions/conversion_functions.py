#! /usr/bin/env python3

from typing import List
import re

def gcode_files_to_max_print_time(gcode_files: List[str]) -> str:
    """ get the maximum print time from list of gcode files """
    max_print_time = ""
    max_print_hours = 0
    max_print_minutes = 0

    for gcode_file in gcode_files:

        pattern = r'_(\d+)h(\d+)m\.gcode'
        match = re.search(pattern, gcode_file)

        if match:
            temp_hours = int(match.group(1))
            temp_minutes = int(match.group(2))

            if (temp_hours > max_print_hours or
                    temp_hours == max_print_hours and
                    temp_minutes > max_print_minutes):
                max_print_time = str(temp_hours).zfill(2) + 'h' + \
                                 str(temp_minutes).zfill(2) + 'm_'
                max_print_hours = temp_hours
                max_print_minutes = temp_minutes

    return max_print_time


def job_folder_name_to_date(job_folder_name: str) -> str:
    """ return date from job folder name """

    match = re.search(r'.*(\d{2}-\d{2}_).*', job_folder_name)
    if match:
        return match.group(1)
    else:
        return ""