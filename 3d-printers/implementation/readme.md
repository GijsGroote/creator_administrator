
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

2. **Create the file C:\Users\<your_user_name>\.ssh\mail_credentials.json**

    ```json
    {
        "email": "<MAIL_ADDRESS>",
        "password": "<MAIL_PASSWORD>"
    }
    ```

3. **Create the folder <PRINT_DIR_HOME> on a desired location (~/Desktop is recommended), that folder should contain the following 5 subfolders**

    ```text
   └───<PRINT_DIR_HOME>
    ├───AAN_HET_PRINTEN
    ├───AFGEKEURD
    ├───GESLICED
    ├───VERWERKT
    └───WACHTRIJ
    ```
   
3. **Find and update global_variables.py file**

4. **make the inbox.bat:**

   ```bash
   python3 <path_to_repository>/3d-printers/implementation/functions/create_inbox.py
   ```


    

