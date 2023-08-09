# ! /usr/bin/env python3

from global_variables import *
from helper_functions import *
import imaplib
import email
import os
import re

from email.header import decode_header

def is_print_job_name_unique(job_name: str) -> bool:
    """ check if the print job name is unqiue, return boolean """

    for folder_name in get_print_job_folder_names():
        if job_name in folder_name:
            return False

    return True

def mail_to_print_job_name(msg: str):
    """ extract senders from mail and convert to a print job name """

    if isinstance(msg, email.message.Message):
        from_field = msg.get("From")
        # Decode the "From" field
        decoded_sender, charset = decode_header(from_field)[0]

        # If the sender's name is bytes, decode it using the charset
        if isinstance(decoded_sender, bytes):
            decoded_sender = decoded_sender.decode(charset)

    elif isinstance(msg, str):
        decoded_sender = msg
    else:
        raise ValueError(f"could not convert {msg} to a job name")

    job_name = re.sub(r'[^\w\s]', '', mail_to_name(decoded_sender)).replace(" ", "_")
    # TODO: this error TypeError: decode() argument 'encoding' must be str, not None

    # check if the job name is unique
    print(f'job name is {job_name}')

    # collect all jobs names

    unique_job_name = job_name
    if not is_print_job_name_unique(unique_job_name):
        existing_job_names = [job_name]
        unique_job_name = job_name + "_(" + str(len(existing_job_names)) + ")"

        while not is_print_job_name_unique(unique_job_name):
            existing_job_names.append(unique_job_name)
            unique_job_name = job_name + "_(" + str(len(existing_job_names)) + ")"

        if len(existing_job_names) == 1:
            print(f" Warning! print job name {existing_job_names[0]} already exist, create name: {unique_job_name}")
        else:
            print(f" Warning! print job names {existing_job_names} already exist, create name: {unique_job_name}")




    return unique_job_name


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
        new_mail = False
        print("no unread mails found")
    else:
        new_mail = True

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

            local_path = make_local_folder("WACHTRIJ/" + job_name)

            # Save the email as a .eml file
            with open(os.path.join(PRINT_DIR_HOME, local_path, "mail.eml"), "wb") as eml_file:
                eml_file.write(raw_email)

            # Save .stl files
            # TODO save .stl files

            # create afgekeurd.exe
            # TODO: create afgekeurd.exe
            input("presse enter please, I am making a fodler")
            python_path = os.path.join(IMPLEMENTATION_DIR_HOME, "functions/afgekeurd.py")
            python_to_exe(python_path, os.path.join(PRINT_DIR_HOME+"/WACHTRIJ/", job_name))

            # create gesliced.exe
            # TODO: create gesliced.exe

    # Logout and close the connection
    mail.logout()

    input('press ENTER to continue...')

    if new_mail:
        os.startfile(PRINT_DIR_HOME + "/WACHTRIJ")


if __name__ == '__main__':
    main()

