@echo off
setlocal
cd /d "%~dp0"

if not exist ".env" (
  copy ".env.example" ".env" >nul
  echo Created .env from .env.example
  echo Add your GOOGLE_API_KEY and PHOENIX_API_KEY in .env when you are ready.
)

where py >nul 2>nul
if %errorlevel%==0 (
  py -m pip install --upgrade -r requirements.txt
  py -m uvicorn src.app:app --reload
  goto end
)

where python >nul 2>nul
if %errorlevel%==0 (
  python -m pip install --upgrade -r requirements.txt
  python -m uvicorn src.app:app --reload
  goto end
)

echo Python was not found.
echo Install Python from https://www.python.org/downloads/
pause

:end
endlocal
