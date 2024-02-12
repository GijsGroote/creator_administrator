@echo off

poetry shell

pyinstaller --name "CreatorAdministrator" --onefile --windowed --icon=./creator_administrator/figures/creator_icon.ico ./creator_administrator/laser/src/laser_app.py

REM Then use inno setup to create an installer, 