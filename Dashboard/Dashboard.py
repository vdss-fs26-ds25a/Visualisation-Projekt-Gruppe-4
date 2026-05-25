import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Dashboard", layout="wide")

st.title("Strom Dashboard")

#Daten laden
df = pd.read_excel("Data_Strom.xlsx", sheet_name=0)

#Daten
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

#FILTER
st.sidebar.header("Filter")

jahr_min = int(df["Jahr"].min())
jahr_max = int(df["Jahr"].max())

jahr_range = st.sidebar.slider(
    "Jahre auswählen",
    min_value=jahr_min,
    max_value=jahr_max,
    value=(jahr_min, jahr_max))

monate = st.sidebar.multiselect(
    "Monate auswählen",
    options=df["Monat"].unique(),
    default=df["Monat"].unique())

#data filter
df_filtered = df[
    (df["Jahr"] >= jahr_range[0]) &
    (df["Jahr"] <= jahr_range[1]) &
    (df["Monat"].isin(monate))]

st.write(f"Datenpunkte: {len(df_filtered)}")

col1, col2 = st.columns(2)

# Tempreratur
with col1:
    st.subheader("Temperatur")

    fig, ax = plt.subplots()
    ax.plot(df_filtered["Datum"], df_filtered["Temperatur (C°)"])

    ax.set_xlabel("Datum")
    ax.set_ylabel("°C")
    ax.set_title("Temperatur")

    plt.xticks(rotation=45)
    st.pyplot(fig)

# Strombilanz
with col2:
    st.subheader("Strombilanz")

    df_filtered["Bilanz"] = (
        df_filtered["Stromerzeugnisse"] -
        df_filtered["Stromverbrauch"])

    fig, ax = plt.subplots()
    ax.plot(df_filtered["Datum"], df_filtered["Bilanz"])

    ax.axhline(0, color="black", linewidth=1)

    ax.set_title("Erzeugung - Verbrauch")
    ax.set_xlabel("Datum")
    ax.set_ylabel("Differenz")

    plt.xticks(rotation=45)
    st.pyplot(fig)

# Bevölkerung
st.subheader("Bevölkerung")

df_pop = df_filtered.groupby("Jahr")["Bevölkerung"].max().reset_index()

fig, ax = plt.subplots()
ax.bar(df_pop["Jahr"], df_pop["Bevölkerung"])

ax.set_title("Bevölkerung pro Jahr")
ax.set_xlabel("Jahr")
ax.set_ylabel("Einwohner")

st.pyplot(fig)