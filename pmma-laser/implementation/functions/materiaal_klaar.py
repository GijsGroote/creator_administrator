"""
Material is done, mark selected materials as done and optionally move to VERWERKT.
"""

import glob
import sys

from global_variables import gv
from local_directory_functions import move_job_to_main_folder

from src.mail_functions import EmailManager

from src.directory_functions import (
    job_name_to_global_path,
    does_job_exist_in_main_folder,
    job_name_to_job_folder_name)

from src.talk_to_sa import yes_or_no
from src.cmd_farewell_handler import (
    remove_directory_and_close_cmd_farewell)
# from src.job_tracker import JobTracker

if __name__ == '__main__':

    material_dir_global_path = sys.argv[1]

    # find log file

    # ask if all are done or a selection

    # for the selection that is done:
        # update material_log.json for files which are done
        # if all are done, call verwerkt.bat
        # remove files that are done
        # remove instances from material_log.json that are done



