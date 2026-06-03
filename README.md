# KRS PDF to CSV Converter 🚀

Aplikacja z interfejsem graficznym (GUI) do automatycznej konwersji plików PDF z Krajowego Rejestru Sądowego (KRS) na ustrukturyzowane pliki CSV.

## ✨ Nowe Funkcje (v2.0)

- ✅ **Interfejs Graficzny (GUI)** - Łatwy do użycia interfejs bez konieczności linii poleceń
- ✅ **Wybór Wielu Plików Naraz** - Zaznacz wiele PDF-ów jednocześnie
- ✅ **Osobne Pliki CSV** - Każda kategoria danych w osobnym pliku:
  - `firmy_*.csv` - Dane firm
  - `pracownicy_*.csv` - Lista pracowników
  - `kierownictwo_*.csv` - Dane kierownictwa
  - `prokurenci_*.csv` - Prokurenci i pełnomocnicy
  - `daty_zmian_*.csv` - Historia zmian wpisów
  - `zakresy_dzialalnosci_*.csv` - Zakresy działalności (PKD)
- ✅ **Uruchamianie z Dowolnego Miejsca** - Aplikacja działa niezależnie od lokalizacji
- ✅ **Wybór Folderu Docelowego** - Wskaż gdzie mają być zapisane pliki CSV
- ✅ **Progress Bar** - Wizualizacja postępu przetwarzania
- ✅ **Status Komunikaty** - Otrzymuj informacje o postępie w czasie rzeczywistym

## 📋 Ekstrahowane Dane

Aplikacja ekstrahuje następujące informacje z PDF-ów:
- **Nazwa firmy**
- **Numer KRS** (10 cyfr)
- **Adres siedziby**
- **Pracownicy**
- **Kierownictwo**
- **Prokurenci/Pełnomocnicy**
- **Daty zmian wpisów**
- **Zakres działalności (PKD)**

## 🛠️ Wymagania Systemowe

- **Python 3.7+**
- System Windows, macOS lub Linux
- Internet (do pobrania bibliotek przy pierwszym uruchomieniu)

## 📦 Instalacja

### Opcja 1: Automatyczne Uruchomienie (Rekomendowane)

**Windows:**
1. Pobierz folder projektu
2. Kliknij dwa razy na `run.bat`
3. Aplikacja uruchomi się automatycznie

**Linux/macOS:**
```bash
chmod +x run.sh
./run.sh
```

### Opcja 2: Manualna Instalacja

```bash
# 1. Zainstaluj wymagane pakiety
pip install -r requirements.txt

# 2. Uruchom aplikację
python krs_pdf_to_csv.py
```

## 🚀 Jak Używać

1. **Uruchom aplikację:**
   - **Windows:** Kliknij `run.bat`
   - **Linux/macOS:** Uruchom `./run.sh`

2. **Wybierz pliki PDF:**
   - Kliknij przycisk "📁 Wybierz pliki PDF"
   - Zaznacz jeden lub wiele plików PDF
   - Kliknij "Otwórz"

3. **Wybierz folder docelowy (opcjonalnie):**
   - Domyślnie pliki są zapisywane na Pulpicie
   - Kliknij "📂 Wybierz folder do zapisu" aby zmienić lokalizację

4. **Konwertuj:**
   - Kliknij przycisk "✅ Konwertuj do CSV"
   - Czekaj aż postęp zostanie ukończony
   - Otrzymasz potwierdzenie po zakończeniu

5. **Otwórz wyniki:**
   - Wszystkie pliki CSV zostały zapisane w wybranym folderze
   - Otwórz je w Excelu lub innym edytorze CSV

## 📊 Format Wyjściowych Plików

### firmy_*.csv
```csv
"Nazwa Firmy","Numer KRS","Adres","Zakres Działalności"
"ABC Sp. z o.o.","0000020787","ul. Example 123, 00-000 Warszawa","Usługi IT"
```

