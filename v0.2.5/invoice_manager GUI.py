import tkinter as tk
import tkinter.messagebox
from tkinter import ttk
from tkcalendar import Calendar
import os
from datetime import datetime, timedelta
import csv



class InvoiceManager:
    def __init__(self):
        self.filename = 'faktury.csv'
        self.platnosci = 'platnosci.csv'
        self.numerators_filename = 'numerator.csv'
        self.invoice_number = self._get_last_invoice_number()
        self._check_file_exists()
        self._check_file_exists2()           

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
                writer.writerow(['Numer_faktury', 'Numer_orginalu', 'Kwota', 'Waluta', 'Data_wystawienia',])

    def _check_file_exists2(self):          
        if not os.path.exists(self.platnosci):
            with open(self.platnosci, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter='\t')
                writer.writerow(['Numer_faktury', 'Kwota', 'Data_platnosci',])

    def _update_invoice_number(self):
        with open(self.numerators_filename, 'w', encoding='utf-8') as file:
            file.write(str(self.invoice_number))
    
    def _generate_invoice_number(self):
        current_month_year = datetime.now().strftime("%m/%Y")
        self.invoice_number += 1
        invoice_number = f"{self.invoice_number}/{current_month_year}"
        self._update_invoice_number()
        return invoice_number
    
    def read_invoice_numbers(self):
        invoice_numbers = []
        try:
            with open(self.filename, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile, delimiter='\t')
                for row in reader:
                    invoice_numbers.append(row['Numer_faktury'])
        except FileNotFoundError:
            print(f"Plik {self.filename} nie został znaleziony.")
        except Exception as e:
            print(f"Wystąpił błąd: {e}")
        return invoice_numbers
    
    def add_invoice(self, nr_org, amount, currency,issue_date):

        if not amount or not currency:
            tk.messagebox.showerror("Błąd", "Pola 'Kwota' i 'Waluta' nie mogą być puste")
            return
        invoice_number = self._generate_invoice_number()
        with open(self.filename, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter='\t')
            writer.writerow([invoice_number, nr_org, amount, currency, issue_date])
        tk.messagebox.showinfo("Info", "Faktura dodana pomyślnie")


    def add_payment(self, invoice_number, amount, issue_date):
        if not amount or not invoice_number:
            tk.messagebox.showerror("Błąd", "Pole 'Kwota' i 'Nr faktury' nie może być puste")
            return
        with open(self.platnosci, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter='\t')
            writer.writerow([invoice_number, amount, issue_date])
        tk.messagebox.showinfo("Info", "Płatność dodana pomyślnie")


class InvoiceApp:
    def __init__(self, root):
        self.invoice = InvoiceManager()
        root.title("MenedżerFk")

### SEKCJA DODAJ FAKTURE###
        invoice_list = self.invoice.read_invoice_numbers()
        gui_frame = tk.LabelFrame(root, text="Dodaj Fakturę", padx=10, pady=10)
        gui_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.nr_org_var = tk.StringVar()
        self.amount_var = tk.IntVar()
        self.amount2_var = tk.IntVar()
        self.currency_options = ["USD", "EUR", "PLN"]
        self.currency_var = tk.StringVar()
        self.viewer_options = ["platnosci", "faktury", "bilans"]
        self.viewer_var = tk.StringVar()
        self.invoice_var = tk.StringVar()
        self.tree = None

        tk.Label(gui_frame, text="Numer orginału:").grid(row=0, column=0)
        tk.Entry(gui_frame, textvariable=self.nr_org_var).grid(row=0, column=1)
        
        tk.Label(gui_frame, text="Kwota:").grid(row=1, column=0)
        tk.Entry(gui_frame, textvariable=self.amount_var).grid(row=1, column=1)

        tk.Label(gui_frame, text="Waluta:").grid(row=2, column=0)
        currency_combobox = ttk.Combobox(gui_frame, textvariable=self.currency_var, values=self.currency_options, state="readonly")
        currency_combobox.grid(row=2, column=1)
        currency_combobox.set('')

        tk.Label(gui_frame, text="Data wystawienia:").grid(row=0, column=2)
        self.cal = Calendar(gui_frame, selectmode='day', year=datetime.now().year, month=datetime.now().month, day=datetime.now().day, date_pattern="yyyy-mm-dd")
        self.cal.grid(row=1, column=2, rowspan=15)

        tk.Button(gui_frame, text="Dodaj fakturę", command=self.add_invoice).grid(row=4, column=0, columnspan=2)
    ### KONIEC SIEKCJI ###

### SEKCJA DODAJ PLATNOSC###

        gui_frame = tk.LabelFrame(root, text="Dodaj Platnosc", padx=10, pady=10)
        gui_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        tk.Label(gui_frame, text="Nr faktury:").grid(row=0, column=0)
        invoice_combobox = ttk.Combobox(gui_frame, textvariable=self.invoice_var, values=invoice_list, state="readonly")
        invoice_combobox.grid(row=0, column=1)
        invoice_combobox.set('')

        self.amount2_var = tk.IntVar()

        tk.Label(gui_frame, text="Kwota:").grid(row=1, column=0)
        tk.Entry(gui_frame, textvariable=self.amount2_var).grid(row=1, column=1)


        tk.Label(gui_frame, text="Data płatnośći:").grid(row=0, column=2)
        self.cal2 = Calendar(gui_frame, selectmode='day', year=datetime.now().year, month=datetime.now().month, day=datetime.now().day, date_pattern="yyyy-mm-dd")
        self.cal2.grid(row=1, column=2, rowspan=15)

        tk.Button(gui_frame, text="Dodaj Płatność", command=self.add_payment).grid(row=4, column=0, columnspan=2)
    ### KONIEC SIEKCJI ###       


###Viewer###  
        gui_frame = tk.LabelFrame(root, text="Wybierz podgląd", padx=10, pady=10)
        gui_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        tk.Label(gui_frame, text="Data płatnośći:").grid(row=0, column=0)
        currency_combobox = ttk.Combobox(gui_frame, textvariable=self.viewer_var, values=self.viewer_options, state="readonly")
        currency_combobox.grid(row=0, column=1)
        currency_combobox.set('faktury')
        tk.Button(gui_frame, text="Wybierz", command=self.viewer_csv).grid(row=0, column=2, columnspan=1)
        viewer_frame = tk.LabelFrame(root, text="Paczacz", padx=10, pady=10)
        viewer_frame.grid(padx=10, pady=10, sticky="nsew", columnspan=2)
        self.tree = ttk.Treeview(viewer_frame)
        self.tree.pack(expand=True, fill="both", side="left")
        scrollbar = ttk.Scrollbar(viewer_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
 ###KONIEC###

    def viewer_csv(self):
        with open(self.viewer_var.get()+".csv", newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter='\t')
            headers = next(reader)
            self.tree['columns'] = headers
            self.tree['show'] = 'headings'
            for header in headers:
                self.tree.heading(header, text=header)
            for row in reader:
                self.tree.insert('', 'end', values=row)

    def add_invoice(self):
        amount = self.amount_var.get()
        currency = self.currency_var.get()
        issue_date = self.cal.get_date()
        nr_org = self.nr_org_var.get()
        self.invoice.add_invoice(nr_org, amount, currency, issue_date)

    def add_payment(self):
        invoice_number = self.invoice_var.get()
        amount = self.amount2_var.get()
        payment_date = self.cal2.get_date()
        self.invoice.add_payment(invoice_number, amount, payment_date)


root = tk.Tk()
app = InvoiceApp(root)
root.mainloop()