import tkinter as tk
import tkinter.messagebox
from tkinter import ttk
from tkcalendar import Calendar
import os
from datetime import datetime, timedelta
import csv
import requests



class InvoiceManager:
    def __init__(self):
        self.filename = 'faktury.csv'
        self.platnosci = 'platnosci.csv'
        self.bilans = 'bilans.csv'
        self.numerators_filename = 'numerator.csv'
        self.invoice_number = self._get_last_invoice_number()
        self._check_file_exists()
        self._check_file_exists2()           
        self._check_file_exists3() 
        self._rozlicz_platnosci_1()

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

    def _check_file_exists3(self):          
        if not os.path.exists(self.bilans):
            with open(self.bilans, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter='\t')
                writer.writerow(['Numer_faktury','Kwota','waluta','zapłacono','pozostalo','Data_platnosci','roznica_kursowa'])

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

    def pobierz_kurs_waluty(self, kod_waluty, data, prob=5):
        if kod_waluty == 'PLN':
            return None 
        if prob == 0:
            print("Nie udało się pobrać kursu waluty po 5 próbach.")
            return None
        url = f"http://api.nbp.pl/api/exchangerates/rates/A/{kod_waluty}/{data}/?format=json"
        try:
            response = requests.get(url)
            response.raise_for_status()  # Sprawdza, czy zapytanie zostało pomyślnie obsłużone
            data = response.json()
            kurs_waluty = data['rates'][0]['mid']
            return kurs_waluty
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"Nie znaleziono danych {kod_waluty} dla daty: {data}, próba z poprzednim dniem. (Pozostało prób {prob})")
                nowa_data = datetime.strptime(data, "%Y-%m-%d") - timedelta(days=1)
                nowa_data_str = nowa_data.strftime("%Y-%m-%d")
                return self.pobierz_kurs_waluty(kod_waluty, nowa_data_str, prob-1)
            else:
                print(f"Błąd zapytania: {e}")
        except requests.exceptions.RequestException as e:
            print(f"Błąd połączenia: {e}")
        return None


    def _rozlicz_platnosci_1(self):
        faktury = {}
    # Krok 1: Wczytanie danych o fakturach
        with open('faktury.csv', 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter='\t')
            for row in reader:
                faktury[row['Numer_faktury']] = {
                'kwota': float(row['Kwota']), 
                'waluta': row['Waluta'], 
                'zaplacono': 0, 
                'pozostalo': float(row['Kwota']), 
                'data_faktury': row['Data_wystawienia'],
                'data_platnosci': None,
                'roznica_kursowa': None
            }
            self._rozlicz_platnosci_2(faktury)
                         
    def _rozlicz_platnosci_2(self, faktury):
        with open('platnosci.csv', 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter='\t')
            for row in reader:
                nr_faktury = row['Numer_faktury']
                if nr_faktury in faktury:
                    kwota_platnosci = float(row['Kwota'])
                    faktura = faktury[nr_faktury]
                    faktura['zaplacono'] += kwota_platnosci
                    faktura['pozostalo'] -= kwota_platnosci
                    data_platnosci = datetime.strptime(row['Data_platnosci'], "%Y-%m-%d")
                if faktura['data_platnosci'] is None or data_platnosci > faktura['data_platnosci']:
                    faktura['data_platnosci'] = data_platnosci

                kurs_wystawienia = self.pobierz_kurs_waluty(faktura['waluta'], faktura['data_faktury'])
                kurs_platnosci = self.pobierz_kurs_waluty(faktura['waluta'], row['Data_platnosci'])

                if kurs_wystawienia and kurs_platnosci:
                    faktura['roznica_kursowa'] = kurs_wystawienia - kurs_platnosci
                else:
                    faktura['roznica_kursowa'] = None

            self._rozlicz_platnosci_3(faktury)

    def _rozlicz_platnosci_3(self,faktury):
        with open('bilans.csv', 'w', newline='', encoding='utf-8') as file:
            fieldnames = ['Numer_faktury', 'Kwota', 'Waluta', 'Zaplacono', 'Pozostalo', 'Data_platnosci','roznica_kursowa']
            writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter='\t')
            writer.writeheader()
            for nr_faktury, dane in faktury.items():
                roznica_kursowa_formatowane = "{:.4f}".format(dane['roznica_kursowa']) if dane['roznica_kursowa'] is not None else 'Brak danych'
                #print(dane['roznica_kursowa'],"dane")
               # print(roznica_kursowa_formatowane,"roznica")
                writer.writerow({
                'Numer_faktury': nr_faktury,
                'Kwota': dane['kwota'],
                'Waluta': dane['waluta'],
                'Zaplacono': dane['zaplacono'],
                'Pozostalo': dane['pozostalo'],
                'Data_platnosci': dane['data_platnosci'].strftime("%Y-%m-%d") if dane['data_platnosci'] else 'Brak płatności',
                'roznica_kursowa': roznica_kursowa_formatowane
            })

        
