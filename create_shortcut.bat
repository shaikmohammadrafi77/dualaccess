@echo off
REM Create Desktop Shortcut for Dual Access Login Test
echo Creating desktop shortcut...

set "projectPath=C:\Users\DELL\OneDrive\Desktop\cloud\dual-access-login-test"
set "shortcutPath=%USERPROFILE%\OneDrive\Desktop\Dual Access Login Test.lnk"

REM Create the shortcut using PowerShell
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%shortcutPath%'); $Shortcut.TargetPath = '%projectPath%\start_app.bat'; $Shortcut.WorkingDirectory = '%projectPath%'; $Shortcut.Description = 'Dual Access Login Test - Flask Application'; $Shortcut.Save()"

if exist "%shortcutPath%" (
    echo Desktop shortcut created successfully!
    echo You can now double-click the shortcut on your desktop to start the app.
) else (
    echo Failed to create desktop shortcut, but you can still use the batch file directly.
)

pause
