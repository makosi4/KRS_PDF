@echo off
REM KRS PDF to CSV Converter - Windows Batch File
chcp 65001 >nul
cls

echo.
echo ========================================
echo KRS PDF to CSV Converter
echo ========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Download Python from: https://www.python.org/
    echo.
    pause
    exit /b 1
)

echo Checking required packages...
pip install -q pdfplumber pandas PyPDF2 2>nul

if errorlevel 1 (
    echo Installing required packages...
    pip install pdfplumber pandas PyPDF2
    if errorlevel 1 (
        echo ERROR: Failed to install packages
        pause
        exit /b 1
    )
)

echo.
echo Starting application...
echo.
python krs_pdf_to_csv.py

if errorlevel 1 (
    echo.
    echo Application error occurred!
    pause
)
