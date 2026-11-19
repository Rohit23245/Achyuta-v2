@echo off
TITLE Achyuta AI Assistant - Startup Setup
echo Setting up Achyuta AI to start automatically on Windows Startup...

:: Get current folder path
set "CURRENT_DIR=%~dp0"
set "BATCH_PATH=%CURRENT_DIR%start_achyuta_admin.bat"

:: Create shortcut in Startup folder using VBScript
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "VBS_FILE=%temp%\create_shortcut.vbs"

echo Set oWS = WScript.CreateObject("WScript.Shell") > "%VBS_FILE%"
echo sLinkFile = "%STARTUP_FOLDER%\AchyutaAI.lnk" >> "%VBS_FILE%"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%VBS_FILE%"
echo oLink.TargetPath = "%BATCH_PATH%" >> "%VBS_FILE%"
echo oLink.WorkingDirectory = "%CURRENT_DIR%" >> "%VBS_FILE%"
echo oLink.Description = "Achyuta AI Assistant Startup" >> "%VBS_FILE%"
echo oLink.Save >> "%VBS_FILE%"

cscript //nologo "%VBS_FILE%"
if exist "%VBS_FILE%" del "%VBS_FILE%"

echo ========================================================
echo SUCCESS: Achyuta AI has been added to Windows Startup!
echo It will now run automatically every time your computer restarts.
echo ========================================================
pause
