@echo off
cd /d %~dp0

echo  STREAMLIT DASHBOARD START

:: 1. VENV erstellen falls nicht vorhanden
if not exist venv (
    echo Erstelle Virtual Environment...
    py -m venv venv)

:: 2. Python aus venv setzen
set PYTHON=venv\Scripts\python.exe

:: 3. pip upgraden
echo Upgrade pip...
%PYTHON% -m pip install --upgrade pip

:: 4. Requirements installieren
if exist requirements.txt (
    echo Installiere Requirements...
    %PYTHON% -m pip install -r requirements.txt
) else (
    echo WARNUNG: requirements.txt nicht gefunden)

:: 5. Streamlit starten
echo Starte Streamlit App...
%PYTHON% -m streamlit run Dashboard_Industrie_Reaktor.py

pause