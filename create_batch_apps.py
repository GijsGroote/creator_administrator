import os
import subprocess

# create batch files to the 3d print and laser application
if __name__ == '__main__':

    # Run the command and capture its output
    poetry_python_path = subprocess.check_output("poetry env info -p", shell=True, text=True).strip()

    with open('laser_app.bat', 'w') as file:
        file.write(rf'''@echo off
"{os.path.join(poetry_python_path, 'Scripts', 'python.exe')}" "{os.path.join(os.path.dirname(os.path.abspath(__file__)), 'creator_administrator', 'laser', 'src', 'laser_app.py')}"''')

    with open('printer_app.bat', 'w') as file:
        file.write(rf'''@echo off
"{os.path.join(poetry_python_path, 'Scripts', 'python.exe')}" "{os.path.join(os.path.dirname(os.path.abspath(__file__)), 'creator_administrator', 'printer', 'src', 'printer_app.py')}"''')
