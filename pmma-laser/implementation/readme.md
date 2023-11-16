This repository is intended for Windows OS.

Before you begin, make sure you have the following dependencies installed:

- Python 3.10 or higher
- [IO Bit Unlocker](https://www.iobit.com/nl/iobit-unlocker.php#)
- [Outlook 2019](https://microsoft-outlook.en.softonic.com/)

## Installation Steps

1. **Clone the Repository**

   Start by cloning the project repository to your local machine:

   ```bash
   git clone git@github.com:GijsGroote/laserhok-workflow.git
   ```

2. **Login on outlook on your local machine**

3. **Create the folder <LASER_DIR_HOME> on a desired location (~/Desktop is recommended), that folder should contain the following 5 subfolders**

    ```text
   └───<LASER_DIR_HOME>
      ├───AAN_HET_PRINTEN
      ├───AFGEKEURD
      ├───GESLICED
      ├───VERWERKT
      └───WACHTRIJ
    ```

   you can give <PRINT_DIR_HOME> any name which pleases you.

4. **Create the file 3D_print_global_variables.json (~/.ssh/3D_print_global_variables.json is recommended)**
   update the following template and insert in 3D_print_global_variables.json:
   ```json
   {
       "REPO_DIR_HOME":  "C:\\Users\\user\\Documents\\laserhok-workflow",
       "PRINT_DIR_HOME":  "C:\\Users\\user\\Desktop\\3D PRINT HOME",
       "TRACKER_FILE_PATH":  "C:\\Users\\user\\.ssh\\3D_print_job_log.json",
       "PYTHON_PATH": "C:Program Files\\Python311\\python.exe",
       "IOBIT_UNLOCKER_PATH": "C:\\Program Files (x86)\\IObit\\IObit Unlocker\\IObitUnlocker.exe",
       "OUTLOOK_PATH":  "C:\\Program Files\\Microsoft Office\\root\\Office16\\OUTLOOK.EXE"
   }
   ```

5. **Update the path toward 3D_print_global_variables.json:**
    Find the file in `../laserhok-workflow\3d-printers\implementation\functions\global_variables.py`

6. **make inbox.bat and select_bestand.bat:**

   ```bash
   python3 <REPO_DIR_HOME>/3d-printers/implementation/functions/create_batch_file.py
   ```
7. **Create two desktop shortcuts:**
   link the shortcut to:
 `../laserhok-workflow/3d-printers/implementation/batch_files/inbox.bat`
 `../laserhok-workflow/3d-printers/implementation/batch_files/select_bestand.bat`

   Optionally you can give the shortcuts an custom icon located in
`../laserhok-workflow/3d-printers/implementation/figures/`

8. **Dubble click on inbox.bat (or the shortcut toward inbox.bat) to start.**
   tip: file 3d-printers/documentation/handleiding/handleiding.pdf might help
