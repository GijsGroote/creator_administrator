# Email templates

TODO: this needs an update here

## three default mail templates are provided:
all templates contain {recipient_name}, the sender or recipient is inserted in the mail template. 
* declined.html
contains {declined_reason}, the reason to decline a laser request is inserted into the mail.
* received.html
contains {jobs_in_queue}, the number of laser jobs in the queue before the newly downloaded laser job is loaded into the mail.
* finished.html

# Create custom mail templates:
Specify a custom mail template by specifying the path toward the templates in laser_global_variables.json (recommended location ~/.ssh/pmma_laser_global_variables.json).

Example: see the the MAIL_TEMPLATE files in the following pmma_laser_global_variables.json.

   ```json
   {
       "REPO_DIR_HOME":  "C:\\Users\\user\\Documents\\laserhok-workflow",
       "LASER_DIR_HOME":  "C:\\Users\\user\\Desktop\\3D PRINT HOME",
       "TRACKER_FILE_PATH":  "C:\\Users\\user\\.ssh\\3D_laser_job_log.json",
       "PYTHON_PATH": "C:Program Files\\Python311\\python.exe",
       "IOBIT_UNLOCKER_PATH": "C:\\Program Files (x86)\\IObit\\IObit Unlocker\\IObitUnlocker.exe",
       "OUTLOOK_PATH":  "C:\\Program Files\\Microsoft Office\\root\\Office16\\OUTLOOK.EXE",
       "RECEIVED_MAIL_TEMPLATE":  "C:\\path\\to\\mail\\template.html",
       "DECLINED_MAIL_TEMPLATE":  "C:\\path\\to\\mail\\template.html",
       "FINISHED_MAIL_TEMPLATE":  "C:\\path\\to\\mail\\template.html",
   }
   ```
## do not forget to add {recipient_name}, {declined_reason} and {laser_jobs_in_queue} to your template.

