
Do you receive many request to make stuff?

Do you work with 3D printers and laser cutting machines?

Do you look for an organized workflow to make all these requests?

# Creator Administrator is just the right tool for you!

* Automatically download email attachments
* Keep track of job request status
* Automatically send customizable emails
* Prevent cluttering the computer with .stl, .dxf, .3mf all over the file system

Project started at the Technical University Delft workshop that manages 3D printers and laser cutting machines.

# Dependencies:
* PyQT5 (python -m pip install PyQt5)
* PyQtWebEngine (python -m pip install PyQtWebEngine)



# global_variables.json template:
```json 
{
    "REPO_DIR_HOME":  "C:\\Users\\gijsg\\creator-administrator",
    "PYTHON_PATH": "C:Program Files\\Python311\\python.exe",
    "OUTLOOK_PATH":  "C:\\Program Files\\Microsoft Office\\root\\Office16\\OUTLOOK.EXE",
    "ACCEPTED_EXTENSIONS": ".dxf, .txt",
    "ACCEPTED_MATERIALS": "pmma, wood",
    "DAYS_TO_KEEP_JOBS": "5",
    "PASSWORD":  ""
}
```
Optionally add mail templates locations to the global variables.json
    // "RECEIVED_MAIL_TEMPLATE":  "C:\\path\\to\\mail\\template.html",
    // "DECLINED_MAIL_TEMPLATE":  "C:\\path\\to\\mail\\template.html",
    // "FINISHED_MAIL_TEMPLATE":  "C:\\path\\to\\mail\\template.html",

    {
    "REPO_DIR_HOME":  "C:\\Users\\gijsg\\creator-administrator",
    "PYTHON_PATH": "C:Program Files\\Python311\\python.exe",
    "OUTLOOK_PATH":  "C:\\Program Files\\Microsoft Office\\root\\Office16\\OUTLOOK.EXE",
    "ACCEPTED_EXTENSIONS": ".dxf, .dwg",
    "ACCEPTED_MATERIALS": "pmma, wood",
    "DAYS_TO_KEEP_JOBS": "5",
    "ONLY_UNREAD_MAIL": "true",
    "MOVE_MAILS_TO_VERWERKT_FOLDER": "false",
    "MAIL_INBOX_NAME": "temp_inbox",
    "PASSWORD":  ""
}