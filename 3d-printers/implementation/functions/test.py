import os

from executable_functions import python_to_exe, python_to_bat
from global_variables import FUNCTIONS_DIR_HOME


if __name__ == "__main__":
    python_path = os.path.join(FUNCTIONS_DIR_HOME, 'inbox.py')
    python_to_bat(python_path, 'Gijs_Groote')


    # choose_option()
    # available_options = ['a', 'b', 'c', 'ahahh']  # Example options list
    # main(available_options)
    # python_path = os.path.join(FUNCTIONS_DIR_HOME, 'printer_klaar.py')
    # python_to_exe(python_path, 'Gijs_Groote')

