@echo off
setlocal
set "PY=C:\Users\PC\anaconda3\envs\safe_congo\python.exe"
set "SCRIPT=%~dp0gen_director_ppt_clean.py"
set "OUT=%USERPROFILE%\Desktop\Presentation_SAFE_CONGO_Directeur_Demain.pptx"

"%PY%" -c "import pptx" >nul 2>nul
if errorlevel 1 (
  "%PY%" -m pip install python-pptx
)

"%PY%" "%SCRIPT%"
if errorlevel 1 exit /b 1

if exist "%OUT%" (
  for %%I in ("%OUT%") do echo PPTX_SIZE=%%~zI
) else (
  echo PPTX_MISSING
  exit /b 1
)