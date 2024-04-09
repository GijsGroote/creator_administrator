from PyQt6.QtWidgets import QMessageBox, QWidget
from src.qmessagebox import WarningQMessageBox

from global_variables import gv
from src.validate import (
    check_is_anything,
    check_is_anything_except_nothing,
    check_is_any_integer,
    check_is_integer_larger_than_zero,
    check_is_integer_larger_equel_zero,
    check_is_any_decimal,
    check_is_decimal_larger_than_zero,
    check_is_decimal_larger_equal_zero
)


def validate_material_info(parent: QWidget, material: str, amount: str) -> bool:
        for (thing, value) in (('material', material), ('amount', amount)):

            if value == "":
                dlg = QMessageBox(parent)
                dlg.setText(f'Fill in {thing}')
                dlg.exec()
                return False

        try:
            amount_int = int(amount)
        except (ValueError, SyntaxError):
            dlg = QMessageBox(parent)
            dlg.setText(f'Amount should be a positive interger, not: {amount}')
            dlg.exec()
            return False

        if amount_int <= 0:
            dlg = QMessageBox(parent)
            dlg.setText(f'Amount should be a positive interger, not: {amount}')
            dlg.exec()
            return False

        return True

def validate_print_properties(parent: QWidget, print_properties_dict: dict) -> bool:

    for property_dict in print_properties_dict.values():
        text = property_dict['qline_edit_widget'].text()
        data_type = property_dict['data_type']
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
        
        if check is None: 
            raise ValueError(f'Data type {data_type} not recognized')

        if not check:
            WarningQMessageBox(parent, gv, f'Could not convert {text} to o {data_type}')
            return False

    return True

