
This repository is intended for Windows OS.

Before you begin, make sure you have the following dependencies installed:

- Python 3.10 or higher
- [LockHunter](https://lockhunter.com/download.htm) 
- [Outlook](https://microsoft-outlook.en.softonic.com/)

## Installation Steps

1. **Clone the Repository**

   Start by cloning the project repository to your local machine:

   ```bash
   git clone git@github.com:GijsGroote/laserhok-workflow.git
   ```

2. **Login on outlook on your local machine**  
   
3. **Create the folder <PRINT_DIR_HOME> on a desired location (~/Desktop is recommended), that folder should contain the following 5 subfolders**

    ```text
   └───<PRINT_DIR_HOME>
    ├───AAN_HET_PRINTEN
    ├───AFGEKEURD
    ├───GESLICED
    ├───VERWERKT
    └───WACHTRIJ
    ```
   
   you can give <PRINT_DIR_HOME> any name which pleases you.
   
4. **Create the file global_variables.json (~/.ssh/global_variables.json is recommended)**  
   update the following template and insert in global_variables.json:
   ```json
   {
       "REPO_DIR_HOME":  "C:\\Users\\user\\Documents\\laserhok-workflow",
       "PRINT_DIR_HOME":  "C:\\Users\\user\\Desktop\\3D PRINT HOME",
       "OUTLOOK_PATH":  "C:\\Program Files\\Microsoft Office\\root\\Office16\\OUTLOOK.EXE",
       "LOCKHUNTER_PATH": "C:\\Program Files\\LockHunter\\LockHunter.exe",
       "PYTHON_PATH": "C:Program Files\\Python311\\python.exe"
   }
   ```

5. **Update the path toward global_variables.json in laserhok-workflow\3d-printers\implementation\functions\global_variables.py**

6. **make inbox.bat:**

   ```bash
   python3 <REPO_DIR_HOME>/3d-printers/implementation/functions/create_inbox.py
   ```
   inbox.bat will be placed in the parent directory of <PRINT_DIR_HOME>
   
7. **Dubble click on inbox.bat to start.**  
(tip: file 3d-printers/documentation/handleiding/handleiding.pdf might help)


    

