@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
  py -m pip install --upgrade -r requirements.txt
  py src\test_phoenix.py
  pause
  goto end
)

where python >nul 2>nul
if %errorlevel%==0 (
  python -m pip install --upgrade -r requirements.txt
  python src\test_phoenix.py
  pause
  goto end
)

echo Python was not found.
echo Install Python from https://www.python.org/downloads/
pause

:end
endlocal
