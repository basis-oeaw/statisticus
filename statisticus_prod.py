###############################################/#################################/
# Statisticus v2.0 – Eingabe + Analyzer - Vers.18/11/25
################################################################################




from tkinter import *
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

DB_NAME = "statisticus.db"

# ---------------------------------------------------------------------------
# DB vorbereiten
# ---------------------------------------------------------------------------
with sqlite3.connect(DB_NAME) as conn:
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Statistik (
            entry_number INTEGER PRIMARY KEY AUTOINCREMENT,
            today TEXT,
            valueb INTEGER,
            valueks INTEGER,
            valuea INTEGER,
            valuev INTEGER
        )
    """)

# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------
def insert_data(zb=None, zks=None, za=None, zv=None):
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO Statistik (today, valueb, valueks, valuea, valuev)
            VALUES (CURRENT_TIMESTAMP, ?, ?, ?, ?)
        """, (zb, zks, za, zv))
        conn.commit()

def get_total_year(column):
    year = datetime.now().year
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute(f"""
            SELECT TOTAL({column})
            FROM Statistik
            WHERE strftime('%Y', today) = ?
        """, (str(year),))
        result = cur.fetchone()[0]
        return int(result or 0)

def validate_int(value):
    if value == "":
        return None
    try:
        return int(value)
    except ValueError:
        messagebox.showerror("Fehler", "Bitte eine ganze Zahl eingeben.")
        return None

def update_counters():
    labelzaehlerb.config(text=str(get_total_year("valueb")))
    labelzaehlerks.config(text=str(get_total_year("valueks")))
    labelzaehlera.config(text=str(get_total_year("valuea")))
    labelzaehlerv.config(text=str(get_total_year("valuev")))


# ---------------------------------------------------------------------------
# Eingabefunktionen
# ---------------------------------------------------------------------------
def speichern():
    def to_int_strict(value, field_name):
        value = value.strip()

        # Leeres Feld → 0 speichern
        if value == "":
            return 0

        # Prüfen, ob nur Ziffern eingegeben wurden (keine Kommas, keine Punkte)
        if not value.isdigit():
            messagebox.showerror("Fehler",
                                 f"Ungültige Eingabe im Feld '{field_name}'.\nBitte nur ganze Zahlen eingeben.")
            raise ValueError("Ungültige Eingabe")

        return int(value)

    try:
        zb = to_int_strict(benutzeranzahl.get(), "BenutzerInnen")
        zks = to_int_strict(kopie_scan.get(), "Kopie/Scan")
        za = to_int_strict(anfrage.get(), "Anfrage")
        zv = to_int_strict(visitor.get(), "BesucherInnen")

    except ValueError:
        return  # NICHT speichern bei Fehler

    insert_data(zb, zks, za, zv)
    update_counters()

    # Felder leeren
    benutzeranzahl.delete(0, END)
    kopie_scan.delete(0, END)
    anfrage.delete(0, END)
    visitor.delete(0, END)


# ---------------------------------------------------------------------------
# Analyzer-Fenster
# ---------------------------------------------------------------------------
def open_analyzer():
    analyzer = Toplevel(fenster)
    analyzer.title("Statisticus Analyse – StAn v2.0")
    analyzer.geometry("390x500")

    try:
        analyzer.tk.call("set_theme", fenster.tk.call("ttk::style", "theme", "use"))
    except Exception:
        pass
    
    # --- Neuer Rahmen für Von/Bis nebeneinander ---
    time_frame = Frame(analyzer)
    time_frame.grid(row=1, column=0, padx=50, pady=(5, 15), sticky=W)

# Von
    Label(time_frame, text="Von").grid(row=0, column=0, sticky=W, padx=(0,5), pady=(40, 60))
    start_date = DateEntry(time_frame, date_pattern="yyyy-mm-dd")
    start_date.grid(row=0, column=1, sticky=W)

