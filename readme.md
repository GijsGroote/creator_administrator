
Do you receive many request to make stuff?

Do you work with 3D printers and laser cutting machines?

Do you look for an organized workflow to make all these requests?

# Creator Administrator is just the right tool for you!

* Automatically download email attachments
* Keep track of job request status
* Automatically send customizable emails
* Prevent cluttering the computer with .stl, .dxf, .3mf all over the file system

# Dowload CreatorAdministratorSetup.exe [here](https://drive.google.com/file/d/1Gc8u9itPEubAcBtXttp2Pj62Imj6uPP6/view?usp=drive_link)

# Dependencies:
* PyQT5 (python -m pip install PyQt5)
* PyQtWebEngine (python -m pip install PyQtWebEngine)
* requests (python -m pip install requests)
* unidecode (python -m pip install unidecode)
* win32com (python -m pip install pypiwin32)



# global_variables.json template:
```json 
{
    "REPO_DIR_HOME":  "C:\\Users\\gijsg\\creator-administrator",
    "PYTHON_PATH": "C:Program Files\\Python311\\python.exe",
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

# Errors:
Outlook Has a known error which look like this:
 "We can't open 'C:\\Users\\..\\mail.msg'. It's possible the file is already open, or you don't have permission to open it. To check your permissions, right-click the file folder, then click Properties.
its possible the file is already open, or you dont have permission to open it error in outlook 

If you encounter this: turn off the add-ins in Outlook:
    In Outlook, go to the File tab
    Select Options
    Select Add-Ins on the left
    Near the bottom of the window, you'll see a Manage option; set it to COM Add-Ins and click Go
    De-select all of the add-ins and click OK
    Restart Outlook


[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/gijsgroote)
