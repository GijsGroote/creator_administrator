#! /usr/bin/env python3

import os
import sys
import subprocess

from global_variables import (
    LOCKHUNTER_PATH,
    FUNCTIONS_DIR_HOME,
    PYTHON_PATH)
from directory_functions import job_name_to_global_path

def python_to_batch(python_path: str, job_name: str):
    """ convert a python file to an batch file. """

    assert os.path.isfile(python_path), f"file {python_path} does not exist."
    job_global_path = job_name_to_global_path(job_name)
    assert os.path.exists(job_global_path), f"path {job_global_path} does not exist."

    function_name = os.path.splitext(os.path.basename(python_path))[0]

    myBat = open(os.path.join(job_global_path, f'{function_name}.bat'), 'w+')
    myBat.write(rf"""
@echo off

REM Get the folder path of the batch script
set "script_folder=%~dp0"
echo The batch script is located in: %script_folder%

"{PYTHON_PATH}" "{python_path}" "{job_name}"

rem custom exit code summary:
rem 0 (default) - display "press any key to continue. . ." message
rem 900 - close cmd that runs .bat file
rem 901 - remove folder that runs .bat file
rem [902, 910] - reserved error status numbers
rem >910 - call python script and pass exit status

if %errorlevel% equ 900 (
    exit
) else if %errorlevel% equ 901 (
set "script_folder=%~dp0"
"C:\Program Files (x86)\IObit\IObit Unlocker\IObitUnlocker.exe" "/Delete" "%script_folder%"
pause
) else if %errorlevel% gtr 910(
"{PYTHON_PATH}" "{os.path.join(FUNCTIONS_DIR_HOME, 'cmd_farewell_handler.py')}" "%errorlevel%
) else (
    pause
)""")

    myBat.close()

