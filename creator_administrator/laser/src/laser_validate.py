from PyQt6.QtWidgets import QMessageBox, QWidget


def validate_material_info(parent: QWidget, material: str, thickness: str, amount: str) -> bool:
        for (thing, value) in (('material', material), ('thickness', thickness), ('amount', amount)):

            if value == "":
                dlg = QMessageBox(parent)
                dlg.setText(f'Fill in {thing}')
                dlg.exec()
                return False

        try:
            thickness_float = float(thickness)

        except (ValueError, SyntaxError):
            dlg = QMessageBox(parent)
            dlg.setText(f'Thickness should be a positive number, not {thickness}')
            dlg.exec()
            return False

        if thickness_float <=0:
            dlg = QMessageBox(parent)
            dlg.setText(f'Thickness should be a positive number, not {thickness}')
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


