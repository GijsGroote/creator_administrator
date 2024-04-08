from PyQt6.QtWidgets import QMessageBox, QWidget

from global_variables import gv


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

    # TODO: make this function once, reuse it later tehn

    for property_dict in print_properties_dict.values():
        text = property_dict['qline_edit_widget'].text()
        data_type = property_dict['data_type']

        if data_type == 'Anything':
            pass

        elif data_type == 'Anything Except Nothing' and text == '':
            return False

        elif data_type == 'Any Integer':
            try:
                int(text)

            except ValueError:
                return False

        elif data_type == 'Integer > 0':
            try:
                int(text)

            except ValueError:
                return False

            if int(text) > 0:
                return False

        elif data_type == 'Integer >= 0':
            try:
                int(text)

            except ValueError:
                return False

            if int(text) >= 0:
                return False

        elif data_type == 'Any Decimal Number':
            if not text.isdecimal():
                return False

        elif data_type == 'Decimal Number > 0':
            if not text.isdecimal() or float(text) > 0:
                return False

        elif data_type == 'Decimal Number >= 0':
            if not text.isdecimal() or float(text) >= 0:
                return False

        raise ValueError(f'data type {data_type} not recognised')

    return True

