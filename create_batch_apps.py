import subprocess

# create batch files to the 3d print and laser application
if __name__ == '__main__':

    # Run the command and capture its output
    poetry_python_path = subprocess.check_output("poetry env info -p", shell=True, text=True).strip()
    print(f"{poetry_python_path} and again {poetry_python_path}")

    with open('./laser_app.bat', 'w') as file:
        file.write(rf'''@ECHO OFF
"{poetry_python_path}" "creator_administrator/printer/src/printer_app.py"''')

    with open('./laser_app.bat', 'w') as file:
        file.write(rf'''@ECHO OFF
"{poetry_python_path}" "creator_administrator/printer/src/printer_app.py"''')
