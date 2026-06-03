# KRS PDF to CSV Converter 🚀 v3.0

Profesjonalna aplikacja z interfejsem graficznym (GUI) do automatycznej konwersji plików PDF z Krajowego Rejestru Sądowego (KRS) na ustrukturyzowane pliki CSV.

## ✨ Nowe Funkcje v3.0

- ✅ **Prawidłowa Ekstrakcja Danych** - Wszystkie sekcje KRS prawidłowo rozpoznawane
- ✅ **8 Osobnych Plików CSV** - Każda kategoria danych w oddzielnym pliku:
  - `podmioty_*.csv` - Dane podmiotu (KRS, nazwa, forma prawna, NIP, REGON)
  - `siedziby_adresy_*.csv` - Siedziby i adresy z historią zmian
  - `wspolnicy_akcjonariusze_*.csv` - Wspólnicy/Akcjonariusze z udziałami
  - `organy_reprezentacji_*.csv` - Organy uprawnione do reprezentacji (Zarząd)
  - `organy_nadzoru_*.csv` - Organy nadzoru (Rada Nadzorcza)
  - `prokurenci_*.csv` - Prokurenci i pełnomocnicy
  - `przedmiot_dzialalnosci_*.csv` - Zakresy działalności (PKD)
  - `zestawienie_zmian_*.csv` - Historia zmian wpisów w KRS

- ✅ **Wybór Wielu Plików Naraz** - Zaznacz wiele PDF-ów jednocześnie
- ✅ **Uruchamianie z Dowolnego Miejsca** - Aplikacja działa niezależnie od lokalizacji
- ✅ **Wybór Folderu Docelowego** - Wskaż gdzie mają być zapisane pliki CSV
- ✅ **Progress Bar** - Wizualizacja postępu przetwarzania
- ✅ **Status Komunikaty** - Otrzymuj informacje o postępie w czasie rzeczywistym

## 📋 Ekstrahowane Dane

### Dział 1 - Dane Identyfikacyjne:
- **Numer KRS** (10 cyfr)
- **Nazwa Firmy** (Firma pod którą spółka działa)
- **Forma Prawna** (Sp. z o.o., S.A., etc.)
- **REGON** i **NIP**

### Siedziby i Adresy (Rubryka 2):
- Siedziба główna
- Adresy (aktalne i historyczne)
- Email, strona internetowa
- Adres do doręczeń elektronicznych

### Wspólnicy (Rubryka 7):
- Imiona i nazwiska (lub nazwa firmy)
- PESEL/REGON
- Liczba udziałów
- Wartość udziałów
- Procent udziału

### Dział 2 - Organy:
- **Organy Reprezentacji** - Zarząd (Prezydenci, Członkowie)
- **Organy Nadzoru** - Rada Nadzorcza (Przewodniczący, Członkowie)
- **Prokurenci** - Pełnomocnicy

### Dział 3 - Działalność:
- **Główna Działalność (PKD)**
- **Pozostałe Zakresy Działalności (PKD)**

### Historia Zmian:
- Daty wpisów
- Opisy zmian
- Sygnatury akt
- Informacje o sądach

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

### podmioty_*.csv
```csv
Numer KRS,Nazwa Firmy,Forma Prawna,REGON,NIP
0001232756,STELVAR SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ,SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ,544388827,6492340175
```

### siedziby_adresy_*.csv
```csv
Numer KRS,Nazwa Firmy,Typ Adresu,Adres,Nr Wpisu
0001232756,STELVAR SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ,Siedziba,"ul. POLEGŁYCH, nr 62, 42-400 ZAWIERCIE",1
```

### wspolnicy_akcjonariusze_*.csv
```csv
Numer KRS,Nazwa Firmy,Imiona,Nazwisko,PESEL/REGON,Udziały,Procent,Nr Wpisu
0001232756,STELVAR SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ,MARCIN,JANOSKA,88092615630,50 UDZIAŁÓW O ŁĄCZNEJ WARTOŚCI 25000 PLN,50,1
```

