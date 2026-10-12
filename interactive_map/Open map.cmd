@echo off
setlocal
set "PPR_PYTHON=%~dp0..\tools\scientific_code\NPPExtraction\.venv\Scripts\python.exe"
set "PPR_PYTHON_ARGS="
if exist "%PPR_PYTHON%" (
  "%PPR_PYTHON%" -c "import openpyxl,numpy,pandas,scipy,sympy,igraph,tqdm" >nul 2>&1
  if not errorlevel 1 goto run
)
for /f "delims=" %%P in ('where python 2^>nul') do (
  "%%P" -c "import openpyxl,numpy,pandas,scipy,sympy,igraph,tqdm" >nul 2>&1
  if not errorlevel 1 (
    set "PPR_PYTHON=%%P"
    goto run
  )
)
py -3 -c "import openpyxl,numpy,pandas,scipy,sympy,igraph,tqdm" >nul 2>&1
if not errorlevel 1 (
  set "PPR_PYTHON=py"
  set "PPR_PYTHON_ARGS=-3"
  goto run
)
echo A Python 3 environment with openpyxl, numpy, pandas, scipy, sympy, igraph and tqdm is required.
echo Install the project dependencies in your Python environment, then reopen this launcher.
echo Existing index.html is a saved view and may not contain current method coverage.
pause
exit /b 1

:run
echo Checking researcher-validated model coverage before opening the map...
"%PPR_PYTHON%" %PPR_PYTHON_ARGS% "%~dp0..\tools\cli\map.py"
if errorlevel 1 (
  echo Map preparation failed. The error above identifies the affected model or publication check.
  pause
  exit /b 1
)
