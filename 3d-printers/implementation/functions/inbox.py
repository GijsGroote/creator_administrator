"""
Loop over unread mail, download all valid 3D print jobs to a unique folder in WACHTRIJ.
"""

import win32com.client

from convert_functions import convert_win32_msg_to_email_msg
from cmd_farewell_handler import open_wachtrij_folder_cmd_farewell
from mail_functions import (
    is_mail_a_valid_print_job_request,
    mail_to_print_job,
    mail_to_print_job_name)

if __name__ == '__main__':

    print('searching for new mail...')

    # open outlook
    outlook = win32com.client.Dispatch('Outlook.Application').GetNamespace('MAPI')
    inbox = outlook.GetDefaultFolder(6)

    # read unread mails and convert to the email format and mark them as read
    msgs = []
    new_print_job = False
    for message in inbox.Items:
        # TODO: this is slow, loop only over unread mail (not over all mail and then use an if statement to see which are unread)
        if message.UnRead:
            converted_email = convert_win32_msg_to_email_msg(message)
            msgs.append(converted_email)
            message.UnRead = False
            message.Save()

    # print how many mails are processed
    if len(msgs) == 0:
        print('no unread mails found')
    else:
        print(f'processing {len(msgs)} new mails')

    # loop over all mails, check if they are valid and create print jobs
    for msg in msgs:
        print(f'processing incoming mail from: {msg.get("From")}')

        (is_valid, invalid_reason) = is_mail_a_valid_print_job_request(msg)

        if is_valid:
            new_print_job = True
            print_job_name = mail_to_print_job_name(msg)
            print(f'mail from: {msg.get("From")} is valid request,' \
                    f' create print job: {print_job_name}')
            mail_to_print_job(msg, msg.as_bytes())
            print(f'print job: {print_job_name} created\n')

        else:
            print(f'mail from {msg.get("From")} is not a valid request '\
                  f'because:\n {invalid_reason}, abort!\n')

    # open the 'WACHTRIJ' folder if new print jobs are created
    if new_print_job:
        open_wachtrij_folder_cmd_farewell()
