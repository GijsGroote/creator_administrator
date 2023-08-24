import win32com.client
import os
from global_variables import EMAIL_TEMPLATES_DIR_HOME


class EmailManager:
    """
    Class for managing emails using win32com.client
    can be used to:
    - get unread emails
    - save emails to file
    - reply to emails
    - reply to emails from file
    """
    def __init__(self):
        self.outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
        self.inbox = self.outlook.GetDefaultFolder(6)


    def get_unread_emails(self):
        """get all unread emails from inbox"""
        unread_emails = []
        for message in self.inbox.Items:
            if message.UnRead:
                unread_emails.append(message)
        return unread_emails


    def save_emails(self, emails, folder):
        """save list of emails to file"""
        for email in emails:
            self.save_email(email, folder, filename=f"{email.Sender}.msg")


    def save_email(self, email, folder, filename="email.msg"):
        """save email to file"""
        email.SaveAs(os.path.join(folder, filename))

    def reply_to_email(self, email, reply_body=""):
        """reply to email that is in mailitem format"""
        reply = email.Reply()
        reply.HTMLBody = reply_body + "\n" + reply.HTMLBody
        reply.Display(True)

    def reply_to_email_from_file(self, file_path, reply_body=""):
        """reply to email that is saved to .msg file"""
        msg = self.outlook.OpenSharedItem(file_path)
        self.reply_to_email(msg, reply_body=reply_body)
        
    def reply_to_email_from_file_using_template(self, file_path, template_file_name, template_content):
        """reply to email that is saved to .msg file"""
        template_path = os.path.join(EMAIL_TEMPLATES_DIR_HOME, template_file_name)
        msg = self.outlook.OpenSharedItem(file_path)
        sender_name = msg.SenderName
        
        with open(template_path, "r") as file:
            html_content = file.read()
        
        html_content = html_content.replace("{recipient_name}", sender_name)
        
        for key, value in template_content.items():
            html_content = html_content.replace(key, value)
        
        self.reply_to_email(msg, reply_body=html_content)
        
    
# if __name__ == '__main__':
#     mail_manager = EmailManager()
#     unread_emails = mail_manager.get_unread_emails()
#     mail_manager.save_emails(unread_emails, "C:\\Users\\levij\\Programming\\IWS\\laserhok-workflow\\3d-printers\\implementation\\functions")
#