# Bis
    Label(time_frame, text="Bis").grid(row=0, column=2, sticky=W, padx=(20,5), pady=(40, 60))
    end_date = DateEntry(time_frame, date_pattern="yyyy-mm-dd")
    end_date.grid(row=0, column=3, sticky=W)

    Label(analyzer, text="Wert:", font=("Arial", 11)).grid(
    row=5, column=0, padx=50, pady=(10, 5), sticky=W)

    # --- Frame für 2×2 Checkbox-Layout ---
    werte_frame = Frame(analyzer)
    werte_frame.grid(row=6, column=0, padx=50, pady=(5, 10), sticky=W)

    var_b = IntVar()
    var_a = IntVar()
    var_k = IntVar()
    var_v = IntVar()

    # Erste Zeile
    ttk.Checkbutton(werte_frame, text="BenutzerIn", variable=var_b)\
        .grid(row=0, column=0, sticky=W, padx=(40, 40))
    ttk.Checkbutton(werte_frame, text="Anfrage", variable=var_a)\
        .grid(row=0, column=1, sticky=W)

    # Zweite Zeile
    ttk.Checkbutton(werte_frame, text="Kopie/Scan", variable=var_k)\
        .grid(row=1, column=0, sticky=W, padx=(40, 40), pady=(5,0))
    ttk.Checkbutton(werte_frame, text="BesucherIn", variable=var_v)\
        .grid(row=1, column=1, sticky=W, pady=(5,0))

    # --- Abfrage-Button unten zentriert ---
    button_frame = Frame(analyzer)
    button_frame.grid(row=20, column=0, columnspan=3, pady=(60, 20), sticky="ew")

    button_frame.grid_columnconfigure(0, weight=1)
    
    # Focus auf das neue Fenster
    analyzer.focus_set()

        
    def run_query():
        if not any((var_b.get(), var_a.get(), var_k.get(), var_v.get())):
            
            messagebox.showerror("Fehler", "Bitte mindestens einen Wert auswählen!")
            return

        # Datumswerte sichern, bevor Analyzer geschlossen wird
        date_from_val = start_date.get_date()
        date_to_val = end_date.get_date()
        dt_to_val = f"{date_to_val} 23:59:59"

        # Analyzer schließen
        analyzer.destroy()

        # Ergebnisfenster öffnen
        result = Toplevel(fenster)
        result.title("Ergebnis")
        result.geometry("390x500")
        result.focus_set()

        # Daten aus DB abrufen
        with sqlite3.connect(DB_NAME) as conn:
            cur = conn.cursor()
            def get_value(column, date_from, date_to):
                cur.execute(f"""
                    SELECT TOTAL({column})
                    FROM Statistik
                    WHERE today BETWEEN ? AND ?
                """, (str(date_from), f"{date_to} 23:59:59"))
                return int(cur.fetchone()[0] or 0)

                # Frame für Ergebnis-Labels
            result_frame = Frame(result)
            result_frame.pack(pady=(30, 30))

            # Ergebnis-Labels dynamisch einfügen
            if var_b.get():
                Label(result_frame, text=f"BenutzerInnen: {get_value('valueb', date_from_val, date_to_val)}")\
                    .pack(anchor=W, padx=30, pady=5)
            if var_a.get():
                Label(result_frame, text=f"Anfragen: {get_value('valuea', date_from_val, date_to_val)}")\
                    .pack(anchor=W, padx=30, pady=5)
            if var_k.get():
                Label(result_frame, text=f"Kopien/Scans: {get_value('valueks', date_from_val, date_to_val)}")\
                    .pack(anchor=W, padx=30, pady=5)
            if var_v.get():
                Label(result_frame, text=f"BesucherInnen: {get_value('valuev', date_from_val, date_to_val)}")\
                    .pack(anchor=W, padx=30, pady=5)

        # --- Funktion zum Plotten ---
        def plot_view():
            verbindung = sqlite3.connect(DB_NAME)
            df = pd.read_sql_query(
                "SELECT * from Statistik WHERE today BETWEEN ? AND ?",
                verbindung, params=(str(date_from_val), f"{date_to_val} 23:59:59")
            )

            if df.empty:
                messagebox.showinfo("Info", "Keine Daten im gewählten Zeitraum.")
                verbindung.close()
                return

            # UTC → lokale Zeit
            d = pd.to_datetime(df['today'])
            local = d.dt.tz_localize("UTC").dt.tz_convert('Europe/Vienna').dt.tz_localize(None)
            df['localtime'] = local.astype(str)
            df['time'] = df['localtime'].str[-8:]
            df['date'] = df['localtime'].str[:10]

            # Spalten umbenennen
            df = df.rename(columns={
                "date": "Datum",
                "valueb": "BenutzerIn",
                "valueks": "Kopie/Scan",
                "valuea": "Anfrage",
                "valuev": "BesucherIn",
                "time": "Uhrzeit"
            })

            df = df.set_index('Uhrzeit').sort_index()
            for col in ["BenutzerIn", "Kopie/Scan", "Anfrage", "BesucherIn"]:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

            # Plot je nach Auswahl
            if var_b.get() == 1:
                df[['BenutzerIn']].plot(color='blue', title=f"{date_from_val} bis {date_to_val}")
                plt.ylim(bottom=0)
            if var_a.get() == 1:
                df[['Anfrage']].plot(color='red', title=f"{date_from_val} bis {date_to_val}")
            if var_k.get() == 1:
                df[['Kopie/Scan']].plot(color='orange', title=f"{date_from_val} bis {date_to_val}")
            if var_v.get() == 1:
                df[['BesucherIn']].plot(color='green', title=f"{date_from_val} bis {date_to_val}")

            plt.show()
            verbindung.close()

        # --- Funktion zum Excel-Export ---
        def export_excel():
            with sqlite3.connect(DB_NAME) as conn:
                df = pd.read_sql_query(
                    "SELECT * FROM Statistik WHERE today BETWEEN ? AND ?",
                    conn, params=(str(date_from_val), f"{date_to_val} 23:59:59")
                )

            if df.empty:
                messagebox.showinfo("Info", "Keine Daten zum Exportieren.")
                return

            # Lokale Zeit
            d = pd.to_datetime(df['today'])
            local = d.dt.tz_localize("UTC").dt.tz_convert('Europe/Vienna').dt.tz_localize(None)
            df['localtime'] = local.astype(str)

            # Spalten umbenennen
            df = df.rename(columns={
                "today": "utc-timestamp",
                "valueb": "BenutzerIn",
                "valueks": "Kopie/Scan",
                "valuea": "Anfrage",
                "valuev": "BesucherIn",
                "localtime": "Datum"
            })

            df = df.drop(columns=["utc-timestamp"])

            path = os.path.join(os.getcwd(), "statisticus_export.xlsx")

            try:
                df.to_excel(path, index=False)
            except PermissionError:
                messagebox.showerror(
                    "Fehler",
                    "Die Excel-Datei ist bereits geöffnet.\nBitte schließen Sie sie und versuchen Sie es erneut."
                )
                return

            try:
                os.startfile(path)
            except Exception:
                messagebox.showinfo("Export", f"Excel-Datei gespeichert unter:\n{path}")

        # Buttons für Plot und Excel
        
        ttk.Button(result, text="Excel-Export", style="Accent.TButton", command=export_excel)\
            .pack(pady=(60, 20))
        ttk.Button(result, text="Diagramme ansehen", style="Accent.TButton", command=plot_view)\
            .pack(pady=20)
        

        
    ttk.Button(button_frame, text="Abfrage starten", style="Accent.TButton", command=run_query).grid(row=0, column=0)
    
       


