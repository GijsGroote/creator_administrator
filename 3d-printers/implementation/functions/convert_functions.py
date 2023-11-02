"""
Extract information from input.
"""

from typing import List
import os
import re
import email
import tempfile
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

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

def convert_win32_msg_to_email_msg(win32_msg) -> email.mime.multipart.MIMEMultipart:
    """ Convert a win32 message to an email message. """
    # create a new email message and copy the win32 message fields to the email message
    email_msg = MIMEMultipart()
    email_msg['From'] = win32_msg.SenderEmailAddress
    email_msg['To'] = win32_msg.To
    email_msg['Subject'] = win32_msg.Subject

    email_body = MIMEText(win32_msg.Body, _charset="utf-8")
    email_msg.attach(email_body)

    # Loop over attachments and add them to the email message
    for attachment in win32_msg.Attachments:
        # Save attachment to a temporary file
        temp_dir = tempfile.gettempdir()
        temp_filename = os.path.join(temp_dir, attachment.FileName)
        attachment.SaveAsFile(temp_filename)

        # Read attachment content and create MIMEApplication object
        with open(temp_filename, "rb") as attachment_file:
            attachment_content = attachment_file.read()

        mime_attachment = MIMEApplication(attachment_content)
        mime_attachment.add_header('content-disposition', 'attachment', filename=attachment.FileName)

        # Attach the attachment to the email
        email_msg.attach(mime_attachment)

        # Remove the temporary file
        os.remove(temp_filename)

    return email_msg

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