class InvoiceApp:

    def __init__(self, root):
        self.invoice = InvoiceManager()
        root.title("MenedżerFk")

### zmienne i pomocnicze ###
        invoice_list = self.invoice.read_invoice_numbers()
        self.nr_org_var = tk.StringVar()
        self.amount_var = tk.IntVar()
        self.amount2_var = tk.IntVar()
        self.currency_options = ["USD", "EUR", "PLN"]
        self.currency_var = tk.StringVar()
        self.viewer_options = ["platnosci", "faktury", "bilans"]
        self.viewer_var = tk.StringVar()
        self.invoice_var = tk.StringVar()
        self.tree = None

### SEKCJA DODAJ FAKTURE###
        gui_frame = tk.LabelFrame(root, text="Dodaj Fakturę", padx=10, pady=10)
        gui_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

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
        self.invoice_combobox = ttk.Combobox(gui_frame, textvariable=self.invoice_var, values=invoice_list, state="readonly", name="invoice_combobox")
        self.invoice_combobox.grid(row=0, column=1)
        self.invoice_combobox.set('')

        self.amount2_var = tk.IntVar()

        tk.Label(gui_frame, text="Kwota:").grid(row=1, column=0)
        tk.Entry(gui_frame, textvariable=self.amount2_var).grid(row=1, column=1)


        tk.Label(gui_frame, text="Data płatnośći:").grid(row=0, column=2)
        self.cal2 = Calendar(gui_frame, selectmode='day', year=datetime.now().year, month=datetime.now().month, day=datetime.now().day, date_pattern="yyyy-mm-dd")
        self.cal2.grid(row=1, column=2, rowspan=15)

        tk.Button(gui_frame, text="Dodaj Płatność", command=self.add_payment).grid(row=4, column=0, columnspan=2)
### KONIEC SIEKCJI ###       


###Viewer###  
    ###Wybieracz
        gui_frame = tk.LabelFrame(root, text="Wybierz podgląd", padx=10, pady=10)
        gui_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        currency_combobox = ttk.Combobox(gui_frame, textvariable=self.viewer_var, values=self.viewer_options, state="readonly")
        currency_combobox.grid(row=0, column=1)
        currency_combobox.set('faktury')
        tk.Button(gui_frame, text="Wybierz", command=self.viewer_csv).grid(row=0, column=2, columnspan=1)
    ###AKCJE
        gui_frame = tk.LabelFrame(root, text="AKCJE", padx=10, pady=10)
        gui_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        tk.Button(gui_frame, text="Odświerz bilans", command=self.ref_bil).grid(row=0, column=0, columnspan=1)
        tk.Button(gui_frame, text="Odświerz NrFaktur", command=self.ref_inv).grid(row=0, column=1, columnspan=1)

    ###OKNO
        viewer_frame = tk.LabelFrame(root, text="Paczacz", padx=10, pady=10)
        viewer_frame.grid(padx=10, pady=10, sticky="nsew", columnspan=2)
        self.tree = ttk.Treeview(viewer_frame)
        self.tree.pack(expand=True, fill="both", side="left")
        scrollbar = ttk.Scrollbar(viewer_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
###KONIEC###


###Funkcje###
    def viewer_csv(self):
        self.tree.delete(*self.tree.get_children())
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

    def ref_bil(self):
        self.invoice._rozlicz_platnosci_1()

    def ref_inv(self):
        invoice_list = self.invoice.read_invoice_numbers()
        self.invoice_combobox['values'] = invoice_list
        self.invoice_combobox.set('')

    def kurs(self):
        currency = self.currency_var.get()
        issue_date = self.cal.get_date()
        self.invoice.pobierz_kurs_waluty(currency, issue_date)


root = tk.Tk()
app = InvoiceApp(root)
root.mainloop()