### organy_reprezentacji_*.csv
```csv
Numer KRS,Nazwa Firmy,Imiona,Nazwisko,PESEL/REGON,Funkcja,Nr Wpisu
0001232756,STELVAR SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ,MARCIN,JANOSKA,88092615630,PREZES ZARZĄDU,1
```

### prokurenci_*.csv
```csv
Numer KRS,Nazwa Firmy,Imiona,Nazwisko,PESEL/REGON,Nr Wpisu
0001232756,STELVAR SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ,ANNA,LEWANDOWSKA,12345678901,1
```

### przedmiot_dzialalnosci_*.csv
```csv
Numer KRS,Nazwa Firmy,Typ,Zawartość,Nr Wpisu
0001232756,STELVAR SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ,Przeważająca,71 12 B POZOSTAŁA DZIAŁALNOŚĆ,1
```

### zestawienie_zmian_*.csv
```csv
Numer KRS,Nazwa Firmy,Nr Wpisu,Data,Opis,Sygnatura Akt,Sąd
0001232756,STELVAR SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ,1,27.03.2026,REJESTRACJA W KRAJOWYM REJESTRZE SĄDOWYM,KA.VIII NS-REJ.KRS/11389/26/578,SĄD REJONOWY KATOWICE
```

## 📁 Struktura Projektu

```
KRS_PDF/
├── krs_pdf_to_csv.py           # Główny skrypt aplikacji v3.0
├── requirements.txt             # Zależności Pythona
├── run.bat                      # Executable dla Windows
├── run.sh                       # Executable dla Linux/macOS
├── CREATE_SHORTCUT.bat          # Tworzenie skrótu (Windows)
├── README.md                    # Ten plik
└── *.pdf                        # Pliki PDF do przetworzenia (dodaj tutaj)
```

## 🔧 Rozwiązywanie Problemów

### Problem: Okno GUI się nie pojawia
```bash
Spróbuj uruchomić bezpośrednio:
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

### Problem: Dane nie są prawidłowo ekstrahowane
- Sprawdź czy PDF jest oficjalnym odpisem KRS
- Upewnij się, że PDF zawiera tekst (nie tylko obrazy)
- Skontaktuj się podając przykładowy plik PDF

## 💡 Tips & Tricks

- **Batch Processing:** Przetwarzaj wiele firm naraz - wszystkie dane zostaną w jednym zestawie plików
- **Timestampy:** Każdy plik CSV ma timestamp (YYYYMMDD_HHMMSS) - łatwo rozróżniać konwersje
- **Excel Compatibility:** Wszystkie pliki CSV są kompatybilne z Microsoft Excel
- **UTF-8 Encoding:** Prawidłowe znaki diakrytyczne oraz polskie znaki specjalne

## 📝 Notatki Techniczne

- Aplikacja używa `pdfplumber` do ekstrahowania tekstu z PDF-ów
- Dane są przetwarzane za pomocą wyrażeń regularnych (regex)
- Dokładność ekstrakcji zależy od formatu PDF
- CSV-y są zapisywane w kodowaniu UTF-8 BOM (kompatybilne z Excel)
- Aplikacja obsługuje wielokrotne adresy i zmiany historyczne

## 🤝 Wsparcie

W przypadku problemów:
1. Sprawdź czy Python jest zainstalowany: `python --version`
2. Zainstaluj ponownie pakiety: `pip install -r requirements.txt`
3. Spróbuj uruchomić: `python krs_pdf_to_csv.py`
4. Sprawdź komunikaty błędów w oknie aplikacji

## 📄 Licencja

MIT License - wolne do użytku prywatnego i komercyjnego

## 👨‍💻 Historia Wersji

- **v3.0** (2026-06-03) - Kompletna restrukturyzacja, 8 plików CSV, prawidłowa ekstrakcja danych
- v2.0 - GUI Interface
- v1.0 - Podstawowa wersja konsolowa

---

**Gotowy do użycia!** 🎉 Uruchom `run.bat` (Windows) lub `./run.sh` (Linux/macOS) aby rozpocząć.
