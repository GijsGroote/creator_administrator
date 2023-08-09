

from afgekeurd import *
from helper_functions import python_to_exe
from global_variables import *

if __name__ == '__main__':
    python_path = os.path.join(IMPLEMENTATION_DIR_HOME, "functions/afgekeurd.py")
    python_to_exe(python_path, "WACHTRIJ/Gijs_Groote", arguments="Gijs_Groote")