### pracownicy_*.csv
```csv
"Numer KRS","Nazwa Firmy","Pracownik"
"0000020787","ABC Sp. z o.o.","Jan Kowalski"
"0000020787","ABC Sp. z o.o.","Maria Nowak"
```

### kierownictwo_*.csv
```csv
"Numer KRS","Nazwa Firmy","Kierownik"
"0000020787","ABC Sp. z o.o.","Jan Kowalski"
```

### prokurenci_*.csv
```csv
"Numer KRS","Nazwa Firmy","Prokurent"
"0000020787","ABC Sp. z o.o.","Anna Lewandowska"
```

### daty_zmian_*.csv
```csv
"Numer KRS","Nazwa Firmy","Data Zmian"
"0000020787","ABC Sp. z o.o.","01-03-2024"
"0000020787","ABC Sp. z o.o.","15-06-2023"
```

### zakresy_dzialalnosci_*.csv
```csv
"Numer KRS","Nazwa Firmy","Zakres Działalności"
"0000020787","ABC Sp. z o.o.","62.01.Z Działalność związana z oprogramowaniem"
```

## 📁 Struktura Projektu

```
KRS_PDF/
├── krs_pdf_to_csv.py           # Główny skrypt aplikacji GUI
├── requirements.txt             # Zależności Pythona
├── run.bat                      # Executable dla Windows
├── run.sh                       # Executable dla Linux/macOS
├── README.md                    # Ten plik
└── *.pdf                        # Pliki PDF do przetworzenia (dodaj tutaj)
```

## 🔧 Rozwiązywanie Problemów

### Problem: Okno GUI się nie pojawia
```bash
# Spróbuj uruchomić bezpośrednio
python krs_pdf_to_csv.py
```

### Problem: "Python nie znaleziony"
- Zainstaluj Python z https://www.python.org/
- Upewnij się, że opcja "Add Python to PATH" jest zaznaczona podczas instalacji

### Problem: "Moduły nie znalezione"
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Problem: Pliki CSV są puste
- Sprawdź czy PDF-y zawierają tekst (nie tylko obrazy)
- Upewnij się, że PDF-y mają prawidłowy format KRS
- Sprawdź komunikaty błędów w oknie aplikacji

### Problem: Dane nie są prawidłowo ekstrahowane
- Różne wersje formatu KRS mogą wymagać dostosowania
- Skontaktuj się podając przykładowy plik PDF

## 💡 Tips & Tricks

- **Batch Processing:** Możesz przetwarzać wiele plików naraz - aplikacja stworzy osobne wiersze w każdym CSV
- **Timestampy:** Każdy plik CSV ma timestamp w nazwie (YYYYMMDD_HHMMSS) - łatwo odróżnić nowe konwersje
- **Excel Compatibility:** Wszystkie pliki CSV są kompatybilne z Microsoft Excel
- **UTF-8 Encoding:** Prawidłowe znaki diakrytyczne oraz polskie znaki specjalne

## 📝 Notatki Techniczne

- Aplikacja używa `pdfplumber` do ekstrahowania tekstu z PDF-ów
- Dane są przetwarzane za pomocą wyrażeń regularnych (regex)
- Dokładność ekstrakcji zależy od formatu i jakości PDF-u
- CSV-y są zapisywane w kodowaniu UTF-8 BOM (kompatybilne z Excel)

## 🤝 Wsparcie i Błędy

W przypadku problemów:
1. Sprawdź czy Python jest zainstalowany: `python --version`
2. Zainstaluj ponownie pakiety: `pip install -r requirements.txt`
3. Spróbuj uruchomić: `python krs_pdf_to_csv.py`
4. Sprawdź komunikaty błędów w oknie aplikacji

## 📄 Licencja

MIT License - wolne do użytku prywatnego i komercyjnego

## 👨‍💻 Autor

Copilot GitHub  
Ostatnia aktualizacja: 2026-06-03

---

**Gotowy do użycia!** 🎉 Uruchom `run.bat` (Windows) lub `./run.sh` (Linux/macOS) aby rozpocząć.
