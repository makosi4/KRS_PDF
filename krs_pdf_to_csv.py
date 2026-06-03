#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KRS PDF to CSV Converter - GUI Version
Aplikacja do konwersji plików PDF z KRS na ustrukturyzowane pliki CSV
Wymaga: pip install PyPDF2 pdfplumber pandas tkinter-filedialog
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
from typing import Dict, List, Optional


class KRSPDFExtractor:
    """Klasa do ekstrakcji danych z plików PDF KRS"""
    
    def __init__(self):
        self.reset_data()
    
    def reset_data(self):
        """Resetuje dane"""
        self.data = {
            'nazwa_firmy': '',
            'numer_krs': '',
            'adres': '',
            'pracownicy': [],
            'kierownictwo': [],
            'prokurenci': [],
            'daty_zmian': [],
            'zakres_działalności': ''
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
            print(f"❌ Błąd podczas czytania PDF: {e}")
            return ""
    
    def extract_krs_number(self, text: str) -> str:
        """Wyciąga numer KRS z tekstu"""
        patterns = [
            r'KRS\s*[:\-]?\s*(\d{10})',
            r'Numer\s+KRS\s*[:\-]?\s*(\d{10})',
            r'(\d{10})(?=\s*KRS)'
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return ""
    
    def extract_company_name(self, text: str) -> str:
        """Wyciąga nazwę firmy"""
        lines = text.split('\n')
        for i, line in enumerate(lines[:30]):
            line = line.strip()
            if len(line) > 5 and not any(skip in line.upper() for skip in ['KRS', 'NUMER', 'TELEFON', 'EMAIL', 'INFORMACJA']):
                if line and line[0].isupper() and not line.startswith('Odpis'):
                    return line
        return ""
    
    def extract_address(self, text: str) -> str:
        """Wyciąga adres siedziby firmy"""
        patterns = [
            r'[Ss]iedziba\s*[:\-]?\s*(.+?)(?=\n|$)',
            r'[Aa]dres\s*[:\-]?\s*(.+?)(?=\n|$)',
            r'ul\.\s+([^\n]+)',
            r'al\.\s+([^\n]+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        return ""
    
    def extract_people_section(self, text: str, section_name: str) -> List[str]:
        """Wyciąga listę osób z danej sekcji"""
        people = []
        
        pattern = rf'{section_name.upper()}.*?(?=\n\n|\n[A-Z]{{2,}}|Zmiana|Skreślenie|$)'
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        
        if match:
            section_text = match.group(0)
            lines = section_text.split('\n')
            for line in lines:
                line = line.strip()
                # Szuka linii zawierających imiona i nazwiska
                if line and len(line) > 3 and not any(skip in line for skip in [':', '---', '###', section_name.upper()]):
                    if re.search(r'^[A-Z][a-ząćęłńóśźż]+(\s+[A-Z][a-ząćęłńóśźż]+)+', line):
                        people.append(line)
        
        return people
    
    def extract_activity_scope(self, text: str) -> str:
        """Wyciąga zakres działalności (sekcja PKD)"""
        patterns = [
            r'[Pp]rzedmiot\s+[Dd]ziałalności.*?(?=\n\n|\n[A-Z]{2})',
            r'PKD.*?(?=\n\n|\n[A-Z]{2})',
            r'[Dd]ziałalność.*?(?=\n\n|\n[A-Z]{2})'
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                return match.group(0).strip()
        return ""
    
    def extract_change_dates(self, text: str) -> List[str]:
        """Wyciąga daty zmian wpisów"""
        date_pattern = r'\d{1,2}[-./]\d{1,2}[-./]\d{4}'
        matches = re.findall(date_pattern, text)
        dates = sorted(set(matches), reverse=True)
        return dates
    
    def extract_all_data(self, pdf_path: str) -> Dict:
        """Główna metoda ekstrakcji wszystkich danych"""
        self.reset_data()
        text = self.extract_text_from_pdf(pdf_path)
        
        if not text:
            return self.data
        
        self.data['numer_krs'] = self.extract_krs_number(text)
        self.data['nazwa_firmy'] = self.extract_company_name(text)
        self.data['adres'] = self.extract_address(text)
        self.data['pracownicy'] = self.extract_people_section(text, 'pracownik')
        self.data['kierownictwo'] = self.extract_people_section(text, 'kierownik')
        self.data['prokurenci'] = self.extract_people_section(text, 'prokurent')
        self.data['daty_zmian'] = self.extract_change_dates(text)
        self.data['zakres_działalności'] = self.extract_activity_scope(text)
        
        return self.data


class KRSConverterGUI:
    """Główna klasa aplikacji GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("KRS PDF to CSV Converter")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # Zmienne
        self.selected_files = []
        self.extractor = KRSPDFExtractor()
        self.output_dir = None
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
        
        # Frame główny
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Tytuł
        title_label = ttk.Label(
            main_frame,
            text="KRS PDF to CSV Converter",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Separator
        separator = ttk.Separator(main_frame, orient="horizontal")
        separator.grid(row=1, column=0, columnspan=2, sticky="ew", pady=10)
        
        # Przycisk wyboru plików
        select_button = ttk.Button(
            main_frame,
            text="📁 Wybierz pliki PDF",
            command=self.select_files
        )
        select_button.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)
        
        # Rama z listą plików
        list_frame = ttk.LabelFrame(main_frame, text="Wybrane pliki PDF", padding="10")
        list_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Listbox
        self.file_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            height=10
        )
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_listbox.yview)
        
        # Przycisk usuwania pliku
        remove_button = ttk.Button(
            main_frame,
            text="🗑️ Usuń zaznaczony plik",
            command=self.remove_selected_file
        )
        remove_button.grid(row=4, column=0, columnspan=2, sticky="ew", pady=5)
        
        # Separator
        separator2 = ttk.Separator(main_frame, orient="horizontal")
        separator2.grid(row=5, column=0, columnspan=2, sticky="ew", pady=10)
        
        # Przycisk wyboru folderu wyjścia
        output_button = ttk.Button(
            main_frame,
            text="📂 Wybierz folder do zapisu",
            command=self.select_output_dir
        )
        output_button.grid(row=6, column=0, columnspan=2, sticky="ew", pady=5)
        
        # Label z folderem wyjścia
        self.output_label = ttk.Label(
            main_frame,
            text="Folder: Pulpit",
            foreground="blue"
        )
        self.output_label.grid(row=7, column=0, columnspan=2, sticky="ew", pady=5)
        self.output_dir = str(Path.home() / "Desktop")
        
        # Separator
        separator3 = ttk.Separator(main_frame, orient="horizontal")
        separator3.grid(row=8, column=0, columnspan=2, sticky="ew", pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            main_frame,
            mode="indeterminate"
        )
        self.progress.grid(row=9, column=0, columnspan=2, sticky="ew", pady=5)
        
        # Status label
        self.status_label = ttk.Label(
            main_frame,
            text="Gotowy do pracy",
            foreground="green"
        )
        self.status_label.grid(row=10, column=0, columnspan=2, sticky="ew", pady=5)
        
        # Frame na przyciski
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=11, column=0, columnspan=2, sticky="ew", pady=10)
        
        # Przycisk konwersji
        convert_button = ttk.Button(
            button_frame,
            text="✅ Konwertuj do CSV",
            command=self.start_conversion
        )
        convert_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Przycisk wyjścia
        exit_button = ttk.Button(
            button_frame,
            text="❌ Wyjście",
            command=self.root.quit
        )
        exit_button.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
    
    def select_files(self):
        """Otwiera dialog wyboru plików"""
        files = filedialog.askopenfilenames(
            title="Wybierz pliki PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if files:
            self.selected_files.extend(files)
            self.update_file_list()
            self.update_status(f"Wybrano {len(self.selected_files)} plik(ów)", "blue")
    
    def remove_selected_file(self):
        """Usuwa zaznaczony plik z listy"""
        selection = self.file_listbox.curselection()
        if selection:
            index = selection[0]
            self.selected_files.pop(index)
            self.update_file_list()
            self.update_status(f"Pozostało {len(self.selected_files)} plik(ów)", "blue")
    
    def update_file_list(self):
        """Aktualizuje listę wybranych plików"""
        self.file_listbox.delete(0, tk.END)
        for file in self.selected_files:
            self.file_listbox.insert(tk.END, Path(file).name)
    
    def select_output_dir(self):
        """Otwiera dialog wyboru folderu"""
        folder = filedialog.askdirectory(title="Wybierz folder do zapisu plików CSV")
        if folder:
            self.output_dir = folder
            # Wyświetla skróconą ścieżkę
            display_path = folder if len(folder) < 40 else "..." + folder[-37:]
            self.output_label.config(text=f"Folder: {display_path}")
    
    def update_status(self, message: str, color: str = "black"):
        """Aktualizuje status"""
        self.status_label.config(text=message, foreground=color)
        self.root.update()
    
    def start_conversion(self):
        """Uruchamia konwersję w osobnym wątku"""
        if not self.selected_files:
            messagebox.showwarning("Błąd", "Nie wybrano żadnych plików!")
            return
        
        if not self.output_dir:
            messagebox.showwarning("Błąd", "Nie wybrano folderu do zapisu!")
            return
        
        if self.is_processing:
            messagebox.showwarning("Ostrzeżenie", "Konwersja już trwa!")
            return
        
        # Uruchamia konwersję w osobnym wątku
        thread = threading.Thread(target=self.convert_files)
        thread.start()
    
    def convert_files(self):
        """Główna metoda konwersji"""
        self.is_processing = True
        self.progress.start()
        self.update_status("Przetwarzam pliki...", "orange")
        
        try:
            # Kolekcje danych
            all_firms = []
            all_employees = []
            all_management = []
            all_attorneys = []
            all_activities = []
            all_dates = []
            
            total_files = len(self.selected_files)
            
            # Przetwarzanie każdego pliku
            for idx, pdf_path in enumerate(self.selected_files):
                try:
                    data = self.extractor.extract_all_data(pdf_path)
                    
                    # Zbieranie danych do firm
                    firm_record = {
                        'Nazwa Firmy': data['nazwa_firmy'],
                        'Numer KRS': data['numer_krs'],
                        'Adres': data['adres'],
                        'Zakres Działalności': data['zakres_działalności']
                    }
                    all_firms.append(firm_record)
                    
                    # Zbieranie pracowników
                    for pracownik in data['pracownicy']:
                        all_employees.append({
                            'Numer KRS': data['numer_krs'],
                            'Nazwa Firmy': data['nazwa_firmy'],
                            'Pracownik': pracownik
                        })
                    
                    # Zbieranie kierownictwa
                    for kierownik in data['kierownictwo']:
                        all_management.append({
                            'Numer KRS': data['numer_krs'],
                            'Nazwa Firmy': data['nazwa_firmy'],
                            'Kierownik': kierownik
                        })
                    
                    # Zbieranie prokurów
                    for prokurent in data['prokurenci']:
                        all_attorneys.append({
                            'Numer KRS': data['numer_krs'],
                            'Nazwa Firmy': data['nazwa_firmy'],
                            'Prokurent': prokurent
                        })
                    
                    # Zbieranie dat zmian
                    for data_zmian in data['daty_zmian']:
                        all_dates.append({
                            'Numer KRS': data['numer_krs'],
                            'Nazwa Firmy': data['nazwa_firmy'],
                            'Data Zmian': data_zmian
                        })
                    
                    # Zbieranie zakresu działalności
                    if data['zakres_działalności']:
                        all_activities.append({
                            'Numer KRS': data['numer_krs'],
                            'Nazwa Firmy': data['nazwa_firmy'],
                            'Zakres Działalności': data['zakres_działalności']
                        })
                    
                    self.update_status(f"Przetworzono: {Path(pdf_path).name} ({idx+1}/{total_files})", "blue")
                    
                except Exception as e:
                    self.update_status(f"Błąd przy {Path(pdf_path).name}: {str(e)}", "red")
            
            # Zapis do CSV
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 1. Firmy
            if all_firms:
                df_firms = pd.DataFrame(all_firms)
                firms_file = os.path.join(self.output_dir, f"firmy_{timestamp}.csv")
                df_firms.to_csv(firms_file, index=False, encoding='utf-8-sig', quoting=csv.QUOTE_ALL)
            
            # 2. Pracownicy
            if all_employees:
                df_employees = pd.DataFrame(all_employees)
                employees_file = os.path.join(self.output_dir, f"pracownicy_{timestamp}.csv")
                df_employees.to_csv(employees_file, index=False, encoding='utf-8-sig', quoting=csv.QUOTE_ALL)
            
            # 3. Kierownictwo
            if all_management:
                df_management = pd.DataFrame(all_management)
                management_file = os.path.join(self.output_dir, f"kierownictwo_{timestamp}.csv")
                df_management.to_csv(management_file, index=False, encoding='utf-8-sig', quoting=csv.QUOTE_ALL)
            
            # 4. Prokurenci
            if all_attorneys:
                df_attorneys = pd.DataFrame(all_attorneys)
                attorneys_file = os.path.join(self.output_dir, f"prokurenci_{timestamp}.csv")
                df_attorneys.to_csv(attorneys_file, index=False, encoding='utf-8-sig', quoting=csv.QUOTE_ALL)
            
            # 5. Daty zmian
            if all_dates:
                df_dates = pd.DataFrame(all_dates)
                dates_file = os.path.join(self.output_dir, f"daty_zmian_{timestamp}.csv")
                df_dates.to_csv(dates_file, index=False, encoding='utf-8-sig', quoting=csv.QUOTE_ALL)
            
            # 6. Zakresy działalności
            if all_activities:
                df_activities = pd.DataFrame(all_activities)
                activities_file = os.path.join(self.output_dir, f"zakresy_dzialalnosci_{timestamp}.csv")
                df_activities.to_csv(activities_file, index=False, encoding='utf-8-sig', quoting=csv.QUOTE_ALL)
            
            self.progress.stop()
            self.is_processing = False
            
            summary = f"""✅ Konwersja zakończona pomyślnie!

Przetworzono: {len(self.selected_files)} plik(ów)

Utworzone pliki:
• Firmy: {len(all_firms)} rekordów
• Pracownicy: {len(all_employees)} rekordów
• Kierownictwo: {len(all_management)} rekordów
• Prokurenci: {len(all_attorneys)} rekordów
• Daty zmian: {len(all_dates)} rekordów
• Zakresy działalności: {len(all_activities)} rekordów

Folder: {self.output_dir}"""
            
            self.update_status("✅ Konwersja zakończona!", "green")
            messagebox.showinfo("Sukces", summary)
            
        except Exception as e:
            self.progress.stop()
            self.is_processing = False
            self.update_status(f"❌ Błąd: {str(e)}", "red")
            messagebox.showerror("Błąd", f"Błąd podczas konwersji:\n{str(e)}")


def main():
    """Główna funkcja"""
    root = tk.Tk()
    app = KRSConverterGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
