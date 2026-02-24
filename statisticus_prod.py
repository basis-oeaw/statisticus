## Statisticus v1.2.0 ##
# Tool zum Speichern der Anzahl von BenutzerInnen, BesucherInnen, angefertigten Kopien/Scans und Anfragen in BASIS.
# Autor: Roman Sack, (überarbeitet von ChatGPT 2025)
# Verbesserungen: saubere DB-Verwaltung, bessere Fehlerprüfung, robustere GUI

#Enter-Funktion: alle vier Felder speichern einzeln per <Return>.
#Button „Speichern“: schreibt alle vier Felder gleichzeitig.
#DB-Verwaltung: nutzt with sqlite3.connect (sicher und sauber).
#Fehlerbehandlung: durch validate_int() mit messagebox.
#Gesamtzähler: wird korrekt ausgelesen und aktualisiert.
#GUI: gut strukturiert, Azure-Theme richtig eingebunden.
#Theme-Switch: funktioniert stabil und ohne Stilkonflikte.

from tkinter import *
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3

# === Setup ===
DB_NAME = "statisticus.db"

# aktuelles Datum
date_today = datetime.now()

# Datenbank vorbereiten
with sqlite3.connect(DB_NAME) as conn:
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Statistik (
            entry_number INTEGER PRIMARY KEY,
            today TEXT,
            valueb INTEGER,
            valueks INTEGER,
            valuea INTEGER,
            valuev INTEGER
        )
    """)

# === Hilfsfunktionen ===
def insert_data(zb=None, zks=None, za=None, zv=None):
    """Fügt einen Datensatz in die DB ein."""
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO Statistik (today, valueb, valueks, valuea, valuev) VALUES (CURRENT_TIMESTAMP, ?, ?, ?, ?)",
            (zb, zks, za, zv)
        )
        conn.commit()

def get_total(column):
    """Gibt die Summe einer Spalte zurück (0 falls leer)."""
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT TOTAL({column}) FROM Statistik")
        result = cur.fetchone()[0]
        return int(result or 0)

def validate_int(value):
    """Validiert Integer-Eingaben."""
    if value == "":
        return None
    try:
        return int(value)
    except ValueError:
        messagebox.showerror("Fehler", "Bitte eine ganze Zahl eingeben.")
        return None

def update_counters():
    """Aktualisiert alle Zählerlabels."""
    labelzaehlerb.config(text=str(get_total("valueb")))
    labelzaehlerks.config(text=str(get_total("valueks")))
    labelzaehlera.config(text=str(get_total("valuea")))
    labelzaehlerv.config(text=str(get_total("valuev")))

# === Eingabefunktionen ===
def speichern():
    zb = validate_int(benutzeranzahl.get())
    zks = validate_int(kopie_scan.get())
    za = validate_int(anfrage.get())
    zv = validate_int(visitor.get())

    if zb is None and zks is None and za is None and zv is None:
        return  # nichts eingegeben

    insert_data(zb, zks, za, zv)
    update_counters()

    # Eingabefelder leeren
    for e in (benutzeranzahl, kopie_scan, anfrage, visitor):
        e.delete(0, END)
        
        
def get_datab(event):
    eingabeb = benutzeranzahl.get()
    try:
        zb = int(eingabeb)
    except ValueError:
        messagebox.showerror("Fehler", "Bitte eine ganze Zahl eingeben")
        return

    verbindung = sqlite3.connect(DB_NAME)
    zeiger = verbindung.cursor()
    zeiger.execute(
        "INSERT INTO Statistik (today, valueb, valueks, valuea, valuev) VALUES (CURRENT_TIMESTAMP, ?, ?, ?, ?)",
        (zb, None, None, None),
    )

    zeiger.execute("SELECT total(valueb) FROM Statistik")
    labelzaehlerb.config(text=str(round(zeiger.fetchone()[0])))
    verbindung.commit()
    verbindung.close()
    benutzeranzahl.delete(0, "end")


def get_dataks(event):
    eingabeks = kopie_scan.get()
    try:
        zks = int(eingabeks)
    except ValueError:
        messagebox.showerror("Fehler", "Bitte eine ganze Zahl eingeben")
        return

    verbindung = sqlite3.connect(DB_NAME)
    zeiger = verbindung.cursor()
    zeiger.execute(
        "INSERT INTO Statistik (today, valueb, valueks, valuea, valuev) VALUES (CURRENT_TIMESTAMP, ?, ?, ?, ?)",
        (None, zks, None, None),
    )

    zeiger.execute("SELECT total(valueks) FROM Statistik")
    labelzaehlerks.config(text=str(round(zeiger.fetchone()[0])))
    verbindung.commit()
    verbindung.close()
    kopie_scan.delete(0, "end")


def get_dataa(event):
    eingabea = anfrage.get()
    try:
        za = int(eingabea)
    except ValueError:
        messagebox.showerror("Fehler", "Bitte eine ganze Zahl eingeben")
        return

    verbindung = sqlite3.connect(DB_NAME)
    zeiger = verbindung.cursor()
    zeiger.execute(
        "INSERT INTO Statistik (today, valueb, valueks, valuea, valuev) VALUES (CURRENT_TIMESTAMP, ?, ?, ?, ?)",
        (None, None, za, None),
    )

    zeiger.execute("SELECT total(valuea) FROM Statistik")
    labelzaehlera.config(text=str(round(zeiger.fetchone()[0])))
    verbindung.commit()
    verbindung.close()
    anfrage.delete(0, "end")


def get_datav(event):
    eingabev = visitor.get()
    try:
        zv = int(eingabev)
    except ValueError:
        messagebox.showerror("Fehler", "Bitte eine ganze Zahl eingeben")
        return

    verbindung = sqlite3.connect(DB_NAME)
    zeiger = verbindung.cursor()
    zeiger.execute(
        "INSERT INTO Statistik (today, valueb, valueks, valuea, valuev) VALUES (CURRENT_TIMESTAMP, ?, ?, ?, ?)",
        (None, None, None, zv),
    )

    zeiger.execute("SELECT total(valuev) FROM Statistik")
    labelzaehlerv.config(text=str(round(zeiger.fetchone()[0])))
    verbindung.commit()
    verbindung.close()
    visitor.delete(0, "end")


# === GUI ===
fenster = Tk()
fenster.geometry("465x685")
fenster.title("Statisticus v1.2.0")

# Azure-Theme laden
fenster.tk.call("source", "azure.tcl")
fenster.tk.call("set_theme", "dark")

def change_theme():
    if fenster.tk.call("ttk::style", "theme", "use") == "azure-dark":
        fenster.tk.call("set_theme", "light")
    else:
        fenster.tk.call("set_theme", "dark")

switch = ttk.Checkbutton(fenster, text='💡 Switch', style='Switch.TCheckbutton', command=change_theme)

# Eingabefelder
benutzeranzahl = ttk.Entry(fenster, width=12, font=("Calibri", 13))
kopie_scan = ttk.Entry(fenster, width=12, font=("Calibri", 13))
anfrage = ttk.Entry(fenster, width=12, font=("Calibri", 13))
visitor = ttk.Entry(fenster, width=12, font=("Calibri", 13))

# binden von <Return> (Enter-Taste) an die jeweiligen Funktionen
benutzeranzahl.bind('<Return>', get_datab)
kopie_scan.bind('<Return>', get_dataks)
anfrage.bind('<Return>', get_dataa)
visitor.bind('<Return>', get_datav)


# Labels
labelbenutzer = Label(fenster, text="BenutzerIn:", font=("Calibri", 13))
labelkopie_scan = Label(fenster, text="Kopie/Scan:", font=("Calibri", 13))
labelanfrage = Label(fenster, text="Anfrage:", font=("Calibri", 13))
labelvisitor = Label(fenster, text="BesucherIn:", font=("Calibri", 13))

labelgesamtb = Label(fenster, text="BenutzerInnen gesamt:", font=("Calibri", 11))
labelgesamtk = Label(fenster, text="Kopien/Scans gesamt:", font=("Calibri", 11))
labelgesamta = Label(fenster, text="Anfragen gesamt:", font=("Calibri", 11))
labelgesamtv = Label(fenster, text="BesucherInnen gesamt:", font=("Calibri", 11))

labeltoday = Label(fenster, text=f"{date_today:%A, %B %d, %Y}", font=("Calibri", 8))

# Zählerlabels mit Startwerten
labelzaehlerb = Label(fenster, text=str(get_total("valueb")), font=("Calibri", 11))
labelzaehlerks = Label(fenster, text=str(get_total("valueks")), font=("Calibri", 11))
labelzaehlera = Label(fenster, text=str(get_total("valuea")), font=("Calibri", 11))
labelzaehlerv = Label(fenster, text=str(get_total("valuev")), font=("Calibri", 11))

# Speichern-Button
SpeichernButton = ttk.Button(fenster, text="SPEICHERN", style="Accent.TButton", width=18, command=speichern)


# Grid-Layout
labelbenutzer.grid(row=0, column=0, padx=50, pady=(30, 20), sticky=W)
labelkopie_scan.grid(row=1, column=0, padx=50, pady=20, sticky=W)
labelanfrage.grid(row=2, column=0, padx=50, pady=20, sticky=W)
labelvisitor.grid(row=3, column=0, padx=50, pady=20, sticky=W)

labelgesamtb.grid(row=4, column=0, padx=50, pady=(40, 15), sticky=W)
labelgesamtk.grid(row=5, column=0, padx=50, pady=15, sticky=W)
labelgesamta.grid(row=6, column=0, padx=50, pady=15, sticky=W)
labelgesamtv.grid(row=7, column=0, padx=50, pady=15, sticky=W)

labelzaehlerb.grid(row=4, column=2, padx=20, pady=(40, 15))
labelzaehlerks.grid(row=5, column=2, padx=20, pady=15)
labelzaehlera.grid(row=6, column=2, padx=20, pady=15)
labelzaehlerv.grid(row=7, column=2, padx=20, pady=15)

benutzeranzahl.grid(row=0, column=2, padx=0, pady=(30, 20))
kopie_scan.grid(row=1, column=2, padx=0, pady=20)
anfrage.grid(row=2, column=2, padx=0, pady=20)
visitor.grid(row=3, column=2, padx=0, pady=20)

SpeichernButton.grid(row=8, column=2, padx=0, pady=(30, 10))
switch.grid(row=8, column=0, padx=50, pady=(30, 10), sticky=W)
labeltoday.grid(row=9, column=0, padx=8, pady=(30, 0), sticky=W)

# Startwerte aktualisieren
update_counters()

# Start
fenster.mainloop()
