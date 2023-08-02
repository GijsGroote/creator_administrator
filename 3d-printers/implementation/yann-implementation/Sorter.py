"""
Data File Organizer
------------------

This script reads through a specified folder, identifies various data files,
and organizes them into subfolders based on their file type.

Usage:
1. Specify the folder path containing the data files.
2. Run the script.

"""

import os
import shutil
import re


def find_data_files(folder_path):
    """
        Finds the data files in the specified folder and returns them sorted based on their file type.

        Args:
            folder_path (str): Path to the folder containing the data files.

        Returns:
            list: Sorted list of data files based on their file type.

    """

    sorted_files = [[], [], [], [], []]
    for root, dirs, files in os.walk(folder_path):                           # Read through all folders
        for file in files:                                                   # Read through all files
            for i in range(len(file_types)):                                 # Look for all file types
                if file.lower().endswith(list(file_types.keys())[i]):
                    if list(file_types.keys())[i] == ".dxf":                 # Split dxf for different lasers
                        if re.search(r"PMMA", file, re.IGNORECASE):
                            sorted_files[i+1].append(os.path.join(root, file))
                        else:
                            sorted_files[i].append(os.path.join(root, file))
                    else:
                        sorted_files[i].append(os.path.join(root, file))     # save the other files
    return sorted_files


# Create the new sub folders if it doesn't exist
def create_folders():
    """
    Creates new sub folders based on the specified file types if they don't already exist.
    Returns: list of paths for the created subfolders
    """
    data_path = []
    for data_type in file_types.items():
        data_path.append(os.path.join(folder_path, data_type[1]))
        path = os.path.join(folder_path, data_type[1])
        if not os.path.exists(path):
            os.makedirs(path)
    return data_path


def copy_files():
    """
    Copies the data files to their respective folders.
    """
    data_path = create_folders()
    for count, file_type in enumerate(all_files):
        for file in file_type:
            file_name = os.path.basename(file)
            parent_folder_name = os.path.basename(os.path.dirname(file))
            subfolder_path = os.path.join(data_path[count], parent_folder_name)
            if not os.path.exists(subfolder_path):
                os.makedirs(subfolder_path)
            new_file_path = os.path.join(subfolder_path, file_name)
            shutil.copy2(file, new_file_path)


# Specify the folder path you want to check
folder_path = "C://Users/IWS/Desktop/Aangeleverde bestanden"

file_types = {
    ".gcode": "gcodes",
    ".stl": "3D_printer",
    ".xlsx": "bestellijst",
    ".dxf": "Metaal",
    "Pmma_laser": "PMMA"
}


all_files = find_data_files(folder_path)
copy_files()
print("Sorting done")
