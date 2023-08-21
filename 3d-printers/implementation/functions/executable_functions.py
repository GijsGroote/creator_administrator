#! /usr/bin/env python3

import os

from global_variables import (
    FUNCTIONS_DIR_HOME,
    PYTHON_PATH)
from cmd_farewell_handler import cmd_farewells
from directory_functions import job_name_to_global_path

def python_to_batch(python_path: str, job_name: str):
    """ convert a python file to an batch file. """

    assert os.path.isfile(python_path), f"file {python_path} does not exist."
    job_global_path = job_name_to_global_path(job_name)
    assert os.path.exists(job_global_path), f"path {job_global_path} does not exist."

    function_name = os.path.splitext(os.path.basename(python_path))[0]

    bat_file = open(os.path.join(job_global_path, f'{function_name}.bat'), 'w+')
    bat_file.write(rf"""
@echo off

"{PYTHON_PATH}" "{python_path}" "{job_name}"

{cmd_farewells}""")

    bat_file.close()

