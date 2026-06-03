@echo off
REM KRS PDF to CSV Converter - Executable Batch File
REM Windows batch file to run the Python application with GUI

chcp 65001 >nul
cls

echo.
echo ========================================
echo KRS PDF to CSV Converter
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python nie jest zainstalowany lub nie jest w PATH
    echo Pobierz Python z: https://www.python.org/
    echo.
    pause
    exit /b 1
)

REM Install required packages
echo Sprawdzam wymagane pakiety...
pip install -q pdfplumber pandas PyPDF2 2>nul

if errorlevel 1 (
    echo Instaluję wymagane pakiety...
    pip install pdfplumber pandas PyPDF2
    if errorlevel 1 (
        echo ERROR: Nie udało się zainstalować pakietów
        pause
        exit /b 1
    )
)

REM Run the application
echo.
echo Uruchamiam aplikację...
echo.
python krs_pdf_to_csv.py

if errorlevel 1 (
    echo.
    echo Błąd przy uruchomieniu aplikacji!
    pause
)
