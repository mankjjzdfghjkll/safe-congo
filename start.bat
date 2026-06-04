@echo off
chcp 65001 > nul
title SAFE CONGO - Lancement

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
if not exist ".conda\python.exe" (
    echo  ERREUR: Environnement Python introuvable (.conda\python.exe)
    echo  Veuillez reinstaller l'environnement conda du projet.
    pause
    exit /b 1
)

:: Verifier que app.py existe
if not exist "app.py" (
    echo  ERREUR: app.py introuvable. Lancez ce script depuis le dossier SAFE CONGO.
    pause
    exit /b 1
)

echo  Demarrage de l'application...
echo  Ouvrez http://localhost:8501 dans votre navigateur
echo  Ctrl+C pour arreter
echo.

.conda\python.exe -m streamlit run app.py --server.port=8501 --server.headless=false --browser.gatherUsageStats=false

pause
