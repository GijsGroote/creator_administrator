"""
Extract information from input specific to the 3D printers.
"""

from typing import List
import re


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
