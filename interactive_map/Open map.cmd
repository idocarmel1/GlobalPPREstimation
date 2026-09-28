@echo off
setlocal
if exist "%~dp0..\tools\scientific_code\NPPExtraction\.venv\Scripts\pythonw.exe" (
  start "" "%~dp0..\tools\scientific_code\NPPExtraction\.venv\Scripts\pythonw.exe" "%~dp0..\tools\open_map.py"
  exit /b
)
where pyw >nul 2>&1
if not errorlevel 1 (
  start "" pyw -3 "%~dp0..\tools\open_map.py"
  exit /b
)
where pythonw >nul 2>&1
if not errorlevel 1 (
  start "" pythonw "%~dp0..\tools\open_map.py"
  exit /b
)
echo Python 3 is needed for the street-map launcher.
echo You can still open index.html directly for the bundled land map.
pause
