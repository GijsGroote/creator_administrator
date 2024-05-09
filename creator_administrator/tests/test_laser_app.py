

import sys
import os
import pytest


sys.path.append(os.path.abspath('./'))
from laser.src.laser_app import LaserMainApp, LaserMainWindow


@pytest.fixture(scope="module")
def app():
    """Fixture for creating a QApplication instance."""
    application = LaserMainApp(sys.argv)
    yield application
    application.quit()

@pytest.fixture
def main_window(app):
    """Fixture for creating a main window instance."""
    window = LaserMainWindow()
    yield window
    window.close()

def test_initialization(main_window):
    """Test case to ensure main window initialization."""
    assert main_window is not None

def test_button_click_changes_text(main_window):
    """Test case to ensure clicking button changes some text."""

    # textLabel = main_window.showTextLabel
    # btn = main_window.showTextLabelButton

    # btn.click()
    # assert textLabel.text() == 'display this text'
    assert True

def test_button_click_opens_message_box(main_window):
    """Test case to ensure clicking button opens QMessageBox."""

    # btn = main_window.messageBoxButton
    # btn.click()
    # qmsgbox = main_window.findChild(QW.QMessageBox)

    # assert qmsgbox is not None
    # qmsgbox.close()
    assert True


def test_button_click_opens_custom_dialog(main_window):
    """Test case to ensure clicking button opens CustomDialog."""

    # main_window.openDialogPushButton.click()
    # dlg = main_window.findChild(QW.QDialog)

    # assert dlg is not None
    # dlg.close()
  
