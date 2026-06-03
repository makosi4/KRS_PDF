#!/bin/bash
# KRS PDF to CSV Converter - Executable Shell Script
# Linux/macOS shell script to run the Python application with GUI

clear

echo ""
echo "========================================"
echo "KRS PDF to CSV Converter"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 nie jest zainstalowany"
    echo "Zainstaluj Python: https://www.python.org/"
    read -p "Naciśnij Enter aby zamknąć..."
    exit 1
fi

# Install required packages
echo "Sprawdzam wymagane pakiety..."
pip3 install -q pdfplumber pandas PyPDF2 2>/dev/null

if [ $? -ne 0 ]; then
    echo "Instaluję wymagane pakiety..."
    pip3 install pdfplumber pandas PyPDF2
    if [ $? -ne 0 ]; then
        echo "ERROR: Nie udało się zainstalować pakietów"
        read -p "Naciśnij Enter aby zamknąć..."
        exit 1
    fi
fi

# Run the application
echo ""
echo "Uruchamiam aplikację..."
echo ""
python3 krs_pdf_to_csv.py

if [ $? -ne 0 ]; then
    echo ""
    echo "Błąd przy uruchomieniu aplikacji!"
    read -p "Naciśnij Enter aby zamknąć..."
fi
