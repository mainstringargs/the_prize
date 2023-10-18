@echo off
setlocal

rem Define variables for Python script arguments
set YEAR=2023
set WEEK=7
set PP_DAY=friday
set GAME_DAY=all
set SPORT=college-football

set YEAR=2023
set WEEK=6
set PP_DAY=saturday
set GAME_DAY=all
set SPORT=nfl

rem Construct the command
set COMMAND=python driver.py --year %YEAR% --week %WEEK% --pp_day %PP_DAY% --game_day %GAME_DAY% --sport %SPORT%

rem Start Git Bash and run the Python script with the provided arguments
start "" "%ProgramFiles%\Git\git-bash.exe" -c "%COMMAND% && /usr/bin/bash --login -i"

endlocal
