
import os

from src.laser_app import LaserMainApp

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
