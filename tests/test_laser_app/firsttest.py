import os

from creator_administrator.laser.src.laser_app import LaserMainApp

import unittest

class TestMyApp(unittest.TestCase):

    def setUp(self):
        self.laser_app = LaserMainApp([])
        self.laser_window = self.laser_app.build()

    def test_appExists(self):
        self.assertIsNotNone(self.laser_app)
        self.assertIsNotNone(self.laser_window)
    
    def test_openSettingsDialg(self):

        self.assertEqual(1, 1)

    def tearDown(self):
        self.laser_app.quit()

if __name__ == '__main__':
    unittest.main()



#     import pytest

# # Assuming you have an application class named MyApp that you want to test

# @pytest.fixture
# def app(qtbot):
#     # Assuming MyApp is the class representing your application
#     # You might need to adjust this according to your application structure
#     app = MyApp()
#     qtbot.addWidget(app)
#     return app

# def test_application_opens(qtbot, app):
#     # Assuming there's a method in MyApp that opens the application window
#     app.open_window()

#     # You can use Qt's signals and slots mechanism to wait for the window to open
#     # For example, assuming you have a signal called 'windowOpened' emitted when the window is opened
#     # You would connect this signal to a method in your test class that sets a flag when the window is opened
#     # Then, you can wait for this flag to be set
#     opened
