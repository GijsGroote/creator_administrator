import os

import email
import subprocess
from email import generator
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_response_mail(incoming_mail_path, response_text):
    # Load the original email
    with open(incoming_mail_path, 'r') as file:
        original_email = email.message_from_file(file)

    tbirdPath = '/usr/bin/thunderbird'
    to = original_email["From"]
    subject = 'Re: ' + original_email['Subject']
    body = f"""<html><body>
        <p>Hi {original_email["From"]}</p> 
        <h3>{response_text}</h3>
        <p>Kind regards<br><br> The IWS </p> 
    </body></html>"""
    composeCommand = 'format=html,to={},subject={},body={}'.format(to, subject, body)
    subprocess.Popen([tbirdPath, '-compose', composeCommand])


# def write_eml_file(mail):

#     # filename = str(uuid.uuid4()) + ".eml"
#     filename = str("response.eml")

#     with open(filename, 'w') as file:
#         emlGenerator = generator.Generator(file)
#         emlGenerator.flatten(mail)


def main():

    # hard coded parameters, replace these
    incoming_mail_path = os.path.abspath("can_i_print.eml")

    response_text = "Your print was ugly I am not going to print that"

    # create a respond mail
    send_response_mail(incoming_mail_path, response_text)


if __name__ == '__main__':
    main()


