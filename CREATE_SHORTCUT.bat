@echo off
REM Script to create desktop shortcut for KRS PDF to CSV Converter

echo.
echo Creating desktop shortcut...
echo.

REM Get the current directory
set SCRIPT_DIR=%~dp0

REM Create VBS script to create shortcut
(
echo Set oWS = WScript.CreateObject("WScript.Shell"^)
echo sLinkFile = oWS.SpecialFolders("Desktop"^) ^& "\KRS PDF to CSV.lnk"
echo Set oLink = oWS.CreateShortcut(sLinkFile^)
echo oLink.TargetPath = "%SCRIPT_DIR%run.bat"
echo oLink.WorkingDirectory = "%SCRIPT_DIR%"
echo oLink.Description = "KRS PDF to CSV Converter"
echo oLink.Save
) > "%TEMP%\create_shortcut.vbs"

cscript "%TEMP%\create_shortcut.vbs"
del "%TEMP%\create_shortcut.vbs"

echo.
echo Successfully created shortcut on Desktop!
echo You can now run the application by double-clicking the shortcut.
echo.
pause
