# Email templates

## three default mail templates are provided:
all templates contain {recipient_name}, the sender or recipient is inserted in the mail template. 
* declined.html
contains {declined_reason}, the reason to decline a laser request is inserted into the mail.
* received.html
contains {laser_jobs_in_queue}, the number of laser jobs in the queue before the newly downloaded laser job is loaded into the mail.
* finished.html

# Create custom mail templates:
Specify a custom mail template by specifying the path toward the templates in 3d_laser_global_variables.json (recommended location ~/.ssh/3D_laser_global_variables.json).

Example: see the the declined_mail_template, attachments_downloaded_mail_template and laser_finished_mail_template in the following 3D_laser_global_variables.json.

   ```json
   {
       "REPO_DIR_HOME":  "C:\\Users\\user\\Documents\\laserhok-workflow",
       "LASER_DIR_HOME":  "C:\\Users\\user\\Desktop\\3D PRINT HOME",
       "TRACKER_FILE_PATH":  "C:\\Users\\user\\.ssh\\3D_laser_job_log.json",
       "PYTHON_PATH": "C:Program Files\\Python311\\python.exe",
       "IOBIT_UNLOCKER_PATH": "C:\\Program Files (x86)\\IObit\\IObit Unlocker\\IObitUnlocker.exe",
       "OUTLOOK_PATH":  "C:\\Program Files\\Microsoft Office\\root\\Office16\\OUTLOOK.EXE"
       "received_mail_template":  "C:\\path\\to\\mail\\template.html",
       "declined_mail_template":  "C:\\path\\to\\mail\\template.html",
       "finished_mail_template":  "C:\\path\\to\\mail\\template.html",
   }
   ```
## do not forget to add {recipient_name}, {declined_reason} and {laser_jobs_in_queue} to your template.

