"""
Convert subfolders in a selected folder to print jobs.
"""


import os
import sys
from convert_functions import convert_win32_msg_to_email_msg
from global_variables import (
    FUNCTIONS_DIR_HOME,
    PRINT_DIR_HOME)
from cmd_farewell_handler import open_wachtrij_folder_cmd_farewell
from talk_to_sa import password_please
import tkinter as tk
from tkinter import filedialog


if __name__ == '__main__':

    print('You are using select_bestand.bat, the default method '
          ' is to click on the input.bat file')
    # password_please()

    print('''select <FOLDER> with the following structure:'
└───<FOLDER>
  ├───<SUBFOLDER_1>
  │  ├───3d_file.stl
  │  └───another_3d_file.stl
  └───<SUBFOLDER_2>
    ├───3d_file.stl
    └───another_3d_file.stl
    ''')

    folder_global_path = filedialog.askdirectory(initialdir=os.path.join(PRINT_DIR_HOME, '../'))

    subfolders = [f for f in os.listdir(folder_global_path) if os.path.isdir(os.path.join(folder_global_path, f))]
    if len(subfolders) == 0:
        print(f'There are no subfolders in {folder_global_path}, aborting. . .')
        sys.exit(0)

    project_name = input(f'Where are the 3D prints for? Enter a name for the project:')


    # loop through subfolders

    new_print_job = False

    if new_print_job:
        open_wachtrij_folder_cmd_farewell()
