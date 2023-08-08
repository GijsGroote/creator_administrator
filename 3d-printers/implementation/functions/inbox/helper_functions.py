import os
import re
from global_variables import PRINT_DIR_HOME


def make_local_folder(local_path: str):
    """ make a new folder"""

    assert local_path.split("/")[0] in ["AFGEKEURD", "WACHTRIJ",  "GESLICED", "AAN_HET_PRINTEN", "VERWERKT"], \
        f"path {local_path} does not meet the requirements"

    new_local_path = local_path
    if os.path.exists(os.path.join(PRINT_DIR_HOME, local_path)):
        existing_paths = [local_path]
        new_local_path = local_path+"_("+str(len(existing_paths))+")"

        while os.path.exists(os.path.join(PRINT_DIR_HOME, new_local_path)):
            existing_paths.append(new_local_path)
            new_local_path = local_path + "_(" + str(len(existing_paths)) + ")"

        print(f" Warning! Folder(s) {existing_paths} already exist, create folder {new_local_path}")

    os.mkdir(os.path.join(PRINT_DIR_HOME, new_local_path))

    return new_local_path

# old stuf
def save_attachments(item, path):
    """
    Saves attachments from the Outlook item to a folder path

    :param item: Outlook item (email) containing all attachments
    :param path: The folder path where attachments are to be saved
    """
    attachments = item.Attachments
    for attachment in attachments:
        attachment_path = os.path.join(path, attachment.FileName)
        attachment.SaveAsFile(attachment_path)

def save_msg(item, path):
    """
    Saves Outlook emails as .msg

    :param item: Outlook item (email)
    :param path: The folder path where attachments are to be saved
    """
    email_subject = re.sub(r'[<>:"/\\|?*]', "", item.Subject)  # Remove invalid characters from the subject
    email_path = os.path.join(path, f"{email_subject}.msg")
    item.SaveAs(email_path, 3)  # Save as .msg format
    save_attachments(item, path)  # Save attachments into the folder

def move_items(move_list, wachtrij):
    """
    Moves outlook items from the inbox folder to the Verwerkt folder.

    :param move_list: List of outlook items to be moved.
    :param wachtrij: Path to the verwerkt 3d folder
    """
    for email in move_list:
        try:
            email.Move(wachtrij)
        except Exception as e:
            print("Error occurred while moving the email:", str(e))

def find_inbox(outlook_namespace, account):
    """
    look for the inbox folder of the email account

    :param outlook_namespace: The API of outlook.
    :param account: Name of the account you want the inbox from.
    :return: Inbox of the Outlook account.
    """
    for folder in outlook_namespace.Folders:
        if folder.Name == account:
            for sub_folder in folder.Folders:
                if sub_folder.Name == "Inbox":
                    return sub_folder

def check_duplicate(name, name_list, count):
    """
    Check if there is any duplicate sender

    :param name: Name of the sender
    :param name_list: list of all the names of senders
    :param count: Dictionary which keeps track of the amount of mails for each sender
    :return:  counter to sender
    """
    if name in name_list:
        count[name] += 1
        name = f"{name}_{count[name]}"
    else:
        count[name] = 1
    return name