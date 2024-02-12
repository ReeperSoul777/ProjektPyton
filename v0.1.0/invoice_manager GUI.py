import tkinter as tk
import tkinter.messagebox
from tkinter import ttk
from tkcalendar import Calendar
import os
from datetime import datetime, timedelta
import csv

class InvoiceManager:
    def __init__(self, filename, numerators_filename):
        self.filename = filename
        self.numerators_filename = numerators_filename
        self.invoice_number = self._get_last_invoice_number()
        self._check_file_exists()
            

    def _get_last_invoice_number(self):
        if os.path.exists(self.numerators_filename):
            with open(self.numerators_filename, 'r', encoding='utf-8') as file:
                last_number = file.read().strip()
                return int(last_number) if last_number else 0
        return 0

    def _check_file_exists(self):
        if not os.path.exists(self.filename):
            with open(self.filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter='\t')
                writer.writerow(['Numer_faktury', 'Numer_orginalu', 'Kwota', 'Waluta', 'Data_wystawienia', 'Termin', 'Data_platnosci'])

    def _update_invoice_number(self):
        with open(self.numerators_filename, 'w', encoding='utf-8') as file:
            file.write(str(self.invoice_number))
    
    def _generate_invoice_number(self):
        current_month_year = datetime.now().strftime("%m-%Y")
        self.invoice_number += 1
        invoice_number = f"{self.invoice_number}/{current_month_year}"
        self._update_invoice_number()
        return invoice_number
    
    def add_invoice(self, Numer_orginalu, amount, currency, issue_date, termin, ):
        invoice_number = self._generate_invoice_number()
        with open(self.filename, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter='\t')
            writer.writerow([invoice_number, Numer_orginalu, amount, currency, issue_date, termin])

class PaymentManager:
    def __init__(self, filename):
        self.filename = filename
        self._check_file_exists()

    def _check_file_exists(self):
        """Sprawdza, czy plik istnieje, a jeśli nie - tworzy go z odpowiednimi nagłówkami."""
        if not os.path.exists(self.filename):
            with open(self.filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter='\t')
                writer.writerow(['Numer_faktury', 'Kwota', 'Waluta', 'Data_wpłaty'])

    def add_payment(self, invoice_number, amount, currency, payment_date):
        """Dodaje płatność do pliku CSV."""
        with open(self.filename, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter='\t')
            writer.writerow([invoice_number, amount, currency, payment_date])

class InvoiceApp:
    def __init__(self, root):
        self.manager = InvoiceManager("faktury.csv", "numerator.csv")
        root.title("MenedżerFk")

        ### SEKCJA DODAJ FAKTURE###
        add_invoice_frame = tk.LabelFrame(root, text="Dodaj Fakturę", padx=10, pady=10)
        add_invoice_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.nr_org_var = tk.StringVar()
        self.amount_var = tk.IntVar()
        self.currency_var = tk.StringVar()
        self.termin_var = tk.IntVar()

        tk.Label(add_invoice_frame, text="Numer orginału:").grid(row=0, column=0)
        tk.Entry(add_invoice_frame, textvariable=self.nr_org_var).grid(row=0, column=1)
        
        tk.Label(add_invoice_frame, text="Kwota:").grid(row=1, column=0)
        tk.Entry(add_invoice_frame, textvariable=self.amount_var).grid(row=1, column=1)

        tk.Label(add_invoice_frame, text="Waluta:").grid(row=2, column=0)
        tk.Entry(add_invoice_frame, textvariable=self.currency_var).grid(row=2, column=1)

        tk.Label(add_invoice_frame, text="Termin płatności (dni):").grid(row=3, column=0)
        tk.Entry(add_invoice_frame, textvariable=self.termin_var).grid(row=3, column=1)

        tk.Label(add_invoice_frame, text="Data wystawienia:").grid(row=0, column=2)
        self.cal = Calendar(add_invoice_frame, selectmode='day', year=datetime.now().year, month=datetime.now().month, day=datetime.now().day, date_pattern="yyyy-mm-dd")
        self.cal.grid(row=1, column=2, rowspan=15)

        tk.Button(add_invoice_frame, text="Dodaj fakturę", command=self.add_invoice).grid(row=4, column=0)
        ### KONIEC SIEKCJI ###

    def add_invoice(self):
        amount = self.amount_var.get()
        currency = self.currency_var.get()
        issue_date = self.cal.get_date()
        Numer_orginalu = self.nr_org_var.get()
        termin = self.termin_var.get()

        if not amount or not currency:
            tk.messagebox.showerror("Błąd", "Pola 'Kwota' i 'Waluta' nie mogą być puste")
            return
           
        self.manager.add_invoice( Numer_orginalu, amount, currency, issue_date, termin)
        tk.messagebox.showinfo("Info", "Faktura dodana pomyślnie")

root = tk.Tk()
app = InvoiceApp(root)
root.mainloop()