#! /usr/bin/env python3

# TODO: fix path toward global variables in directory helper_functions
from global_variables import *
from helper_functions import *
import imaplib
import email
import os
import re
import subprocess

from email.header import decode_header
from unidecode import unidecode

def mail_to_print_job_name(msg: str):
    """ extract senders from mail and convert to a print job name """

    from_field = msg.get("From")

    # Decode the "From" field
    decoded_sender, charset = decode_header(from_field)[0]

    # If the sender's name is bytes, decode it using the charset
    if isinstance(decoded_sender, bytes):
        decoded_sender = decoded_sender.decode(charset)

    matches = re.match(r"(.*?)\s*<(.*)>", decoded_sender)

    if matches:
        if len(matches.group(1)) > 0:
            dirty_job_name = matches.group(1)
        elif len(matches.group(2)):
            dirty_job_name = matches.group(2).split('@')[0]
        else:
            raise Exception(f"could not convert to print job name: {decoded_sender}")

    # Remove spaces and special characters from the sender's name
    return re.sub(r'[^\w\s]', '', dirty_job_name).replace(" ", "_")

def main():
    """
    Loop over inbox, download all valid 3D print jobs to a unique folder in WACHTRIJ.
    """

    # Connect to the IMAP server
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_ADRES, EMAIL_PASSWORD)
    mail.select("inbox")

    # Loop over all new mails
    status, email_ids = mail.search(None, "UNSEEN")
    if status != "OK":
        raise Exception("Searching for unseen mails did not return 'OK' status")

    email_ids = email_ids[0].split()

    if len(email_ids) == 0:
        print("no new mails")

    # Loop over email IDs and fetch emails
    for email_id in email_ids:

        status, msg_data = mail.fetch(email_id, "(RFC822)")

        if status != "OK":
            raise Exception(f"fetching mail with id: {email_id} did not return 'OK' status")

        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        # TODO: input sanitization
        if True:

            job_name = mail_to_print_job_name(msg)

            print(f"The job name is {job_name}")

            local_path = make_local_folder("WACHTRIJ/"+job_name)

            # Save the email as a .eml file
            with open(os.path.join(PRINT_DIR_HOME, local_path, "mail.eml"), "wb") as eml_file:
                eml_file.write(raw_email)

    # Logout and close the connection
    mail.logout()

    input('press ENTER to continue...')

    os.startfile(PRINT_DIR_HOME+"/WACHTRIJ")

if __name__ == '__main__':
    main()
