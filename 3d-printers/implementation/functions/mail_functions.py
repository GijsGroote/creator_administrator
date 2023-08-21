"""
Handle mail functionality.
"""

import email
import subprocess
import re

from global_variables import OUTLOOK_PATH


def send_response_mail(incoming_mail_path, response_text):
    """ Send a response to incoming mail. """

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
    command = ' '.join([OUTLOOK_PATH, compose, recipients])
    process = subprocess.Popen(command, shell=False)
    process.wait()


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
