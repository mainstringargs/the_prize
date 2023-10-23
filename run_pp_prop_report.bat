@echo off
setlocal

rem Define variables for Python script arguments
set YEAR=2023
set WEEK=8
set PP_DAY=friday
set GAME_DAY=saturday
set SPORT=college-football

rem set YEAR=2023
rem set WEEK=6
rem set PP_DAY=saturday
rem set GAME_DAY=all
rem set SPORT=nfl

rem Construct the command
set COMMAND=python driver.py --year %YEAR% --week %WEEK% --pp_day %PP_DAY% --game_day %GAME_DAY% --sport %SPORT%

rem Start Git Bash and run the Python script with the provided arguments
start "" "%ProgramFiles%\Git\git-bash.exe" -c "%COMMAND% && /usr/bin/bash --login -i"

endlocal
