@echo off
setlocal
set "PPR_PYTHON=%~dp0..\tools\scientific_code\NPPExtraction\.venv\Scripts\python.exe"
set "PPR_PYTHON_ARGS="
if exist "%PPR_PYTHON%" (
  "%PPR_PYTHON%" -c "import sys; sys.exit(sys.version_info < (3, 11))" >nul 2>&1
  if not errorlevel 1 goto run
)
for /f "delims=" %%P in ('where python 2^>nul') do (
  "%%P" -c "import sys; sys.exit(sys.version_info < (3, 11))" >nul 2>&1
  if not errorlevel 1 (
    set "PPR_PYTHON=%%P"
    goto run
  )
)
py -3 -c "import sys; sys.exit(sys.version_info < (3, 11))" >nul 2>&1
if not errorlevel 1 (
  set "PPR_PYTHON=py"
  set "PPR_PYTHON_ARGS=-3"
  goto run
)
echo Python 3.11 or newer is required to serve the existing map.
echo Install Python or add it to PATH, then reopen this launcher.
pause
exit /b 1

:run
echo Opening the existing map locally for street detail...
"%PPR_PYTHON%" %PPR_PYTHON_ARGS% "%~dp0..\tools\cli\map.py"
if errorlevel 1 (
  echo Could not serve the existing map. See the error above.
  pause
  exit /b 1
)
