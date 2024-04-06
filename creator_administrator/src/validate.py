
import os

from PyQt6.QtWidgets import QWidget

def check_empty(widget: QWidget, gv: dict) -> bool:
    if widget.text() == '':
        widget.setStyleSheet(f'background-color: {gv["BAD_COLOR_RGBA"]};')
        return False

    widget.setStyleSheet(f'background-color: {gv["GOOD_COLOR_RGBA"]};')
    return True

def check_int(widget: QWidget, gv: dict) -> bool:
    try:
        int(widget.text())
        widget.setStyleSheet(f'background-color: {gv["GOOD_COLOR_RGBA"]};')
        return True

    except ValueError:
        widget.setStyleSheet(f'background-color: {gv["BAD_COLOR_RGBA"]};')
        return False

def check_extensions_tuple(widget: QWidget, gv: dict) -> bool:
    try:
        tuple(widget.text().split(', '))

    except ValueError:
        widget.setStyleSheet(f'background-color: {gv["GOOD_COLOR_RGBA"]};')
        return False

    for string in widget.text().split(', '):
        if not (string.startswith('.') and string[1:].isalnum()):
            widget.setStyleSheet(f'background-color: {gv["BAD_COLOR_RGBA"]};')
            return False

    widget.setStyleSheet(f'background-color: {gv["GOOD_COLOR_RGBA"]};')
    return True

def check_comma_seperated_tuple(widget: QWidget, gv: dict) -> bool:
    try:
        tuple(widget.text().split(', '))

    except ValueError:
        widget.setStyleSheet(f'background-color: {gv["BAD_COLOR_RGBA"]};')
        return False

    for string in widget.text().split(', '):
        if not string.isalpha():
            widget.setStyleSheet(f'background-color: {gv["BAD_COLOR_RGBA"]};')
            return False

    widget.setStyleSheet(f'background-color: {gv["GOOD_COLOR_RGBA"]};')
    return True


def check_html(widget: QWidget, gv: dict) -> bool:
    if not widget.file_global_path.lower().endswith('.html'):
        widget.setStyleSheet(f'background-color: {gv["BAD_COLOR_RGBA"]};')
        return False

    widget.setStyleSheet(f'background-color: {gv["GOOD_COLOR_RGBA"]};')
    return True

def check_file_exists(widget: QWidget, file_path: str, gv: dict) -> bool:
    if os.path.exists(file_path):
        widget.setStyleSheet(f'background-color: {gv["GOOD_COLOR_RGBA"]};')
        return True

    widget.setStyleSheet(f'background-color: {gv["BAD_COLOR_RGBA"]};')
    return False

def check_is_directory(widget: QWidget, gv: dict) -> bool:

    if os.path.isdir(widget.folder_global_path):
        widget.setStyleSheet(f'background-color: {gv["GOOD_COLOR_RGBA"]};')
        return True

    widget.setStyleSheet(f'background-color: {gv["BAD_COLOR_RGBA"]};')
    return False

def check_is_executable(widget: QWidget, gv: dict) -> bool:

    if os.path.isfile(widget.file_global_path) and widget.file_global_path.endswith('.exe'):
        widget.setStyleSheet(f'background-color: {gv["GOOD_COLOR_RGBA"]};')
        return True
    widget.setStyleSheet(f'background-color: {gv["BAD_COLOR_RGBA"]};')
    return False

def validate_properties(widget: QWidget, properties_dict: dict) -> bool:
    ''' Validate if all properties. '''

    # No properties to check
    if properties_dict is None:
        return True
    # for prope
    # TODO make this functiosn
    return True
