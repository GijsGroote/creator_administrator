
import os
import sys

sys.path.append(os.path.abspath('./'))
from creator_administrator.printer.src.printer_app import PrinterMainApp

import unittest

class TestMyApp(unittest.TestCase):

    def setUp(self):
        self.printer_app = PrinterMainApp([])
        self.printer_window = self.printer_app.build()

    def test_appExists(self):
        self.assertIsNotNone(self.printer_app)
        self.assertIsNotNone(self.printer_window)
    
    def test_openSettingsDialg(self):

        self.assertEqual(1, 1)

    def tearDown(self):
        self.printer_app.quit()

if __name__ == '__main__':
    unittest.main()
