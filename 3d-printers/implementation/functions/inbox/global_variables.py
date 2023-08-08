
import json
import os

absolute_path = os.path.abspath("/Users/gijsg/.ssh/mail_credentials.json")

with open(absolute_path, "r") as json_file:
    json_data = json.load(json_file)
    EMAIL_ADRES = json_data["email"]
    EMAIL_PASSWORD = json_data["password"]

PRINT_DIR_HOME = 'C:/Users/gijsg/Desktop/3d-print-test-env'
IMAP_SERVER = 'outlook.office365.com'