# ---------------------------------------------------------------------------
# Hauptfenster – Eingabetool
# ---------------------------------------------------------------------------
fenster = Tk()
fenster.geometry("600x735")
fenster.title("Statisticus v2.0")
fenster.grid_columnconfigure(1, weight=1)
# Theme (azure.tcl muss im selben Ordner liegen)
try:
    fenster.tk.call("source", "azure.tcl")
    fenster.tk.call("set_theme", "dark")
except Exception:
    pass

def change_theme():
    try:
        if fenster.tk.call("ttk::style", "theme", "use") == "azure-dark":
            fenster.tk.call("set_theme", "light")
        else:
            fenster.tk.call("set_theme", "dark")
    except Exception:
        pass

switch = ttk.Checkbutton(fenster, text="💡 Switch", style="Switch.TCheckbutton", command=change_theme)

# Eingabe-GUI (Labels + Entries)
date_today = datetime.now()
labeltoday = Label(fenster, text=f"{date_today:%A, %B %d, %Y}", font=("Calibri", 8))

labelbenutzer = Label(fenster, text="BenutzerIn:", font=("Calibri", 13))
labelkopie_scan = Label(fenster, text="Kopie/Scan:", font=("Calibri", 13))
labelanfrage = Label(fenster, text="Anfrage:", font=("Calibri", 13))
labelvisitor = Label(fenster, text="BesucherIn:", font=("Calibri", 13))

