import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Strom Dashboard", layout="wide")

# data load
df = pd.read_excel("Data_Strom.xlsx", sheet_name=0)

df = df[df["Jahr"] != 2026]

month_map = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "may": 5, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "oct": 10, "nov": 11, "dec": 12}

df["Monat_num"] = df["Monat"].str.lower().map(month_map)

df["Datum"] = pd.to_datetime({
    "year": df["Jahr"],
    "month": df["Monat_num"],
    "day": 1})

df = df.sort_values("Datum")

df["Bevölkerung"] = (
    df["Bevölkerung"]
    .astype(str)
    .str.replace("’", "", regex=False)
    .str.replace(" ", "", regex=False)
    .astype(float))

# Seiten
page = st.sidebar.selectbox(
    "Seite auswählen",
    ["Start / Overview", "Analyse 1", "Analyse 2"])

# globale Filter
st.sidebar.header("Filter")

jahr_min = int(df["Jahr"].min())
jahr_max = int(df["Jahr"].max())

jahr_range = st.sidebar.slider(
    "Jahre auswählen",
    min_value=jahr_min,
    max_value=jahr_max,
    value=(jahr_min, jahr_max))

df_filtered = df[
    (df["Jahr"] >= jahr_range[0]) &
    (df["Jahr"] <= jahr_range[1])]

# Seite 1 - übersicht
if page == "Start / Overview":

    st.title("Strom Dashboard – Überblick")

    st.write("""
    Diese Seite zeigt den geglätteten Stromverbrauch über die Zeit (1990–2025).
    Die Darstellung hebt strukturelle Phasen hervor.
    """)

    st.info("""
    Phasen:
    - 1990–1999: stabile Entwicklung  
    - 2000–2008: Wachstum  
    - 2009–2025: Sättigung / Volatilität  
    """)

    df_filtered = df_filtered.sort_values("Datum")
    df_filtered["Trend"] = df_filtered["Stromverbrauch"].rolling(12).mean()

    fig, ax = plt.subplots()

    # Hauptlinie
    ax.plot(df_filtered["Datum"],
            df_filtered["Trend"],
            color="black",
            linewidth=2,
            label="Stromverbrauch (Trend)")

    # Phasen
    ax.axvspan(pd.Timestamp("1990-01-01"),
               pd.Timestamp("1999-12-01"),
               color="green",
               alpha=0.1,
               label="1990–1999")

    ax.axvspan(pd.Timestamp("2000-01-01"),
               pd.Timestamp("2008-12-01"),
               color="orange",
               alpha=0.1,
               label="2000–2008")

    ax.axvspan(pd.Timestamp("2009-01-01"),
               pd.Timestamp("2025-12-01"),
               color="red",
               alpha=0.1,
               label="2009–2025")

    # WICHTIG: doppelte Labels entfernen
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys())

    # Styling
    ax.set_title("Stromverbrauch über Zeit (Phasenmodell)")
    ax.set_xlabel("Jahre")
    ax.set_ylabel("Stromverbrauch (geglättet)")

    st.pyplot(fig)
    
# Seite 2 - Analyse 1 -> Trend
elif page == "Analyse 1":

    st.title("Analyse 1 – Langfristige Entwicklung")

    df_year = df_filtered.groupby("Jahr")[[
        "Stromverbrauch",
        "Temperatur (C°)"
    ]].mean().reset_index()

    fig, ax1 = plt.subplots()

    # Verbrauch
    ax1.plot(df_year["Jahr"],
             df_year["Stromverbrauch"],
             label="Stromverbrauch",
             color="blue")

    ax1.set_xlabel("Jahr")
    ax1.set_ylabel("Stromverbrauch", color="blue")

    # Temperatur 
    ax2 = ax1.twinx()
    ax2.plot(df_year["Jahr"],
             df_year["Temperatur (C°)"],
             label="Temperatur",
             color="red")

    ax2.set_ylabel("Temperatur (°C)", color="red")

    st.pyplot(fig)

# Seite 3 - Analyse 2
elif page == "Analyse 2":

    st.title("Analyse 2 – Temperatur vs Verbrauch")

    fig, ax = plt.subplots()

    ax.scatter(
        df_filtered["Temperatur (C°)"],
        df_filtered["Stromverbrauch"],
        alpha=0.5)

    ax.set_title("Zusammenhang Temperatur vs Stromverbrauch")
    ax.set_xlabel("Temperatur (°C)")
    ax.set_ylabel("Stromverbrauch")

    st.pyplot(fig)