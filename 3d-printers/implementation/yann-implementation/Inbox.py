"""
Outlook Email Organizer
-----------------------

This script organizes emails and attachments from the Outlook inbox into separate folders based on the sender's name.
It moves each email to the corresponding folder and saves them as .msg files.

Requirements:
- Python 3.x
- win32com library
- unidecode library

Usage:
1. Ensure that the required libraries are installed.
2. Configure the target folder path where the new folders will be created.
3. Specify the sub_account name and the inbox sub_folder name within that sub_account.
4. Run the script.

"""
import win32com.client
import os
import re
from unidecode import unidecode


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


def create_folder(name, target):
    """
    Creates new folder with ASCII characters.

    :param name: Name of the sender of the email
    :param target: Specified target for to save items
    :return: Path to the new folder
    """

    folder_name = unidecode(name)  # Replace non-ASCII characters with their closest ASCII equivalents
    folder_name = re.sub(r'[<>:"/\\|?*]', "", folder_name)  # Remove additional invalid characters from the folder name
    new_folder_path = os.path.join(target, folder_name)
    os.makedirs(new_folder_path, exist_ok=True)
    return new_folder_path


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


def main():
    # Make lists of senders and items to be filled
    if inbox_sub:
        # Store all items and make all lists of variables
        items = inbox_sub.Items  # Get all inbox items
        sender_names = []
        name_count = {}
        items_to_move = []  # List to store items that need to be moved

        # Read through all items and make the folders
        for item in items:
            sender_name = check_duplicate(item.SenderName, sender_names, name_count)  # Check for duplicate sender names

            if sender_name:  # Check if there is a sender name
                sender_names.append(sender_name)  # Add the name of the sender to the list of senders
                new_folder_path = create_folder(sender_name, target_path)  # Create new folder and path to the folder
                save_msg(item, new_folder_path)  # Save email as .msg file
                save_attachments(item, new_folder_path)  # Save attachments into the folder
                items_to_move.append(item)  # Add the item to the list of items to be moved

        verwerkt_folder = inbox_sub.Folders("Verwerkt 3d")
        move_items(items_to_move, verwerkt_folder)

        print("All items moved to the 'Wachtrij' folder.")


# Open Outlook application and get access to the API
outlook = win32com.client.Dispatch("Outlook.Application")
namespace = outlook.GetNamespace("MAPI")

# Folder path to store the new folders in
target_path = "C://Users/IWS/Desktop/3D TO DO"

# Find the target folder and make inbox_sub the inbox of 3D-IWS
sub_account_name = "3D-IWS@tudelft.nl"
inbox_sub = find_inbox(namespace, sub_account_name)

main()