benutzeranzahl = ttk.Entry(fenster, width=12, font=("Calibri", 13))
kopie_scan = ttk.Entry(fenster, width=12, font=("Calibri", 13))
anfrage = ttk.Entry(fenster, width=12, font=("Calibri", 13))
visitor = ttk.Entry(fenster, width=12, font=("Calibri", 13))

# Enter-Taste speichert
benutzeranzahl.bind("<Return>", lambda e: speichern())
kopie_scan.bind("<Return>", lambda e: speichern())
anfrage.bind("<Return>", lambda e: speichern())
visitor.bind("<Return>", lambda e: speichern())

# Jahres-Zähler-Labels
labelgesamtb = Label(fenster, text="BenutzerInnen lfd. Jahr:", font=("Calibri", 11))
labelgesamtk = Label(fenster, text="Kopien/Scans lfd. Jahr:", font=("Calibri", 11))
labelgesamta = Label(fenster, text="Anfragen lfd. Jahr:", font=("Calibri", 11))
labelgesamtv = Label(fenster, text="BesucherInnen lfd. Jahr:", font=("Calibri", 11))

labelzaehlerb = Label(fenster, text=str(get_total_year("valueb")), font=("Calibri", 11))
labelzaehlerks = Label(fenster, text=str(get_total_year("valueks")), font=("Calibri", 11))
labelzaehlera = Label(fenster, text=str(get_total_year("valuea")), font=("Calibri", 11))
labelzaehlerv = Label(fenster, text=str(get_total_year("valuev")), font=("Calibri", 11))

SpeichernButton = ttk.Button(fenster, text="SPEICHERN", style="Accent.TButton", width=16, command=speichern)
AnalyzerButton = ttk.Button(fenster, text="ABFRAGE", style="Accent.TButton", width=16, command=open_analyzer)
BeendenButton = ttk.Button(fenster, text="BEENDEN", style="Accent.TButton", width=16, command=fenster.quit)
# ---------------------------------------------------------------------------
# Layout (grid) – Korrigierte Platzierung (Eingabefelder bleiben sichtbar)
# ---------------------------------------------------------------------------

# Zeile 0..3: Eingabefelder
labelbenutzer.grid(row=0, column=0, padx=50, pady=(30, 12), sticky=W)
benutzeranzahl.grid(row=0, column=2, pady=(30, 12))

labelkopie_scan.grid(row=1, column=0, padx=50, pady=12, sticky=W)
kopie_scan.grid(row=1, column=2, pady=12)

labelanfrage.grid(row=2, column=0, padx=50, pady=12, sticky=W)
anfrage.grid(row=2, column=2, pady=12)

labelvisitor.grid(row=3, column=0, padx=50, pady=12, sticky=W)
visitor.grid(row=3, column=2, pady=12)

# Zeile 4..7: Jahres-Gesamtlabels
labelgesamtb.grid(row=4, column=0, padx=50, pady=(60,8), sticky=W)
labelzaehlerb.grid(row=4, column=2, pady=(60,8))

labelgesamtk.grid(row=5, column=0, padx=50, pady=8, sticky=W)
labelzaehlerks.grid(row=5, column=2, pady=8)

labelgesamta.grid(row=6, column=0, padx=50, pady=8, sticky=W)
labelzaehlera.grid(row=6, column=2, pady=8)

labelgesamtv.grid(row=7, column=0, padx=50, pady=8, sticky=W)
labelzaehlerv.grid(row=7, column=2, pady=8)

# ---------------------------------------------------------------------------
# Button-Layout (klassisch, stabil)
# ---------------------------------------------------------------------------

# Abfrage links mit identischem Einzug wie die Labels
AnalyzerButton.grid(row=8, column=0, padx=50, pady=(40,10), sticky=W)

# Speichern rechts unter den Eingabefeldern
SpeichernButton.grid(row=8, column=2, padx=50, pady=(40,10), sticky=E)


# Beenden zentriert darunter
BeendenButton.grid(row=9, column=1, pady=(40,20))


# Datum ganz unten links
switch.grid(row=10, column=0, padx=50, pady=(40, 10), sticky=SW)

# Switch ganz unten rechts
labeltoday.grid(row=10, column=2, padx=50, pady=(40, 10), sticky=SE)


# Update Zähler und Start
update_counters()
fenster.mainloop()
