@echo off
    
"C:\Users\gijsg\AppData\Local\Programs\Python\Python311\python.exe" "C:\Users\gijsg\Documents\laserhok-workflow\3d-printers\implementation\functions\select_bestand.py"

rem custom exit code summary:
rem 0 (default) - display "press any key to continue. . ." message
rem 900 - close cmd that runs .bat file
rem 901 - remove folder that runs .bat file
rem 902 - remove folder and close cmd that runs .bat file\
rem 903 - 
rem [904, 910] - reserved error status numbers
rem [911 - 920] call python script and pass exit status

if %errorlevel% equ 900 (
    exit
) else if %errorlevel% equ 901 (
    "C:\Program Files (x86)\IObit\IObit Unlocker\IObitUnlocker.exe" "/Delete" "%~dp0"
    pause
) else if %errorlevel% equ 903 (
    "C:\Program Files (x86)\IObit\IObit Unlocker\IObitUnlocker.exe" "/Delete" "%~dp0"\
    pause
    cd "C:\Users\gijsg\Desktop\3D PRINT HOME\GESLICED"
    start explorer.exe
    exit
) else if %errorlevel% geq 911 if %errorlevel% leq 920 (
    pause
"C:\Users\gijsg\AppData\Local\Programs\Python\Python311\python.exe" "C:\Users\gijsg\Documents\laserhok-workflow\3d-printers\implementation\functions\cmd_farewell_handler.py" "%errorlevel%
) else (
    pause
)