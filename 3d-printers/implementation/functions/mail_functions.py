"""
Handle mail functionality.
"""

import os
from typing import Tuple
import win32com.client

from global_variables import (
    EMAIL_TEMPLATES_DIR_HOME,
    ACCEPTED_PRINT_EXTENSIONS,
    IWS_COMPUTER,
    RECEIVED_MAIL_TEMPLATE,
    DECLINED_MAIL_TEMPLATE,
    FINISHED_MAIL_TEMPLATE
    )

from talk_to_sa import yes_or_no
from convert_functions import mail_to_name

class EmailManager:
    """
    Class for managing emails using win32com.client.
    """
    def __init__(self):
        self.outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
        self.inbox = self.outlook.GetDefaultFolder(6)
        try:
            self.verwerkt_folder = self.inbox.Parent.Folders.Item("Verwerkt")
        except:
            self.verwerkt_folder = self.inbox.Parent.Folders.Add("Verwerkt")

    def get_new_emails(self) -> list:
        """ Return emails from Outlook inbox. """
        emails = []
        for message in self.inbox.Items:
            # the IWS computer appends every mail in the inbox
            if IWS_COMPUTER:
                emails.append(message)
            # other than the IWS computer only appends unread mails
            elif message.UnRead:
                emails.append(message)

            message.UnRead = False
            message.Save()

        return emails

    def move_email_to_verwerkt_folder(self, msg):
        """ Move email to verwerkt folder. """
        msg.Move(self.verwerkt_folder)

    def print_mail_content(self, msg_file_path: str):
        """ Print the content of an .msg file. """
        outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
        msg = outlook.OpenSharedItem(msg_file_path)

        print(msg.Body)

    def get_email_address(self, msg) -> str:
        """ Return the email adress. """
        if msg.Class==43:
            if msg.SenderEmailType=='EX':
                if msg.Sender.GetExchangeUser() is not None:
                    return msg.Sender.GetExchangeUser().PrimarySmtpAddress
                return msg.Sender.GetExchangeDistributionList().PrimarySmtpAddress
            return msg.SenderEmailAddress

        raise ValueError("Could not get email adress")

    def reply_to_email_from_file_using_template(self, msg_file_path: str,
                                                template_file_name: str,
                                                template_content: dict,
                                                popup_reply=True):
        """ Reply to .msg file using a template. """
        msg = self.outlook.OpenSharedItem(msg_file_path)

        custom_template_paths = [RECEIVED_MAIL_TEMPLATE, DECLINED_MAIL_TEMPLATE, FINISHED_MAIL_TEMPLATE]
        template_names = ["received.html", "declined.html", "finished.html"]

        if template_file_name in template_names:
            for custom_temp, temp_name in zip(custom_template_paths, template_names):
                if template_file_name == temp_name:
                    if custom_temp is not None:
                        html_template_path = custom_temp
                    else:
                        html_template_path = os.path.join(EMAIL_TEMPLATES_DIR_HOME, template_file_name)
        else:
            raise ValueError(f"unknown template: {template_file_name}")

        with open(html_template_path, "r") as file:
            html_content = file.read()

        # load recipient_name in template
        template_content["{recipient_name}"] = mail_to_name(str(msg.Sender))

        for key, value in template_content.items():
            html_content = html_content.replace(key, str(value))

        reply = msg.Reply()
        reply.HTMLBody = html_content

        if popup_reply:
            print('Send the Outlook popup reply, it can be behind other windows')
            reply.Display(True)
        else:
            reply.Send()

    def is_mail_a_valid_print_job_request(self, msg) -> Tuple[bool, str]:
        """ Check if the requirements are met for a valid print job. """

        # Initialize a counter for 3D print attachments
        print_file_count = 0

        attachments = msg.Attachments

        for attachment in attachments:
            if attachment.FileName.lower().endswith(ACCEPTED_PRINT_EXTENSIONS):
                print_file_count += 1

        if print_file_count == 0:
            return False, 'no .stl attachment found'

        if 5 < print_file_count <= 10:
            print(f'warning! there are: {print_file_count} .stl files in the mail')

        elif print_file_count > 10:
            if yes_or_no(f'{print_file_count} .stl files found do '
                        f'you want to create an print job (Y/n)?'):
                return True, f'you decided that: {print_file_count} .stl is oke'
            return False, f'you decided that: {print_file_count} .stl files are to much'

        return True, ' '
