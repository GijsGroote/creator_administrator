
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

    if widget.file_global_path is not None and\
        os.path.isfile(widget.file_global_path) and\
              widget.file_global_path.endswith('.exe'):
        widget.setStyleSheet(f'background-color: {gv["GOOD_COLOR_RGBA"]};')
        return True
    widget.setStyleSheet(f'background-color: {gv["BAD_COLOR_RGBA"]};')
    return False

def check_property(widget: QWidget, data_type: str, gv: dict) -> bool:
    ''' Validate if all properties. '''

    text = widget.text()

    if data_type == 'Anything':
        widget.setStyleSheet(f'background-color: {gv["GOOD_COLOR_RGBA"]};')
        return True

    if data_type == 'Anything Except Nothing':
        return check_empty(widget, gv)

    if data_type == 'Any Integer':
        return check_int(widget, gv)

    if data_type == 'Integer > 0':
        if check_int(widget, gv) and int(text) > 0:
            widget.setStyleSheet(f'background-color: {gv["GOOD_COLOR_RGBA"]};')
            return True
        widget.setStyleSheet(f'background-color: {gv["BAD_COLOR_RGBA"]};')
        return False

    if data_type == 'Integer >= 0':
        if check_int(widget, gv) and int(text) >= 0:
            widget.setStyleSheet(f'background-color: {gv["GOOD_COLOR_RGBA"]};')
            return True
        widget.setStyleSheet(f'background-color: {gv["BAD_COLOR_RGBA"]};')
        return False

    if data_type == 'Any Decimal Number':
        if text.isdecimal():
            widget.setStyleSheet(f'background-color: {gv["GOOD_COLOR_RGBA"]};')
            return True
        widget.setStyleSheet(f'background-color: {gv["BAD_COLOR_RGBA"]};')
        return False

    if data_type == 'Decimal Number > 0':
        if text.isdecimal() and float(text) > 0:
            widget.setStyleSheet(f'background-color: {gv["GOOD_COLOR_RGBA"]};')
            return True
        widget.setStyleSheet(f'background-color: {gv["BAD_COLOR_RGBA"]};')
        return False

    if data_type == 'Decimal Number >= 0':
        if text.isdecimal() and float(text) >= 0:
            widget.setStyleSheet(f'background-color: {gv["GOOD_COLOR_RGBA"]};')
            return True
        widget.setStyleSheet(f'background-color: {gv["BAD_COLOR_RGBA"]};')
        return False

    raise ValueError(f'data type {data_type} not recognised')

