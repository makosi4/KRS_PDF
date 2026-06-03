#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KRS PDF to CSV Converter - v3.1 (Poprawiona Wersja)
Aplikacja do konwersji plików PDF z KRS na ustrukturyzowane pliki CSV
Ekstrahuje wszystkie kategorie danych: wspólnicy, kierownictwo, adresy, prokurenci, etc.
"""

import os
import csv
import re
import sys
import threading
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pdfplumber
import pandas as pd
from typing import Dict, List, Tuple, Optional


class KRSPDFExtractor:
    """Klasa do ekstrakcji danych z plików PDF KRS"""
    
    def __init__(self):
        self.reset_data()
    
    def reset_data(self):
        """Resetuje dane"""
        self.data = {
            'numer_krs': '',
            'nazwa_firmy': '',
            'forma_prawna': '',
            'regon': '',
            'nip': '',
            'siedziby_adresy': [],
            'wspolnicy_akcjonariusze': [],
            'organy_reprezentacji': [],
            'organy_nadzoru': [],
            'prokurenci': [],
            'przedmiot_dzialalnosci': [],
            'zestawienie_zmian': []
        }
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Ekstrahuje cały tekst z pliku PDF"""
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
            return text
        except Exception as e:
            print(f"Błąd podczas czytania PDF: {e}")
            return ""
    
    def extract_krs_number(self, text: str) -> str:
        """Wyciąga numer KRS"""
        match = re.search(r'Numer KRS:\s*(\d{10})', text)
        if match:
            return match.group(1)
        return ""
    
    def extract_company_name(self, text: str) -> str:
        """Wyciąga nazwę firmy (Firma, pod którą spółka działa)"""
        # Szuka "3.Firma, pod którą spółka działa" w Rubryce 1
        pattern = r'3\.Firma,\s*pod którą spółka działa\s+\d+-(.+?)(?=\n\d\.|Dane o wcześniejszej|\Z)'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""
    
    def extract_legal_form(self, text: str) -> str:
        """Wyciąga formę prawną"""
        pattern = r'1\.Oznaczenie formy prawnej\s+\d+-(.+?)(?=\n\d\.|\Z)'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""
    
    def extract_regon_nip(self, text: str) -> Tuple[str, str]:
        """Wyciąga REGON i NIP"""
        regon = ""
        nip = ""
        
        # Szuka całej sekcji REGON/NIP
        pattern = r'2\.Numer REGON/NIP\s+\d+-REGON:\s*([^,]+),\s*NIP:\s*(.+?)(?=\n\d\.|\Z)'
        matches = re.findall(pattern, text, re.DOTALL)
        
        if matches:
            # Bierze ostatni (najnowszy wpis)
            last_match = matches[-1]
            regon = last_match[0].strip()
            nip = last_match[1].strip()
        
        return regon, nip
    
    def extract_siedziby_adresy(self, text: str) -> List[Dict]:
        """Wyciąga siedziby i adresy z Rubryki 2"""
        adresy = []
        
        # Szuka sekcji Rubryka 2
        pattern = r'Rubryka 2\s+Siedziba i adres podmiotu(.*?)(?=Rubryka 3|Oddziały|\Z)'
        match = re.search(pattern, text, re.DOTALL)
        
        if not match:
            return adresy
        
        section = match.group(1)
        
        # Szuka pól z numerami wpisów
        # Format: "1.Siedziba 1-kraj POLSKA..."
        # Szuka linii zawierających "Siedziba" lub "Adres"
        lines = section.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Szuka linii "1.Siedziba" lub "2.Adres"
            if ('Siedziba' in line or 'Adres' in line) and '-' in line:
                # Wydobywa nr wpisu
                nr_wpisu_match = re.search(r'(\d+)-', line)
                if nr_wpisu_match:
                    nr_wpisu = nr_wpisu_match.group(1)
                    
                    # Wydobywa zawartość (może być wielolinijkowa)
                    content = re.sub(r'^\d+\.\s*\w+\s+\d+-', '', line).strip()
                    
                    # Jeśli jest więcej zawartości poniżej
                    i += 1
                    while i < len(lines) and lines[i].strip() and not re.match(r'^\d+\.', lines[i]):
                        content += " " + lines[i].strip()
                        i += 1
                    
                    if content:
                        adresy.append({
                            'typ': 'Siedziba' if 'Siedziba' in line else 'Adres',
                            'nr_wpisu': nr_wpisu,
                            'content': content
                        })
                    continue
            i += 1
        
        return adresy
    
    def extract_wspolnicy_akcjonariusze(self, text: str) -> List[Dict]:
        """Wyciąga wspólników i akcjonariuszy z Rubryki 7"""
        wspolnicy = []
        
        # Szuka sekcji Rubryka 7
        pattern = r'Rubryka 7\s+Dane wspólników(.*?)(?=Rubryka 8|Kapitał spółki|\Z)'
        match = re.search(pattern, text, re.DOTALL)
        
        if not match:
            return wspolnicy
        
        section = match.group(1)
        
        # Szuka bloków wspólników - każdy zaczyna się od "L.p." lub bezpośrednio od numeru
        # Format: "1 1.Nazwisko / Nazwa lub firma 1-JANOSKA"
        
        # Szuka wszystkich wspólników (L.p. = liczba porządkowa)
        wspolnik_pattern = r'(\d+)\s+1\.Nazwisko.*?(?=\n\d+\s+1\.Nazwisko|Rubryka 8|Kapitał|\Z)'
        
        for wspolnik_match in re.finditer(wspolnik_pattern, section, re.DOTALL):
            wspolnik_block = wspolnik_match.group(0)
            wspolnik = self._parse_wspolnik(wspolnik_block)
            if wspolnik:
                wspolnicy.append(wspolnik)
        
        return wspolnicy
    
    def _parse_wspolnik(self, content: str) -> Optional[Dict]:
        """Parsuje dane wspólnika z bloku tekstu"""
        wspolnik = {
            'lp': '',
            'nr_wpisu': '',
            'nazwisko': '',
            'imiona': '',
            'pesel_regon': '',
            'udzialy': '',
            'wartosc': '',
            'procent': '0'
        }
        
        # Liczba porządkowa
        match = re.search(r'^(\d+)\s+1\.', content)
        if match:
            wspolnik['lp'] = match.group(1)
        
        # Nazwisko
        match = re.search(r'1\.Nazwisko.*?\d+-(.+?)(?=\n2\.)', content, re.DOTALL)
        if match:
            wspolnik['nazwisko'] = match.group(1).strip()
        
        # Imiona
        match = re.search(r'2\.Imiona\s+\d+-(.+?)(?=\n3\.)', content, re.DOTALL)
        if match:
            wspolnik['imiona'] = match.group(1).strip()
        
        # PESEL/REGON
        match = re.search(r'3\.Numer PESEL.*?\d+-(.+?)(?=\n4\.)', content, re.DOTALL)
        if match:
            pesel_text = match.group(1).strip()
            # Wyciąga tylko liczbę PESEL/REGON (pierwszą cyfrową grupę)
            pesel_match = re.search(r'(\d+)', pesel_text)
            if pesel_match:
                wspolnik['pesel_regon'] = pesel_match.group(1)
        
        # Udziały (pola 5)
        match = re.search(r'5\.Posiadane przez wspólnika udziały\s+\d+-(.+?)(?=\n6\.)', content, re.DOTALL)
        if match:
            udzialy_text = match.group(1).strip()
            wspolnik['udzialy'] = udzialy_text
            
            # Wyciąga procent jeśli jest
            procent_match = re.search(r'(\d+(?:[.,]\d+)?)\s*%', udzialy_text)
            if procent_match:
                wspolnik['procent'] = procent_match.group(1)
            
            # Wyciąga nr wpisu z tego pola
            nr_wpisu_match = re.search(r'^(\d+)-', match.group(1))
            if nr_wpisu_match:
                wspolnik['nr_wpisu'] = nr_wpisu_match.group(1)
        
        return wspolnik if wspolnik['nazwisko'] else None
    
    def extract_organy_reprezentacji(self, text: str) -> List[Dict]:
        """Wyciąga organy uprawnione do reprezentacji (Zarząd)"""
        organy = []
        
        # Szuka Rubryka 1 w Dziale 2
        pattern = r'Dział 2.*?Rubryka 1\s+Organ uprawniony do reprezentacji podmiotu(.*?)(?=Rubryka 2|Organ nadzoru|\Z)'
        match = re.search(pattern, text, re.DOTALL)
        
        if not match:
            return organy
        
        section = match.group(1)
        
        # Szuka "Dane osób wchodzących w skład organu"
        osoby_pattern = r'Dane osób wchodzących w skład organu(.*?)(?=Rubryka 2|Organ nadzoru|\Z)'
        osoby_match = re.search(osoby_pattern, section, re.DOTALL)
        
        if not osoby_match:
            return organy
        
        osoby_section = osoby_match.group(1)
        
        # Szuka bloków osób - każdy zaczyna się od "L.p."
        osoba_pattern = r'(\d+)\s+1\.Nazwisko.*?(?=\n\d+\s+1\.Nazwisko|\nRubryka|\Z)'
        
        for osoba_match in re.finditer(osoba_pattern, osoby_section, re.DOTALL):
            osoba_block = osoba_match.group(0)
            osoba = self._parse_osoba_organu(osoba_block)
            if osoba:
                organy.append(osoba)
        
        return organy
    
    def _parse_osoba_organu(self, content: str) -> Optional[Dict]:
        """Parsuje osobę w organie"""
        osoba = {
            'lp': '',
            'nr_wpisu': '',
            'nazwisko': '',
            'imiona': '',
            'pesel_regon': '',
            'funkcja': ''
        }
        
        # Liczba porządkowa
        match = re.search(r'^(\d+)\s+1\.', content)
        if match:
            osoba['lp'] = match.group(1)
        
        # Nazwisko
        match = re.search(r'1\.Nazwisko.*?\d+-(.+?)(?=\n2\.)', content, re.DOTALL)
        if match:
            osoba['nazwisko'] = match.group(1).strip()
        
        # Imiona
        match = re.search(r'2\.Imiona\s+\d+-(.+?)(?=\n3\.)', content, re.DOTALL)
        if match:
            osoba['imiona'] = match.group(1).strip()
        
        # PESEL/REGON
        match = re.search(r'3\.Numer PESEL.*?\d+-(.+?)(?=\n4\.)', content, re.DOTALL)
        if match:
            pesel_text = match.group(1).strip()
            pesel_match = re.search(r'(\d+)', pesel_text)
            if pesel_match:
                osoba['pesel_regon'] = pesel_match.group(1)
        
        # Nr wpisu z pola 1 (Nazwisko)
        match = re.search(r'1\.Nazwisko.*?(\d+)-', content)
        if match:
            osoba['nr_wpisu'] = match.group(1)
        
        # Funkcja (pole 5)
        match = re.search(r'5\.Funkcja w organie\s+\d+-(.+?)(?=\n6\.|\Z)', content, re.DOTALL)
        if match:
            osoba['funkcja'] = match.group(1).strip()
        
        return osoba if osoba['nazwisko'] else None
    
    def extract_organy_nadzoru(self, text: str) -> List[Dict]:
        """Wyciąga organy nadzoru (Rada Nadzorcza)"""
        nadzoru = []
        
        # Szuka Rubryka 2 w Dziale 2
        pattern = r'Rubryka 2\s+Organ nadzoru(.*?)(?=Rubryka 3|Prokurenci|\Z)'
        match = re.search(pattern, text, re.DOTALL)
        
        if not match:
            return nadzoru
        
        section = match.group(1)
        
        if 'Brak wpisów' in section:
            return nadzoru
        
        # Szuka bloków osób nadzoru
        osoba_pattern = r'(\d+)\s+1\.Nazwisko.*?(?=\n\d+\s+1\.Nazwisko|\nRubryka|\Z)'
        
        for osoba_match in re.finditer(osoba_pattern, section, re.DOTALL):
            osoba_block = osoba_match.group(0)
            osoba = self._parse_osoba_organu(osoba_block)
            if osoba:
                nadzoru.append(osoba)
        
        return nadzoru
    
    def extract_prokurenci(self, text: str) -> List[Dict]:
        """Wyciąga prokurów"""
        prokurenci = []
        
        # Szuka Rubryka 3 w Dziale 2
        pattern = r'Rubryka 3\s+Prokurenci(.*?)(?=Dział 3|\Z)'
        match = re.search(pattern, text, re.DOTALL)
        
        if not match:
            return prokurenci
        
        section = match.group(1)
        
        if 'Brak wpisów' in section:
            return prokurenci
        
        # Szuka bloków osób prokurów
        osoba_pattern = r'(\d+)\s+1\.Nazwisko.*?(?=\n\d+\s+1\.Nazwisko|\nRubryka|\Z)'
        
        for osoba_match in re.finditer(osoba_pattern, section, re.DOTALL):
            osoba_block = osoba_match.group(0)
            osoba = self._parse_osoba_organu(osoba_block)
            if osoba:
                prokurenci.append(osoba)
        
        return prokurenci
    
    def extract_przedmiot_dzialalnosci(self, text: str) -> List[Dict]:
        """Wyciąga przedmiot działalności (PKD) z Dział 3, Rubryka 1"""
        dzialalnosc = []
        
        # Szuka Dział 3 -> Rubryka 1 Przedmiot działalności
        pattern = r'Dział 3.*?Rubryka 1\s+Przedmiot działalności(.*?)(?=Rubryka 2|\Z)'
        match = re.search(pattern, text, re.DOTALL)
        
        if not match:
            return dzialalnosc
        
        section = match.group(1)
        
        # Szuka "1.Przedmiot przeważającej działalności"
        przewazajaca_match = re.search(r'1\.Przedmiot przeważającej działalności(.*?)(?=2\.Przedmiot pozostałej|\Z)', section, re.DOTALL)
        
        if przewazajaca_match:
            przewazajaca_section = przewazajaca_match.group(1)
            # Szuka numerów wpisów z zawartością
            wpisy_pattern = r'(\d+)\s+(\d+)-(.+?)(?=\n\d+\s+\d+-|$)'
            
            for wpis_match in re.finditer(wpisy_pattern, przewazajaca_section, re.DOTALL):
                lp = wpis_match.group(1)
                nr_wpisu = wpis_match.group(2)
                content = wpis_match.group(3).strip()
                
                if content:
                    dzialalnosc.append({
                        'typ': 'Przeważająca',
                        'nr_wpisu': nr_wpisu,
                        'lp': lp,
                        'content': content
                    })
        
        # Szuka "2.Przedmiot pozostałej działalności"
        pozostala_match = re.search(r'2\.Przedmiot pozostałej działalności(.*?)(?=Rubryka 2|\Z)', section, re.DOTALL)
        
        if pozostala_match:
            pozostala_section = pozostala_match.group(1)
            wpisy_pattern = r'(\d+)\s+(\d+)-(.+?)(?=\n\d+\s+\d+-|$)'
            
            for wpis_match in re.finditer(wpisy_pattern, pozostala_section, re.DOTALL):
                lp = wpis_match.group(1)
                nr_wpisu = wpis_match.group(2)
                content = wpis_match.group(3).strip()
                
                if content:
                    dzialalnosc.append({
                        'typ': 'Pozostała',
                        'nr_wpisu': nr_wpisu,
                        'lp': lp,
                        'content': content
                    })
        
        return dzialalnosc
    
    def extract_zestawienie_zmian(self, text: str) -> List[Dict]:
        """Wyciąga zestawienie zmian z początku dokumentu"""
        zmiany = []
        
        # Szuka sekcji z "Nr wpisu X Data dokonania wpisu"
        pattern = r'Nr wpisu\s+(\d+)\s+Data dokonania wpisu\s+([\d.]+)\s+Opis\s+(.*?)(?=Nr wpisu\s+\d+\s+Data|Stan na dzień|\Z)'
        
        for match in re.finditer(pattern, text, re.DOTALL):
            nr_wpisu = match.group(1)
            data = match.group(2)
            opis_raw = match.group(3).strip()
            
            # Wyciąga sygnaturę akt
            sygnatura_match = re.search(r'Sygnatura akt\s+([^\n]+)', opis_raw)
            sygnatura = sygnatura_match.group(1).strip() if sygnatura_match else ""
            
            # Wyciąga sąd
            sad_match = re.search(r'Oznaczenie sądu\s+([^\n]+?)(?=Nr wpisu|$)', opis_raw, re.DOTALL)
            sad = sad_match.group(1).strip() if sad_match else ""
            
            # Wyciąga opis (bez sygnatur i sądów)
            opis = re.sub(r'Sygnatura akt.*', '', opis_raw).strip()
            opis = re.sub(r'Oznaczenie sądu.*', '', opis).strip()
            opis = opis.split('\n')[0].strip()
            
            zmiany.append({
                'nr_wpisu': nr_wpisu,
                'data': data,
                'opis': opis,
                'sygnatura': sygnatura,
                'sad': sad
            })
        
        return zmiany
    
    def extract_all_data(self, pdf_path: str) -> Dict:
        """Główna metoda ekstrakcji wszystkich danych"""
        self.reset_data()
        text = self.extract_text_from_pdf(pdf_path)
        
        if not text:
            return self.data
        
        self.data['numer_krs'] = self.extract_krs_number(text)
        self.data['nazwa_firmy'] = self.extract_company_name(text)
        self.data['forma_prawna'] = self.extract_legal_form(text)
        self.data['regon'], self.data['nip'] = self.extract_regon_nip(text)
        self.data['siedziby_adresy'] = self.extract_siedziby_adresy(text)
        self.data['wspolnicy_akcjonariusze'] = self.extract_wspolnicy_akcjonariusze(text)
        self.data['organy_reprezentacji'] = self.extract_organy_reprezentacji(text)
        self.data['organy_nadzoru'] = self.extract_organy_nadzoru(text)
        self.data['prokurenci'] = self.extract_prokurenci(text)
        self.data['przedmiot_dzialalnosci'] = self.extract_przedmiot_dzialalnosci(text)
        self.data['zestawienie_zmian'] = self.extract_zestawienie_zmian(text)
        
        return self.data


