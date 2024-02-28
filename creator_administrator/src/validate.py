from PyQt6.QtWidgets import QMessageBox, QWidget

def validate_password(parent_widget: QWidget, gv: dict, password: str) -> bool:
    ''' Validate password in inform user. '''

    if password != gv['PASSWORD']:
        dlg = QMessageBox(parent_widget)
        dlg.setText('Password Incorrect')
        dlg.exec()
        return False
    return True
