"""
Handle mail functionality.
"""

from typing import Tuple
import win32com.client

from src.talk_to_sa import yes_or_no
from src.convert_functions import mail_to_name

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

    def get_new_emails(self, gv: dict) -> list:
        """ Return emails from Outlook inbox. """
        msgs = []
        for message in self.inbox.Items:
            # the IWS computer appends every mail in the inbox
            if gv['IWS_COMPUTER']:
                msgs.append(message)
            # other than the IWS computer only appends unread mails
            elif message.UnRead:
                msgs.append(message)

            message.UnRead = False
            message.Save()

        # print how many mails are processed
        if len(msgs) == 0:
            print('no unread mails found')
        else:
            print(f'processing {len(msgs)} new mails')

        return msgs

    def move_email_to_verwerkt_folder(self, msg):
        """ Move email to verwerkt folder. """
        msg.Move(self.verwerkt_folder)

    def laser_mail_content(self, msg_file_path: str):
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

    def reply_to_email_from_file_using_template(self, gv: dict, 
                                                msg_file_path: str,
                                                template_file_name: str,
                                                template_content: dict,
                                                popup_reply=True):
        """ Reply to .msg file using a template. """
        msg = self.outlook.OpenSharedItem(msg_file_path)

        with open(gv[template_file_name], "r") as file:
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

    def is_mail_a_valid_job_request(self, gv: dict, msg) -> Tuple[bool, str]:
        """ Check if the requirements are met for a valid job request. """

        job_file_count = 0

        attachments = msg.Attachments

        for attachment in attachments:
            if attachment.FileName.lower().endswith(gv['ACCEPTED_EXTENSIONS']):
                job_file_count += 1

        if job_file_count == 0:
            return False, 'no {gv["ACCEPTED_EXTENSIONS"]} attachment found'

        if 5 < job_file_count <= 10:
            print(f'warning! there are: {job_file_count} '
                  f'{gv["ACCEPTED_EXTENSIONS"]} files in the mail')

        elif job_file_count > 10:
            if yes_or_no(f'{job_file_count} {gv["ACCEPTED_EXTENSIONS"]} files '
                        f'found do you want to create an job (Y/n)?'):
                return True,\
            f'you decided that: {job_file_count} {gv["ACCEPTED_EXTENSIONS"]} is oke'
            return False,\
                    f'you decided that: {job_file_count} {gv["ACCEPTED_EXTENSIONS"]} files are to much'

        return True, ' '
