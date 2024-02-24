@echo off

:start
cls
echo Please enter the file name:
set /p inputFile=

if exist settings.json (
  del settings.json
)

copy settings-%inputFile%.json settings.json

echo Operation complete. Press any key to run again, or 'Q' to quit.
pause >nul
if /i "%errorlevel%"=="81" goto quit

goto start

:quit
echo Exiting...
