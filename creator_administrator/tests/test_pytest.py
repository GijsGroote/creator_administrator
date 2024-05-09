import sys
import os
import pytest

sys.path.append(os.path.abspath('./'))
from laser.src.laser_app import LaserMainWindow, LaserMainApp

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

# def test_open_dialog(main_window):
#     """Test case to ensure clicking button opens QMessageBox."""

#     main_window.importFromMailAction.trigger()
#     main_window.selectFilesAction.trigger()
#     main_window.selectFoldersAction.trigger()


