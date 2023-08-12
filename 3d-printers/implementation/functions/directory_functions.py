#! /usr/bin/env python3

import os
import shutil

from global_variables import PRINT_DIR_HOME


def get_print_job_global_paths():
    """ return global path for all print jobs """

    print_job_global_paths = []

    for main_folder in os.listdir(PRINT_DIR_HOME):
        temp_print_job_global_paths = [os.path.join(PRINT_DIR_HOME, main_folder, job_folder_name)
                                       for job_folder_name in os.listdir(os.path.join(PRINT_DIR_HOME, main_folder))]

        if len(temp_print_job_global_paths) > 0:
            print_job_global_paths.extend(temp_print_job_global_paths)

    return print_job_global_paths


def get_print_job_folder_names():
    """ return all print job names """

    print_job_names = []

    for main_folder in os.listdir(PRINT_DIR_HOME):
        temp_print_job_names = [print_job_name for print_job_name in
                                os.listdir(os.path.join(PRINT_DIR_HOME, main_folder))]

        if len(temp_print_job_names) > 0:
            print_job_names.extend(temp_print_job_names)

    return print_job_names


def job_name_to_global_path(job_name: str) -> str:
    """ return global path of print job """

    for print_job_global_path in get_print_job_global_paths():
        if job_name in print_job_global_path:
            return print_job_global_path

    raise ValueError(f"no print job path found for print job with name {job_name}")


def get_new_job_folder_name(job_name: str, source_dir_global_path: str, target_main_folder: str) -> str:
    """ get a job folder name for a print job moved to a main folder """

    job_folder_name = None
    for print_job_folder_name in get_print_job_folder_names():
        if job_name in print_job_folder_name:
            job_folder_name = print_job_folder_name
    assert job_folder_name is not None, \
        f'could not find job folder name for job name: {job_name}'

    if target_main_folder in ['AFGEKEURD', 'WACHTRIJ', 'VERWERKT']:
        return job_folder_name

    elif target_main_folder == 'GESLICED':
        date = ""
        if '-' in job_folder_name:
            date_day = job_folder_name.split('-')[0][-2:]
            date_hours = job_folder_name.split('-')[1][:2]
            date = date_day + '-' + date_hours + '_'


        gcode_files = [file for file in os.listdir(source_dir_global_path) if file.lower().endswith(".gcode")]
        print(gcode_files)
        assert len(gcode_files) > 0, f'no .gcode found in print job: {job_name}, slice .stl first'

        max_print_time = ""
        max_print_hours = 0
        max_print_minutes = 0
        for gcode_file in gcode_files:
            if '_' in gcode_file:
                temp_hours = gcode_file.split('_')[0][-3:-1]
                temp_minutes = gcode_file.split('_')[1][:2]
                if (int(temp_hours) > max_print_hours or
                        int(temp_hours) == max_print_hours and
                        int(temp_minutes) > max_print_minutes):
                    max_print_time = temp_hours + 'h_' + temp_minutes + 'm_'
                    max_print_hours = int(temp_hours)
                    max_print_minutes = int(temp_minutes)

        return date + max_print_time + job_name

    elif target_main_folder == 'AAN_HET_PRINTEN':
        return job_folder_name

    else:
        raise ValueError(f'{target_main_folder} is not a main folder')


def move_directory_recursive(source_dir_global: str, target_dir_global: str):
    """ move directory and subdirectories recursively """
    try:
        shutil.move(source_dir_global, target_dir_global)
    except Exception as e:
        print(f"An error occurred: {e}")


def move_print_job(job_name: str, target_main_folder: str):
    """ move print job to target_dir """

    assert target_main_folder in ["AFGEKEURD", "WACHTRIJ", "GESLICED", "AAN_HET_PRINTEN", "VERWERKT"], \
        f"folder {target_main_folder} is not a main folder"

    # find source directory
    source_dir_global_path = job_name_to_global_path(job_name)

    # make target directory
    target_dir_local_path = os.path.join(
        target_main_folder,
        get_new_job_folder_name(
            job_name,
            source_dir_global_path,
            target_main_folder))

    target_dir_global_path = os.path.join(PRINT_DIR_HOME, target_dir_local_path)
    assert target_dir_global_path != source_dir_global_path, \
        'the source directory is equal to the target directory'

    os.mkdir(target_dir_global_path)

    for item in os.listdir(source_dir_global_path):
        source_item = os.path.join(source_dir_global_path, item)
        target_item = os.path.join(target_dir_global_path, item)

        if os.path.isdir(source_item):
            move_directory_recursive(source_item, target_dir_global_path)
        else:
            # TODO: you will get problems moving because op files (especially .stl) which are still open
            shutil.move(source_item, target_item)

    shutil.rmtree(source_dir_global_path)
