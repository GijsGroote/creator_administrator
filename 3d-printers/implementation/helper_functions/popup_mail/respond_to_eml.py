import os

import email
import subprocess
from global_variables import OUTLOOK_PATH
from helper_functions import *
from email import generator
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_response_mail(incoming_mail_path, response_text):
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
    attachment = ' '

    command = ' '.join([OUTLOOK_PATH, compose, attachment, recipients])
    process = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE)

def main():

    # hard coded parameters, replace these
    incoming_mail_path = os.path.abspath("can_i_print.eml")

    response_text = "Your print was ugly I am not going to print that"

    # create a respond mail
    send_response_mail(incoming_mail_path, response_text)


if __name__ == '__main__':
    main()


