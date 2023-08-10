import json
import os

# global paths
IMPLEMENTATION_DIR_HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG_DIR_HOME = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
PRINT_DIR_HOME = 'C:/Users/gijsg/Desktop/3d-print-test-env'
OUTLOOK_PATH = "C:/Program Files/Microsoft Office/root/Office16/OUTLOOK.EXE"


# email login info
IMAP_SERVER = 'outlook.office365.com'
absolute_path = os.path.abspath("/Users/gijsg/.ssh/mail_credentials.json")
with open(absolute_path, "r") as json_file:
    json_data = json.load(json_file)
    EMAIL_ADRES = json_data["email"]
    EMAIL_PASSWORD = json_data["password"]

