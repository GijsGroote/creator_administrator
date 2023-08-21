"""
Extract information from input.
"""

from typing import List
import re

def gcode_files_to_max_print_time(gcode_files: List[str]) -> str:
    """ Get the maximum print time from list of gcode files. """
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

    email_body = MIMEText(message.Body, _charset="utf-8")
    email_msg.attach(email_body)

    # Loop over attachments and add them to the email message
    for attachment in message.Attachments:
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
