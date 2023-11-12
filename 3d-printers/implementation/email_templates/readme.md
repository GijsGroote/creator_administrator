# Email templates

## three default mail templates are provided:
all templates contain {recipient_name}, the sender or recipient is inserted in the mail template. 
* declined.html
contains {declined_reason}, the reason to decline a print request is inserted into the mail.
* received.html
contains {print_jobs_in_queue}, the number of print jobs in the queue before the newly downloaded print job is loaded into the mail.
* finished.html

# Create custom mail templates:
Specify a custom mail template by specifying the path toward the templates in 3d_print_global_variables.json (recommended location ~/.ssh/3D_print_global_variables.json).

Example: see the the declined_mail_template, attachments_downloaded_mail_template and print_finished_mail_template in the following 3D_print_global_variables.json.

   ```json
   {
       "REPO_DIR_HOME":  "C:\\Users\\user\\Documents\\laserhok-workflow",
       "PRINT_DIR_HOME":  "C:\\Users\\user\\Desktop\\3D PRINT HOME",
       "TRACKER_FILE_PATH":  "C:\\Users\\user\\.ssh\\3D_print_job_log.json",
       "PYTHON_PATH": "C:Program Files\\Python311\\python.exe",
       "IOBIT_UNLOCKER_PATH": "C:\\Program Files (x86)\\IObit\\IObit Unlocker\\IObitUnlocker.exe",
       "OUTLOOK_PATH":  "C:\\Program Files\\Microsoft Office\\root\\Office16\\OUTLOOK.EXE"
       "received_mail_template":  "C:\\path\\to\\mail\\template.html",
       "declined_mail_template":  "C:\\path\\to\\mail\\template.html",
       "finished_mail_template":  "C:\\path\\to\\mail\\template.html",
   }
   ```
## do not forget to add {recipient_name}, {declined_reason} and {print_jobs_in_queue} to your template.

