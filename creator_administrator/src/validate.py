from PyQt6.QtWidgets import QMessageBox, QWidget

def validate_password(parent: QWidget, gv: dict, password: str) -> bool:
    ''' Validate password in inform user. '''

    if password != gv['PASSWORD']:
        dlg = QMessageBox(parent)
        dlg.setText('Password Incorrect')
        dlg.exec()
        return False
    return True
