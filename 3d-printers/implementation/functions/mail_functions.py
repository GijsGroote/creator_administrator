"""
Handle mail functionality.
"""

import os
import re
from email_manager import EmailManager



def send_response_mail(incoming_mail_path: str, template: str, template_content: dict):
    """ Send a response to incoming mail. """
    email_manager = EmailManager()
    email_manager.reply_to_email_from_file_using_template(
        incoming_mail_path,
        template,
        template_content)



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

if __name__ == '__main__':
    send_response_mail(os.path.join(r'C:\Users\levij\Desktop\3d-print-test\WACHTRIJ\23-08_levijn_De_Jager', 'mail.msg'),
                       'standard_response.html',
                       {'{recipient_name}': 'levijn', '{response_text}': 'test'})