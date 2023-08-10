#! /usr/bin/env python3

from global_variables import *
import PyInstaller.__main__

def python_to_exe(python_path: str, local_path: str, arguments=None):
    """ convert a python file to an executable file an move to local_path. """

    assert os.path.isfile(python_path), f"file {python_path} does not exist."
    global_path = os.path.join(PRINT_DIR_HOME, local_path)
    assert os.path.exists(global_path), f"path {global_path} does not exist."

    try:
        PyInstaller.__main__.run([
            python_path,
            '--onefile',
            '--console',
            f'--distpath={global_path}',
            f'--icon={os.path.join(FIG_DIR_HOME, "download.ico")}',
            f'--python-option={arguments}',
        ])

    except FileExistsError as exc:
        print(exc)
