
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

2. - **_Either do_: Create mail_credentials.json**

    ```
   C:\Users\<your_user_name>\.ssh\mail_credentials.json
   ```

   that contains:

    ```json
    {
        "email": "<MAIL_ADDRESS>",
        "password": "<MAIL_PASSWORD>"
    }
    ```
   replace <MAIL_ADDRESS> and <MAIL_PASSWORD> with your mail and password.

   - **_Or do_: Login on outlook on your local machine**  
   
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
   
4. **Update some variables in 3d-printers/implementation/functions/global_variables.py**  
   In global_variables.py it is indicated which variables to edit.

5. **make inbox.bat:**

   ```bash
   python3 <REPO_DIR_HOME>/3d-printers/implementation/functions/create_inbox.py
   ```
   inbox.bat will be placed in the parent directory of <PRINT_DIR_HOME>
   
6. **Dubble click on inbox.bat to start.**  
(tip: file 3d-printers/documentation/handleiding/handleiding.pdf might help)


    