class KRSConverterGUI:
    """Główna klasa aplikacji GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("KRS PDF to CSV Converter v3.1")
        self.root.geometry("750x650")
        self.root.resizable(True, True)
        
        self.selected_files = []
        self.extractor = KRSPDFExtractor()
        self.output_dir = str(Path.home() / "Desktop")
        self.is_processing = False
        
        self.setup_ui()
        self.center_window()
    
    def center_window(self):
        """Centruje okno na ekranie"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_ui(self):
        """Tworzy interfejs użytkownika"""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Tytuł
        title_label = ttk.Label(main_frame, text="KRS PDF to CSV Converter v3.1", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Separator
        ttk.Separator(main_frame, orient="horizontal").grid(row=1, column=0, columnspan=2, sticky="ew", pady=10)
        
        # Przycisk wyboru plików
        ttk.Button(main_frame, text="📁 Wybierz pliki PDF", command=self.select_files).grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)
        
        # Lista plików
        list_frame = ttk.LabelFrame(main_frame, text="Wybrane pliki PDF", padding="10")
        list_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=10)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_listbox.yview)
        
        # Przycisk usuwania
        ttk.Button(main_frame, text="🗑️ Usuń zaznaczony plik", command=self.remove_selected_file).grid(row=4, column=0, columnspan=2, sticky="ew", pady=5)
        
        ttk.Separator(main_frame, orient="horizontal").grid(row=5, column=0, columnspan=2, sticky="ew", pady=10)
        
        # Folder wyjścia
        ttk.Button(main_frame, text="📂 Wybierz folder do zapisu", command=self.select_output_dir).grid(row=6, column=0, columnspan=2, sticky="ew", pady=5)
        
        self.output_label = ttk.Label(main_frame, text="Folder: Pulpit", foreground="blue")
        self.output_label.grid(row=7, column=0, columnspan=2, sticky="ew", pady=5)
        
        ttk.Separator(main_frame, orient="horizontal").grid(row=8, column=0, columnspan=2, sticky="ew", pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode="indeterminate")
        self.progress.grid(row=9, column=0, columnspan=2, sticky="ew", pady=5)
        
        # Status
        self.status_label = ttk.Label(main_frame, text="Gotowy do pracy", foreground="green")
        self.status_label.grid(row=10, column=0, columnspan=2, sticky="ew", pady=5)
        
        # Przyciski
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=11, column=0, columnspan=2, sticky="ew", pady=10)
        
        ttk.Button(button_frame, text="✅ Konwertuj do CSV", command=self.start_conversion).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(button_frame, text="❌ Wyjście", command=self.root.quit).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
    
    def select_files(self):
        """Otwiera dialog wyboru plików"""
        files = filedialog.askopenfilenames(title="Wybierz pliki PDF", filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")])
        if files:
            self.selected_files.extend(files)
            self.update_file_list()
            self.update_status(f"Wybrano {len(self.selected_files)} plik(ów)", "blue")
    
    def remove_selected_file(self):
        """Usuwa zaznaczony plik"""
        selection = self.file_listbox.curselection()
        if selection:
            self.selected_files.pop(selection[0])
            self.update_file_list()
            self.update_status(f"Pozostało {len(self.selected_files)} plik(ów)", "blue")
    
    def update_file_list(self):
        """Aktualizuje listę"""
        self.file_listbox.delete(0, tk.END)
        for file in self.selected_files:
            self.file_listbox.insert(tk.END, Path(file).name)
    
    def select_output_dir(self):
        """Wybiera folder wyjścia"""
        folder = filedialog.askdirectory(title="Wybierz folder do zapisu")
        if folder:
            self.output_dir = folder
            display_path = folder if len(folder) < 40 else "..." + folder[-37:]
            self.output_label.config(text=f"Folder: {display_path}")
    
    def update_status(self, message: str, color: str = "black"):
        """Aktualizuje status"""
        self.status_label.config(text=message, foreground=color)
        self.root.update()
    
    def start_conversion(self):
        """Uruchamia konwersję"""
        if not self.selected_files:
            messagebox.showwarning("Błąd", "Nie wybrano żadnych plików!")
            return
        
        if self.is_processing:
            messagebox.showwarning("Ostrzeżenie", "Konwersja już trwa!")
            return
        
        thread = threading.Thread(target=self.convert_files)
        thread.start()
    
    def convert_files(self):
        """Główna metoda konwersji"""
        self.is_processing = True
        self.progress.start()
        self.update_status("Przetwarzam pliki...", "orange")
        
        try:
            # Inicjalizacja kolekcji
            all_podmioty = []
            all_adresy = []
            all_wspolnicy = []
            all_organy_repr = []
            all_organy_nadzoru = []
            all_prokurenci = []
            all_dzialalnosc = []
            all_zmiany = []
            
            total_files = len(self.selected_files)
            
            # Przetwarzanie każdego pliku
            for idx, pdf_path in enumerate(self.selected_files):
                try:
                    data = self.extractor.extract_all_data(pdf_path)
                    
                    # 1. Podmioty
                    if data['numer_krs']:
                        all_podmioty.append({
                            'Numer KRS': data['numer_krs'],
                            'Nazwa Firmy': data['nazwa_firmy'],
                            'Forma Prawna': data['forma_prawna'],
                            'REGON': data['regon'],
                            'NIP': data['nip']
                        })
                    
                    # 2. Adresy
                    for addr in data['siedziby_adresy']:
                        all_adresy.append({
                            'Numer KRS': data['numer_krs'],
                            'Nazwa Firmy': data['nazwa_firmy'],
                            'Typ Adresu': addr.get('typ', ''),
                            'Adres': addr.get('content', ''),
                            'Nr Wpisu': addr.get('nr_wpisu', '')
                        })
                    
                    # 3. Wspólnicy
                    for wspolnik in data['wspolnicy_akcjonariusze']:
                        all_wspolnicy.append({
                            'Numer KRS': data['numer_krs'],
                            'Nazwa Firmy': data['nazwa_firmy'],
                            'L.p.': wspolnik.get('lp', ''),
                            'Imiona': wspolnik.get('imiona', ''),
                            'Nazwisko': wspolnik.get('nazwisko', ''),
                            'PESEL/REGON': wspolnik.get('pesel_regon', ''),
                            'Udziały': wspolnik.get('udzialy', ''),
                            'Procent': wspolnik.get('procent', ''),
                            'Nr Wpisu': wspolnik.get('nr_wpisu', '')
                        })
                    
                    # 4. Organy reprezentacji
                    for organ in data['organy_reprezentacji']:
                        all_organy_repr.append({
                            'Numer KRS': data['numer_krs'],
                            'Nazwa Firmy': data['nazwa_firmy'],
                            'L.p.': organ.get('lp', ''),
                            'Imiona': organ.get('imiona', ''),
                            'Nazwisko': organ.get('nazwisko', ''),
                            'PESEL/REGON': organ.get('pesel_regon', ''),
                            'Funkcja': organ.get('funkcja', ''),
                            'Nr Wpisu': organ.get('nr_wpisu', '')
                        })
                    
                    # 5. Organy nadzoru
                    for nadzor in data['organy_nadzoru']:
                        all_organy_nadzoru.append({
                            'Numer KRS': data['numer_krs'],
                            'Nazwa Firmy': data['nazwa_firmy'],
                            'L.p.': nadzor.get('lp', ''),
                            'Imiona': nadzor.get('imiona', ''),
                            'Nazwisko': nadzor.get('nazwisko', ''),
                            'PESEL/REGON': nadzor.get('pesel_regon', ''),
                            'Funkcja': nadzor.get('funkcja', ''),
                            'Nr Wpisu': nadzor.get('nr_wpisu', '')
                        })
                    
                    # 6. Prokurenci
                    for prokurent in data['prokurenci']:
                        all_prokurenci.append({
                            'Numer KRS': data['numer_krs'],
                            'Nazwa Firmy': data['nazwa_firmy'],
                            'L.p.': prokurent.get('lp', ''),
                            'Imiona': prokurent.get('imiona', ''),
                            'Nazwisko': prokurent.get('nazwisko', ''),
                            'PESEL/REGON': prokurent.get('pesel_regon', ''),
                            'Nr Wpisu': prokurent.get('nr_wpisu', '')
                        })
                    
                    # 7. Działalność
                    for dzialalnosc in data['przedmiot_dzialalnosci']:
                        all_dzialalnosc.append({
                            'Numer KRS': data['numer_krs'],
                            'Nazwa Firmy': data['nazwa_firmy'],
                            'L.p.': dzialalnosc.get('lp', ''),
                            'Typ': dzialalnosc.get('typ', ''),
                            'Zawartość': dzialalnosc.get('content', ''),
                            'Nr Wpisu': dzialalnosc.get('nr_wpisu', '')
                        })
                    
                    # 8. Zmiany
                    for zmiana in data['zestawienie_zmian']:
                        all_zmiany.append({
                            'Numer KRS': data['numer_krs'],
                            'Nazwa Firmy': data['nazwa_firmy'],
                            'Nr Wpisu': zmiana.get('nr_wpisu', ''),
                            'Data': zmiana.get('data', ''),
                            'Opis': zmiana.get('opis', ''),
                            'Sygnatura Akt': zmiana.get('sygnatura', ''),
                            'Sąd': zmiana.get('sad', '')
                        })
                    
                    self.update_status(f"Przetworzono: {Path(pdf_path).name} ({idx+1}/{total_files})", "blue")
                    
                except Exception as e:
                    self.update_status(f"Błąd przy {Path(pdf_path).name}: {str(e)}", "red")
            
            # Zapis do CSV
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if all_podmioty:
                pd.DataFrame(all_podmioty).to_csv(os.path.join(self.output_dir, f"podmioty_{timestamp}.csv"), index=False, encoding='utf-8-sig', quoting=csv.QUOTE_ALL)
            if all_adresy:
                pd.DataFrame(all_adresy).to_csv(os.path.join(self.output_dir, f"siedziby_adresy_{timestamp}.csv"), index=False, encoding='utf-8-sig', quoting=csv.QUOTE_ALL)
            if all_wspolnicy:
                pd.DataFrame(all_wspolnicy).to_csv(os.path.join(self.output_dir, f"wspolnicy_akcjonariusze_{timestamp}.csv"), index=False, encoding='utf-8-sig', quoting=csv.QUOTE_ALL)
            if all_organy_repr:
                pd.DataFrame(all_organy_repr).to_csv(os.path.join(self.output_dir, f"organy_reprezentacji_{timestamp}.csv"), index=False, encoding='utf-8-sig', quoting=csv.QUOTE_ALL)
            if all_organy_nadzoru:
                pd.DataFrame(all_organy_nadzoru).to_csv(os.path.join(self.output_dir, f"organy_nadzoru_{timestamp}.csv"), index=False, encoding='utf-8-sig', quoting=csv.QUOTE_ALL)
            if all_prokurenci:
                pd.DataFrame(all_prokurenci).to_csv(os.path.join(self.output_dir, f"prokurenci_{timestamp}.csv"), index=False, encoding='utf-8-sig', quoting=csv.QUOTE_ALL)
            if all_dzialalnosc:
                pd.DataFrame(all_dzialalnosc).to_csv(os.path.join(self.output_dir, f"przedmiot_dzialalnosci_{timestamp}.csv"), index=False, encoding='utf-8-sig', quoting=csv.QUOTE_ALL)
            if all_zmiany:
                pd.DataFrame(all_zmiany).to_csv(os.path.join(self.output_dir, f"zestawienie_zmian_{timestamp}.csv"), index=False, encoding='utf-8-sig', quoting=csv.QUOTE_ALL)
            
            self.progress.stop()
            self.is_processing = False
            
            summary = f"""Konwersja zakończona pomyślnie!

Przetworzono: {len(self.selected_files)} plik(ów)

Utworzone pliki:
• Podmioty: {len(all_podmioty)} rekordów
• Siedziby/Adresy: {len(all_adresy)} rekordów
• Wspólnicy/Akcjonariusze: {len(all_wspolnicy)} rekordów
• Organy Reprezentacji: {len(all_organy_repr)} rekordów
• Organy Nadzoru: {len(all_organy_nadzoru)} rekordów
• Prokurenci: {len(all_prokurenci)} rekordów
• Przedmiot Działalności: {len(all_dzialalnosc)} rekordów
• Zestawienie Zmian: {len(all_zmiany)} rekordów

Folder: {self.output_dir}"""
            
            self.update_status("Konwersja zakończona!", "green")
            messagebox.showinfo("Sukces", summary)
            
        except Exception as e:
            self.progress.stop()
            self.is_processing = False
            self.update_status(f"Błąd: {str(e)}", "red")
            messagebox.showerror("Błąd", f"Błąd podczas konwersji:\n{str(e)}")


def main():
    """Główna funkcja"""
    root = tk.Tk()
    app = KRSConverterGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
