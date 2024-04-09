
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

    check = None

    if data_type == 'Anything':
        check = check_is_anything(text)

    elif data_type == 'Anything Except Nothing':
        check = check_is_anything_except_nothing(text)

    elif data_type == 'Any Integer':
        check = check_is_any_integer(text)

    elif data_type == 'Integer > 0':
        check = check_is_integer_larger_than_zero(text)

    elif data_type == 'Integer >= 0':
        check = check_is_integer_larger_equel_zero(text)

    elif data_type == 'Any Decimal Number':
        check = check_is_any_decimal(text)

    elif data_type == 'Decimal Number > 0':
        check = check_is_decimal_larger_than_zero(text)

    elif data_type == 'Decimal Number >= 0':
        check = check_is_decimal_larger_equal_zero(text)

    if check:
        widget.setStyleSheet(f'background-color: {gv["GOOD_COLOR_RGBA"]};')
    elif not check:
        widget.setStyleSheet(f'background-color: {gv["BAD_COLOR_RGBA"]};')
    else:
        raise ValueError(f'data type {data_type} not recognised')

    return check

def check_is_anything(input) -> bool:
    if input is not None:
        return True
    return False

def check_is_anything_except_nothing(input) -> bool:
    if input is not None and input != '':
        return True
    return False

def check_is_any_integer(input) -> bool:
    try:
        int(input)
        return True

    except ValueError:
        return False

def check_is_integer_larger_than_zero(input) -> bool:
    if check_is_any_integer(input) and int(input) > 0:
        return True
    return False

def check_is_integer_larger_equel_zero(input) -> bool:
    if check_is_any_integer(input) and int(input) >= 0:
        return True
    return False

def check_is_any_decimal(input) -> bool:
    if input.isdecimal():
        return True
    return False

def check_is_decimal_larger_than_zero(input) -> bool:
    if check_is_any_decimal(input) and float(input) > 0:
        return True
    return False

def check_is_decimal_larger_equal_zero(input) -> bool:
    if check_is_any_decimal(input) and float(input) >= 0:
        return True
    return False