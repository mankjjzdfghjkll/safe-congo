@echo off
chcp 65001 > nul
title SAFE CONGO - Lancement
setlocal
pushd "%~dp0"

set "PYTHON_EXE=%~dp0.conda\python.exe"

:: Tuer tout processus Streamlit encore actif sur le port 8501
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8501 "') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo  ============================================================
echo   SAFE CONGO - Plateforme Epidemiologique RDC
echo  ============================================================
echo.

:: Verifier que Python conda existe
if not exist "%PYTHON_EXE%" goto missing_python

:: Verifier que app.py existe
if not exist "app.py" goto missing_app

echo  Demarrage de l'application...
echo  Ouvrez http://localhost:8501 dans votre navigateur
echo  Ctrl+C pour arreter
echo.

"%PYTHON_EXE%" -m streamlit run app.py --server.port=8501 --server.headless=false --browser.gatherUsageStats=false

goto end

:missing_python
echo  ERREUR: Environnement Python introuvable.
echo  Emplacement attendu: %PYTHON_EXE%
echo  Veuillez reinstaller l'environnement conda du projet.

goto end

:missing_app
echo  ERREUR: app.py introuvable. Lancez ce script depuis le dossier SAFE CONGO.

:end
popd
pause
