"""
============================================================
 IMPUTATION HEIZBEDARF 1990-1993
============================================================
Die MeteoSchweiz-Heizgradtage (ogd105) sind erst ab 1994
verfügbar. Eure Stromdaten reichen aber bis 1990 zurück, also
fehlen 48 Monatswerte (Jan 1990 - Dez 1993).

Dieses Script trainiert ein lineares Regressionsmodell auf den
echten HGT-Werten (1994-2025) und schätzt damit die fehlenden
Werte für 1990-1993.

Eingangs-Variablen (Features):
  - Monatsmitteltemperatur (°C)
  - Anzahl Tage im Monat
  - Sinus & Cosinus des Monats (Saisonalkodierung)

Modellqualität:
  - R² ≈ 0.97
  - MAE ≈ 22 HGT (bei typischen Werten 0-700)

Verwendung:
  pip install pandas openpyxl scikit-learn
  python regression_heizbedarf.py

Output: Data_Strom_mit_HGT.xlsx (mit aufgefüllter Heizbedarf-Spalte
        + Spalte "Heizbedarf_quelle" zur Transparenz)
============================================================
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# ------------------------------------------------------------
# 1. Eingabe-Dateien laden
# ------------------------------------------------------------
STROM_FILE = "Data_Strom.xlsx"          # Salomons Datensatz
HGT_FILE   = "ogd105_heizgradtage.csv"  # MeteoSchweiz, opendata.swiss
OUT_FILE   = "Data_Strom_mit_HGT.xlsx"

# MeteoSchweiz CSV (latin-1 wegen Umlauten)
hgt = pd.read_csv(HGT_FILE, encoding="latin-1")
hgt = hgt.dropna(subset=["Jahr", "Monat"])
hgt["Jahr"]  = hgt["Jahr"].astype(int)
hgt["Monat"] = hgt["Monat"].astype(int)

# Stromdatensatz
df = pd.read_excel(STROM_FILE, sheet_name=0)

# ------------------------------------------------------------
# 2. Vorverarbeitung
# ------------------------------------------------------------
# Monatsnamen -> Zahlen
month_map = {
    "jan": 1, "feb": 2, "mar": 3,  "apr": 4,  "may": 5,  "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}
df["Monat_num"] = df["Monat"].str.lower().map(month_map)

# Tage pro Monat (Februar als 28.25 -> Mittelwert über Schaltjahre)
days_per_month = {
    1:31, 2:28.25, 3:31, 4:30, 5:31, 6:30,
    7:31, 8:31, 9:30, 10:31, 11:30, 12:31,
}
df["Tage"] = df["Monat_num"].map(days_per_month)

# MeteoSchweiz-HGT mit Strom-Datensatz mergen
df = df.merge(
    hgt.rename(columns={"Monat": "Monat_num", "Heizgradtage": "HGT_real"}),
    on=["Jahr", "Monat_num"],
    how="left",
)

# Saisonalitäts-Features (zyklisch: Dez und Jan sind im Featurespace nah)
df["sin_m"] = np.sin(2 * np.pi * df["Monat_num"] / 12)
df["cos_m"] = np.cos(2 * np.pi * df["Monat_num"] / 12)

# ------------------------------------------------------------
# 3. Modell trainieren auf Zeilen mit echten HGT-Werten
# ------------------------------------------------------------
features = ["Temperatur (C°)", "Tage", "sin_m", "cos_m"]

train = df.dropna(subset=["HGT_real"]).copy()
X_train = train[features].values
y_train = train["HGT_real"].values

model = LinearRegression().fit(X_train, y_train)

# Modell-Qualität
r2  = model.score(X_train, y_train)
mae = np.mean(np.abs(model.predict(X_train) - y_train))
print(f"R²  = {r2:.4f}")
print(f"MAE = {mae:.1f} HGT")
print(f"Koeffizienten: {dict(zip(features, model.coef_.round(3)))}")
print(f"Intercept:     {model.intercept_:.2f}")

# ------------------------------------------------------------
# 4. Vorhersage für ALLE Zeilen, dann nur die fehlenden auffüllen
# ------------------------------------------------------------
df["HGT_pred"] = model.predict(df[features].values).clip(min=0)

# Spalte "Heizbedarf" befüllen: echter Wert wo vorhanden, sonst Vorhersage
df["Heizbedarf"] = df["HGT_real"].fillna(df["HGT_pred"]).round(1)

# Transparenz-Spalte (für Data Report)
df["Heizbedarf_quelle"] = np.where(
    df["HGT_real"].notna(), "MeteoSchweiz", "geschätzt"
)

# ------------------------------------------------------------
# 5. Aufräumen und speichern
# ------------------------------------------------------------
df = df.drop(columns=["Monat_num", "Tage", "sin_m", "cos_m",
                       "HGT_real", "HGT_pred"])

df.to_excel(OUT_FILE, sheet_name="Daten", index=False)
n_est = (df["Heizbedarf_quelle"] == "geschätzt").sum()
print(f"\n✓ {len(df)} Zeilen geschrieben nach '{OUT_FILE}'")
print(f"  davon {n_est} mit geschätzten Heizbedarf-Werten")
