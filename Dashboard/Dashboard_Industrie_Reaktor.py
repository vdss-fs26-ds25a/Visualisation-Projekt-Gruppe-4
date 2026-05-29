# ============================================================
#  STROM SCHWEIZ — INDUSTRIE/ENERGIE DASHBOARD (NEU)
# ============================================================
#  Erweiterte Version mit Jahreszeiten-Filter und
#  Kernkraft-Anzeige (Easter Egg)
#
#  Start:
#      streamlit run Dashboard_Industrie_Reaktor_neu.py
#
#  Datenquelle: Data_Strom_korrigiert.xlsx
# ============================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import shutil
import tempfile
import os

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="STROM SCHWEIZ — Energie Dashboard",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="expanded",
)

# ── PALETTE ───────────────────────────────────────────────────────────────────
ORANGE       = "#ff8c42"
AMBER        = "#ffd166"
TEAL         = "#06d6a0"
RED          = "#ef476f"
BLUE         = "#118ab2"
TEXT         = "#d4d8de"
MUTED        = "#9ca3af"
WHITE        = "#ffffff"
SURFACE      = "#21252b"
SURFACE_LINE = "#2a2e35"
BG           = "#1c2025"

# ── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

    .stApp {
        background: linear-gradient(180deg, #1c2025 0%, #181b1f 100%);
        color: #d4d8de;
    }
    section[data-testid="stSidebar"] {
        background: #15171b;
        border-right: 1px solid #2a2e35;
    }
    section[data-testid="stSidebar"] * {
        color: #d4d8de !important;
        font-family: 'Inter', sans-serif;
    }
    h1 {
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        letter-spacing: -0.02em;
        font-size: 2.2rem !important;
        line-height: 1.1;
    }
    h1::before {
        content: "";
        display: inline-block;
        width: 4px;
        height: 1.8rem;
        background: #ff8c42;
        margin-right: 14px;
        vertical-align: -4px;
        border-radius: 1px;
    }
    h2, h3 {
        color: #ffffff !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600;
    }
    .meta-label {
        font-family: 'Inter', sans-serif;
        color: #ff8c42;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        margin-bottom: 0.3rem;
    }
    .meta-subtitle {
        color: #9ca3af;
        font-size: 0.95rem;
        font-weight: 400;
        margin-bottom: 1.5rem;
        line-height: 1.5;
    }
    [data-testid="metric-container"],
    [data-testid="stMetric"] {
        background: #2c3138 !important;
        border: 1px solid #3a4049 !important;
        border-left: 3px solid #ff8c42 !important;
        border-radius: 4px;
        padding: 1rem 1.2rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.4);
    }
    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] > div {
        color: #ffffff !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1.85rem !important;
    }
    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] > div,
    [data-testid="stMetricLabel"] p {
        color: #e5e7eb !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.72rem !important;
        letter-spacing: 0.12em !important;
        text-transform: uppercase !important;
        font-weight: 600 !important;
        opacity: 1 !important;
    }
    div[role="radiogroup"] label,
    div[role="radiogroup"] label p,
    div[role="radiogroup"] label * {
        color: #ffffff !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        opacity: 1 !important;
    }
    .stRadio > label {
        color: #ff8c42 !important;
        font-size: 0.72rem !important;
        letter-spacing: 0.12em !important;
        text-transform: uppercase !important;
        font-weight: 600 !important;
    }
    [data-testid="stPlotlyChart"] {
        background: #21252b;
        border: 1px solid #2a2e35;
        border-radius: 4px;
        padding: 0.75rem;
    }
    .stAlert {
        background: #21252b !important;
        border-left: 3px solid #ff8c42 !important;
        color: #d4d8de !important;
        border-radius: 4px;
    }
    #MainMenu, footer { visibility: hidden; }
    header { background: transparent !important; }
    [data-testid="collapsedControl"] {
        background: #ff8c42 !important;
        color: #1c2025 !important;
        border-radius: 4px;
        padding: 6px;
        box-shadow: 0 2px 8px rgba(255, 140, 66, 0.4);
    }
    [data-testid="collapsedControl"]:hover { background: #ffd166 !important; }
    [data-testid="collapsedControl"] svg { fill: #1c2025 !important; }
    [data-baseweb="select"] > div {
        background: #21252b !important;
        border: 1px solid #2a2e35 !important;
        color: #ffd166 !important;
        border-radius: 3px;
    }
    [data-testid="stSlider"] [role="slider"] { background: #ff8c42 !important; }
    .status-dot {
        display: inline-block;
        width: 8px; height: 8px;
        background: #06d6a0;
        border-radius: 50%;
        margin-right: 8px;
        box-shadow: 0 0 8px rgba(6, 214, 160, 0.6);
        animation: pulse 2s ease-in-out infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50%       { opacity: 0.5; }
    }
    hr { border-color: #2a2e35 !important; margin: 1.5rem 0 !important; }
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.7rem !important;
        color: #ff8c42 !important;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }
    .block-container { padding-top: 2rem; padding-bottom: 3rem; }
</style>
""", unsafe_allow_html=True)


# ── DATA LOADING ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    # Kopiere die Datei zuerst in einen temp-Ordner, damit ein Excel-Lock
    # (PermissionError unter Windows) umgangen wird.
    src = os.path.join(os.path.dirname(__file__), "Data_Strom_korrigiert.xlsx")
    tmp_dir = tempfile.mkdtemp()
    tmp_path = os.path.join(tmp_dir, "Data_Strom_korrigiert.xlsx")
    shutil.copy2(src, tmp_path)
    df = pd.read_excel(tmp_path, sheet_name=0)
    df = df[df["Jahr"] != 2026]
    month_map = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4,
        "may": 5, "jun": 6, "jul": 7, "aug": 8,
        "sep": 9, "oct": 10, "nov": 11, "dec": 12,
    }
    df["Monat_num"] = df["Monat"].str.lower().map(month_map)
    df["Datum"] = pd.to_datetime({
        "year": df["Jahr"], "month": df["Monat_num"], "day": 1
    })
    df = df.sort_values("Datum").reset_index(drop=True)
    df["Bevoelkerung_num"] = (
        df["Bevölkerung"].astype(str)
        .str.replace("'", "", regex=False)
        .str.replace(" ", "", regex=False)
        .astype(float)
    )
    df["Stromverbrauch_pro_Kopf"] = (
        df["Stromverbrauch"] * 1_000_000 / df["Bevoelkerung_num"]
    )
    return df


df = load_data()


# ── SEASON HELPERS ────────────────────────────────────────────────────────────
def _s(s):
    return s.lower()

def season_sort_key(s):
    if "winter" in _s(s): return 0
    if "ling"   in _s(s): return 1   # Frühling
    if "sommer" in _s(s): return 2
    if "herbst" in _s(s): return 3
    return 4

def season_icon(s):
    if "winter" in _s(s): return "❄️"
    if "ling"   in _s(s): return "🌸"
    if "sommer" in _s(s): return "☀️"
    if "herbst" in _s(s): return "🍂"
    return "🌡️"

def season_color(s):
    if "winter" in _s(s): return BLUE
    if "ling"   in _s(s): return TEAL
    if "sommer" in _s(s): return AMBER
    if "herbst" in _s(s): return ORANGE
    return TEXT


ALL_SEASONS    = sorted(df["saison"].dropna().unique().tolist(), key=season_sort_key)
SEASON_LABELS  = {s: f"{season_icon(s)} {s}" for s in ALL_SEASONS}
LABEL_TO_SEASON = {v: k for k, v in SEASON_LABELS.items()}


# ── PLOTLY HELPERS ────────────────────────────────────────────────────────────
def style_fig(fig, title=None, height=480):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=BG,
        font=dict(family="Inter, sans-serif", color=TEXT, size=13),
        title=dict(
            text=title,
            font=dict(family="Space Grotesk, sans-serif", color=WHITE, size=16),
            x=0.02, xanchor="left",
        ) if title else None,
        margin=dict(l=60, r=80, t=70, b=50),
        height=height,
        hoverlabel=dict(bgcolor=SURFACE, bordercolor=ORANGE,
                        font=dict(family="Inter, sans-serif", color=TEXT)),
        xaxis=dict(gridcolor=SURFACE_LINE, zerolinecolor=SURFACE_LINE,
                   color=MUTED, linecolor=SURFACE_LINE, showline=True,
                   tickfont=dict(family="Inter, sans-serif", size=11)),
        yaxis=dict(gridcolor=SURFACE_LINE, zerolinecolor=SURFACE_LINE,
                   color=MUTED, linecolor=SURFACE_LINE, showline=True,
                   tickfont=dict(family="Inter, sans-serif", size=11)),
        showlegend=True,
        legend=dict(bgcolor=SURFACE, bordercolor=SURFACE_LINE, borderwidth=1,
                    font=dict(color=TEXT), orientation="h", y=-0.15),
        dragmode=False,
    )
    # Achsen fixieren → Linien lassen sich nicht verschieben / zoomen
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def animated_line(df_plot, x_col, y_col, color=ORANGE, n_frames=25):
    step = max(1, len(df_plot) // n_frames)
    frames = []
    for i in range(step, len(df_plot) + 1, step):
        sub = df_plot.iloc[:i]
        frames.append(go.Frame(
            data=[go.Scatter(x=sub[x_col], y=sub[y_col], mode="lines",
                             line=dict(color=color, width=2.5, shape="spline"),
                             name=y_col)],
            name=str(i),
        ))
    fig = go.Figure(
        data=[go.Scatter(x=df_plot[x_col], y=df_plot[y_col], mode="lines",
                         line=dict(color=color, width=2.5, shape="spline"),
                         name=y_col)],
        frames=frames,
        layout=go.Layout(
            updatemenus=[dict(
                type="buttons", showactive=False,
                y=1.15, x=1.0, xanchor="right",
                bgcolor=SURFACE, bordercolor=ORANGE,
                font=dict(color=ORANGE, family="Inter, sans-serif", size=11),
                buttons=[dict(
                    label="↻ Replay", method="animate",
                    args=[None, {"frame": {"duration": 35, "redraw": True},
                                 "fromcurrent": True,
                                 "transition": {"duration": 0}}],
                )],
            )],
        ),
    )
    return fig


# ── NUCLEAR HELPER ────────────────────────────────────────────────────────────
def calc_kkw(df_filt, df_all, selected_seasons):
    """
    Summiert Kernkraft-GWh für den gefilterten Zeitraum.
    Fehlende Werte (vor 2000) werden durch den Saison-Durchschnitt von 2000 ersetzt.
    """
    df_2000 = df_all[
        (df_all["Jahr"] == 2000) & (df_all["saison"].isin(selected_seasons))
    ]
    avg_2000 = df_2000.groupby("saison")["Erzeugung_Kernkraftwerk_GWh"].mean().to_dict()

    known   = df_filt["Erzeugung_Kernkraftwerk_GWh"].dropna().sum()
    missing = df_filt[df_filt["Erzeugung_Kernkraftwerk_GWh"].isna()]
    fallback = missing["saison"].map(avg_2000).fillna(0).sum()
    return known + fallback


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<div style='font-family: Space Grotesk, sans-serif; "
        "font-size: 1.3rem; font-weight: 700; color: #ffffff;'>"
        "⚡ STROM <span style='color: #ff8c42;'>SCHWEIZ</span></div>",
        unsafe_allow_html=True,
    )
    # Status (Reaktor-Auslastung) wird unten gefüllt, sobald der KKW-Anteil bekannt ist
    status_ph = st.empty()
    st.markdown("---")

    st.markdown("### MODUL")
    page = st.selectbox(
        " ",
        ["Übersicht", "Verbrauch × Temperatur", "Korrelation", "Effizienz / Heizen"],
        label_visibility="collapsed",
    )

    st.markdown("### ZEITBEREICH")
    jahr_min = int(df["Jahr"].min())
    jahr_max = int(df["Jahr"].max())
    jahr_range = st.slider(
        " ", min_value=jahr_min, max_value=jahr_max,
        value=(jahr_min, jahr_max), label_visibility="collapsed",
    )

    # ── Jahreszeit-Filter (Multiple Choice) ──────────────────────────────────
    st.markdown("### JAHRESZEIT")
    selected_seasons = []
    for s in ALL_SEASONS:
        if st.checkbox(f"{season_icon(s)} {s}", value=True, key=f"season_{s}"):
            selected_seasons.append(s)
    if not selected_seasons:
        selected_seasons = ALL_SEASONS   # Fallback: alle Saisons

    # Kombinierter Filter: Jahr + Saison
    df_filtered = df[
        (df["Jahr"] >= jahr_range[0]) &
        (df["Jahr"] <= jahr_range[1]) &
        (df["saison"].isin(selected_seasons))
    ].copy()

    st.markdown("---")
    st.markdown(
        f"<div style='font-family: Inter, sans-serif; font-size: 0.75rem; color: #9ca3af;'>"
        f"<div style='color: #ff8c42; font-weight: 600; letter-spacing: 0.12em; "
        f"margin-bottom: 6px;'>STATUS</div>"
        f"Datenpunkte: <b style='color: #ffd166;'>{len(df_filtered)}</b><br>"
        f"Zeitraum: <b style='color: #ffd166;'>{jahr_range[0]} – {jahr_range[1]}</b>"
        f"</div>",
        unsafe_allow_html=True,
    )


# ── KERNKRAFT-KENNZAHL + REAKTOR-AUSLASTUNG ─────────────────────────────────
prod_cols        = [c for c in df.columns if "tromerzeug" in c.lower()]
prod_col         = prod_cols[0] if prod_cols else "Stromerzeugnisse"
kkw_gwh          = calc_kkw(df_filtered, df, selected_seasons)
total_produktion = df_filtered[prod_col].sum()
kkw_anteil       = (kkw_gwh / total_produktion * 100) if total_produktion > 0 else 0
n_monate         = len(df_filtered)
kkw_pro_monat    = (kkw_gwh / n_monate) if n_monate > 0 else 0

# Auslastung anhand des Kernkraft-Anteils an der Gesamtproduktion
# (z. B. nur Winter ~44 % → hoch, nur Sommer ~26 % → gering)
if kkw_anteil >= 40:
    ausl_text, ausl_color = "HOHE AUSLASTUNG", "#ef476f"      # rot
elif kkw_anteil >= 32:
    ausl_text, ausl_color = "MITTLERE AUSLASTUNG", "#ffd166"  # amber
else:
    ausl_text, ausl_color = "GERINGE AUSLASTUNG", "#06d6a0"   # grün

# Sidebar-Status nachträglich füllen
status_ph.markdown(
    f"<div style='font-family: Inter, sans-serif; font-size: 0.75rem; "
    f"color: {ausl_color}; letter-spacing: 0.1em; font-weight: 600;'>"
    f"<span class='status-dot' style='background:{ausl_color}; "
    f"box-shadow:0 0 8px {ausl_color};'></span>REAKTOR · {ausl_text}"
    f"</div>",
    unsafe_allow_html=True,
)

# Kernkraft-Box (wird im Seitenkopf rechts neben dem Titel gerendert)
KKW_BOX_HTML = f"""
<div style="
    margin-top: 2.0rem; margin-left: auto; width: max-content; max-width: none;
    white-space: nowrap;
    background: #21252b; border: 1px solid #ff8c42; border-radius: 8px;
    padding: 0.55rem 1.2rem; font-family: 'Inter', sans-serif;
    box-shadow: 0 3px 14px rgba(255,140,66,0.40);
">
    <div style="color:#ff8c42; font-size:0.72rem; letter-spacing:0.15em;
         text-transform:uppercase; font-weight:700;">⚛️ Kernkraft</div>
    <div style="color:#fff; font-size:1.35rem; font-weight:700;
         font-family:'Space Grotesk',sans-serif; line-height:1.2;">
         {kkw_gwh:,.0f} GWh<span style="color:#9ca3af; font-size:0.74rem;
         font-weight:400; font-family:'Inter',sans-serif;"> (gesamt)</span></div>
    <div style="color:#9ca3af; font-size:0.74rem;">Ø {kkw_pro_monat:,.0f} GWh / Monat</div>
    <div style="color:#9ca3af; font-size:0.74rem;">{kkw_anteil:.1f} % der Gesamtproduktion in diesem Zeitraum</div>
</div>
"""


def render_header(meta, title, subtitle):
    """Seitenkopf: Titelblock links, Kernkraft-Box rechts daneben."""
    c_left, c_right = st.columns([2.2, 1.1])
    with c_left:
        st.markdown(f"<div class='meta-label'>{meta}</div>", unsafe_allow_html=True)
        st.title(title)
        st.markdown(f"<div class='meta-subtitle'>{subtitle}</div>",
                    unsafe_allow_html=True)
    with c_right:
        st.markdown(KKW_BOX_HTML, unsafe_allow_html=True)


all_seasons_selected = set(selected_seasons) == set(ALL_SEASONS)


# ── PAGE: ÜBERSICHT ───────────────────────────────────────────────────────────
if page == "Übersicht":
    render_header(
        "▌ REAKTOR 1 · LANGFRIST-ANALYSE",
        "Stromverbrauch Schweiz",
        "Wer treibt den Verbrauch? Die Bevölkerung wuchs von 6.75 auf 9 Mio. — "
        "vor allem durch Einwanderung. Seit 2009 stagniert der Verbrauch trotz "
        "weiter wachsender Bevölkerung. Erste Hypothese: Effizienz und mildere Winter.",
    )

    # KPIs
    bev_max    = df_filtered["Bevoelkerung_num"].dropna().max() if df_filtered["Bevoelkerung_num"].notna().any() else 0
    bev_min    = df_filtered["Bevoelkerung_num"].dropna().min() if df_filtered["Bevoelkerung_num"].notna().any() else 1
    bev_growth = (bev_max - bev_min) / bev_min * 100 if bev_min > 0 else 0
    v_growth   = (
        (df_filtered["Stromverbrauch"].iloc[-12:].mean()
         - df_filtered["Stromverbrauch"].iloc[:12].mean())
        / df_filtered["Stromverbrauch"].iloc[:12].mean() * 100
    ) if len(df_filtered) > 24 else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Bevölkerung heute",  f"{bev_max / 1_000_000:.2f} Mio")
    with c2: st.metric("Bevölkerung Δ",      f"+{bev_growth:.1f} %")
    with c3: st.metric("Verbrauch Δ",        f"+{v_growth:.1f} %")
    with c4: st.metric("Datenpunkte",        f"{len(df_filtered):,}")

    st.markdown("")

    # Fenster für gleitenden Schnitt: 1 Saison → 3, 2 → 6, 3 → 9, 4 → 12 Monate
    n_sel  = len(selected_seasons)
    window = max(1, n_sel * 3)

    if len(df_filtered) < 2:
        st.warning("Nicht genug Datenpunkte für eine Visualisierung.")
    else:
        df_trend = df_filtered.sort_values("Datum").copy()
        df_trend["Trend"] = df_trend["Stromverbrauch"].rolling(window).mean()
        df_trend = df_trend.dropna(subset=["Trend"])

        # Falls zu wenig Punkte für den gleitenden Schnitt → Rohwerte zeigen
        if len(df_trend) < 2:
            df_trend = df_filtered.sort_values("Datum").copy()
            df_trend["Trend"] = df_trend["Stromverbrauch"]

        if not all_seasons_selected:
            seasons_str = "  ".join([f"{season_icon(s)} {s}" for s in selected_seasons])
            st.info(f"Filter aktiv: {seasons_str}  ·  {window}-Monats-Trend")

        fig = animated_line(df_trend, "Datum", "Trend", color=ORANGE)

        # Bevölkerung (Jahresmittel) auf zweiter Achse
        df_bev = df_trend.dropna(subset=["Bevoelkerung_num"]).copy()
        if len(df_bev) > 1:
            df_bev_y = (df_bev.groupby("Jahr")["Bevoelkerung_num"]
                              .mean().reset_index())
            df_bev_y["Datum"] = pd.to_datetime(
                df_bev_y["Jahr"].astype(str) + "-06-15")
            fig.add_trace(go.Scatter(
                x=df_bev_y["Datum"],
                y=df_bev_y["Bevoelkerung_num"] / 1_000_000,
                mode="lines", name="Bevölkerung",
                line=dict(color=BLUE, width=2.5, shape="spline"),
                yaxis="y2",
                hovertemplate="<b>Bevölkerung</b> %{y:.2f} Mio.<extra></extra>",
            ))

        # Era-Markierungen nur bei voller Saison-Auswahl (sonst irreführend)
        if all_seasons_selected:
            for x0, x1, col, label in [
                ("1990-01-01", "2008-12-01", TEAL,  "WACHSTUM ← Bevölkerung wächst"),
                ("2009-01-01", "2025-12-01", AMBER, "SÄTTIGUNG ← trotz mehr Menschen"),
            ]:
                fig.add_vrect(
                    x0=x0, x1=x1, fillcolor=col, opacity=0.08, line_width=0,
                    annotation_text=label, annotation_position="top left",
                    annotation_font=dict(color=col, family="Inter, sans-serif", size=10),
                )

        style_fig(
            fig,
            title=f"Stromverbrauch · {window}-Monats-Trend mit Bevölkerung",
            height=520,
        )
        fig.update_layout(
            yaxis=dict(title="Stromverbrauch (GWh)", color=ORANGE, fixedrange=True),
            yaxis2=dict(title="Bevölkerung (Mio.)", color=BLUE,
                        overlaying="y", side="right", gridcolor="rgba(0,0,0,0)",
                        fixedrange=True),
        )
        st.plotly_chart(fig, use_container_width=True,
                        config={"displayModeBar": False, "scrollZoom": False})


# ── PAGE: VERBRAUCH × TEMPERATUR ──────────────────────────────────────────────
elif page == "Verbrauch × Temperatur":
    render_header(
        "▌ REAKTOR 2 · DUAL SIGNAL",
        "Verbrauch × Temperatur",
        "Werden die Winter wärmer? Die Trendlinie auf der Temperatur "
        "zeigt eine klare Erwärmung — und das passt zur Verbrauchs-Sättigung.",
    )

    temp_col = [c for c in df.columns if "emp" in c and "C" in c][0]

    df_year = df_filtered.groupby("Jahr")[
        ["Stromverbrauch", temp_col]
    ].mean().reset_index()

    if not all_seasons_selected:
        seasons_str = "  ".join([f"{season_icon(s)} {s}" for s in selected_seasons])
        st.info(f"Filter aktiv: {seasons_str} — Jahresmittel nur aus gewählten Monaten")

    df_wachstum = df_year[df_year["Jahr"] <= 2008]
    df_saett    = df_year[df_year["Jahr"] >= 2009]
    if len(df_wachstum) > 0 and len(df_saett) > 0:
        t_wachstum = df_wachstum[temp_col].mean()
        t_saett    = df_saett[temp_col].mean()
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Ø Temp · Wachstumsphase", f"{t_wachstum:.2f} °C", help="1990–2008")
        with c2: st.metric("Ø Temp · Sättigungsphase", f"{t_saett:.2f} °C", help="ab 2009")
        with c3: st.metric("Erwärmung Δ", f"{t_saett - t_wachstum:+.2f} °C")
        st.markdown("")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_year["Jahr"], y=df_year["Stromverbrauch"],
        mode="lines+markers", name="Stromverbrauch",
        line=dict(color=ORANGE, width=2.5, shape="spline"),
        marker=dict(size=7, color=ORANGE, line=dict(color=BG, width=1.5)),
        yaxis="y1",
    ))
    fig.add_trace(go.Scatter(
        x=df_year["Jahr"], y=df_year[temp_col],
        mode="lines+markers", name="Temperatur",
        line=dict(color=BLUE, width=2.5, shape="spline"),
        marker=dict(size=7, color=BLUE, line=dict(color=BG, width=1.5)),
        yaxis="y2",
    ))
    if len(df_year) > 2:
        z = np.polyfit(df_year["Jahr"], df_year[temp_col], 1)
        p = np.poly1d(z)
        fig.add_trace(go.Scatter(
            x=df_year["Jahr"], y=p(df_year["Jahr"]),
            mode="lines",
            name=f"Trend Temperatur ({z[0]:+.3f} °C/Jahr)",
            line=dict(color=AMBER, width=2, dash="dash"),
            yaxis="y2",
        ))
    fig.update_layout(
        yaxis=dict(title="Stromverbrauch",  color=ORANGE, gridcolor=SURFACE_LINE,
                   fixedrange=True),
        yaxis2=dict(title="Temperatur (°C)", color=BLUE,
                    overlaying="y", side="right", gridcolor="rgba(0,0,0,0)",
                    fixedrange=True),
        xaxis=dict(title="Jahr"),
    )
    style_fig(fig, title="Verbrauch und Temperatur · Jahresmittel + Trend", height=520)
    st.plotly_chart(fig, use_container_width=True,
                    config={"displayModeBar": False, "scrollZoom": False})


# ── PAGE: KORRELATION ─────────────────────────────────────────────────────────
elif page == "Korrelation":
    render_header(
        "▌ REAKTOR 3 · KORRELATION",
        "Temperatur und Stromverbrauch",
        "Hat sich der Zusammenhang verschoben? Vergleich zweier Perioden: "
        "1990–2008 (Wachstumsphase) gegen 2009–2025 (Sättigung). "
        "Wenn die Wolke nach unten gewandert ist, brauchen wir bei gleicher "
        "Temperatur heute weniger Strom — Hinweis auf Effizienzgewinne.",
    )

    temp_col = [c for c in df.columns if "emp" in c and "C" in c][0]

    periode = st.radio(
        "Periode",
        ["Alle", "1990–2008 (Wachstum)", "2009–2025 (Sättigung)", "Vergleich beider"],
        horizontal=True,
    )

    df_sc = df_filtered.copy()
    if periode == "1990–2008 (Wachstum)":
        df_sc = df_sc[df_sc["Jahr"] <= 2008]
    elif periode == "2009–2025 (Sättigung)":
        df_sc = df_sc[df_sc["Jahr"] >= 2009]

    Y_COL   = "Stromverbrauch_pro_Kopf"
    Y_LABEL = "Stromverbrauch pro Kopf (kWh/Monat)"

    if periode == "Vergleich beider":
        df_a = df_filtered[df_filtered["Jahr"] <= 2008].dropna(subset=[Y_COL]).copy()
        df_b = df_filtered[df_filtered["Jahr"] >= 2009].dropna(subset=[Y_COL]).copy()
        corr_a = df_a[temp_col].corr(df_a[Y_COL])
        corr_b = df_b[temp_col].corr(df_b[Y_COL])
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Pearson · 1990–2008", f"{corr_a:.3f}")
        with c2: st.metric("Pearson · 2009–2025", f"{corr_b:.3f}")
        with c3: st.metric("Ø pro Kopf Δ",
                           f"{df_b[Y_COL].mean() - df_a[Y_COL].mean():+.0f} kWh")
    else:
        df_sc = df_sc.dropna(subset=[Y_COL])
        corr  = df_sc[temp_col].corr(df_sc[Y_COL])
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Pearson",    f"{corr:.3f}")
        with c2: st.metric("Ø Temperatur", f"{df_sc[temp_col].mean():.1f} °C")
        with c3: st.metric("Ø pro Kopf", f"{df_sc[Y_COL].mean():.0f} kWh")

    st.markdown("")

    fig = go.Figure()

    if periode == "Vergleich beider":
        for label, sub, col in [
            ("1990–2008 (Wachstum)",
             df_filtered[df_filtered["Jahr"] <= 2008].dropna(subset=[Y_COL]), ORANGE),
            ("2009–2025 (Sättigung)",
             df_filtered[df_filtered["Jahr"] >= 2009].dropna(subset=[Y_COL]), BLUE),
        ]:
            fig.add_trace(go.Scatter(
                x=sub[temp_col], y=sub[Y_COL], mode="markers", name=label,
                marker=dict(size=9, color=col, opacity=0.55,
                            line=dict(color=BG, width=0.8)),
            ))
            if len(sub) > 2:
                z = np.polyfit(sub[temp_col], sub[Y_COL], 1)
                p = np.poly1d(z)
                x_line = np.linspace(sub[temp_col].min(), sub[temp_col].max(), 50)
                fig.add_trace(go.Scatter(
                    x=x_line, y=p(x_line), mode="lines",
                    name=f"Trend {label}",
                    line=dict(color=col, width=2, dash="dash"),
                ))
    else:
        for s in selected_seasons:
            sub = df_sc[df_sc["saison"] == s].dropna(subset=[Y_COL])
            fig.add_trace(go.Scatter(
                x=sub[temp_col], y=sub[Y_COL], mode="markers",
                name=f"{season_icon(s)} {s}",
                marker=dict(size=10, color=season_color(s), opacity=0.75,
                            line=dict(color=BG, width=1.2)),
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "Temp: %{x:.1f} °C<br>"
                    "pro Kopf: %{y:.0f} kWh<extra></extra>"
                ),
                text=sub["Datum"].dt.strftime("%b %Y"),
            ))
        if len(df_sc) > 2:
            z = np.polyfit(df_sc[temp_col], df_sc[Y_COL], 1)
            p = np.poly1d(z)
            x_line = np.linspace(df_sc[temp_col].min(), df_sc[temp_col].max(), 50)
            fig.add_trace(go.Scatter(
                x=x_line, y=p(x_line), mode="lines", name="Trend",
                line=dict(color=WHITE, width=1.5, dash="dot"), opacity=0.6,
            ))

    fig.update_layout(
        xaxis=dict(title="Temperatur (°C)"),
        yaxis=dict(title=Y_LABEL),
    )
    style_fig(fig, title="Temperatur · Stromverbrauch pro Kopf · Scatter", height=560)
    # Jahreszeiten-Legende nicht klickbar; bei "Vergleich beider" aber schon
    if periode != "Vergleich beider":
        fig.update_layout(legend=dict(itemclick=False, itemdoubleclick=False))
    st.plotly_chart(fig, use_container_width=True,
                    config={"displayModeBar": False, "scrollZoom": False})


# ── PAGE: EFFIZIENZ / HEIZEN ──────────────────────────────────────────────────
elif page == "Effizienz / Heizen":
    render_header(
        "▌ REAKTOR 4 · WITTERUNGSBEREINIGT",
        "Effizienz & Heizbedarf",
        "Wurden wir sparsamer — oder war es nur wärmer? Der Heizbedarf "
        "(≈ Heizgradtage aus den Temperaturdaten) rechnet den Wettereffekt heraus. "
        "Kennzahl = Stromverbrauch pro Kopf je Heizbedarf-Einheit. Sinkt sie, "
        "brauchen wir bei gleicher Kälte weniger Strom — ein echter Effizienzgewinn.",
    )

    # Nur Heizmonate (echter Heizbedarf) → Effizienz = Verbrauch/Kopf je Heizbedarf
    df_eff = df_filtered[df_filtered["Heizbedarf"] > 50].copy()
    df_eff = df_eff.dropna(subset=["Stromverbrauch_pro_Kopf", "Heizbedarf"])
    df_eff["Effizienz"] = df_eff["Stromverbrauch_pro_Kopf"] / df_eff["Heizbedarf"]

    if len(df_eff) < 2 or df_eff["Jahr"].nunique() < 2:
        st.warning(
            "Zu wenig Heizmonate im aktuellen Filter. Bitte mindestens eine kältere "
            "Jahreszeit (❄️ Winter / 🍂 Herbst / 🌸 Frühling) und einen breiteren "
            "Zeitraum auswählen."
        )
    else:
        g = (df_eff.groupby("Jahr")
                   .agg(Effizienz=("Effizienz", "mean"),
                        Heizbedarf=("Heizbedarf", "mean"),
                        ProKopf=("Stromverbrauch_pro_Kopf", "mean"))
                   .reset_index())

        # KPIs: erste vs. letzte verfügbare Dekade
        early   = g[g["Jahr"] <= g["Jahr"].min() + 9]["Effizienz"].mean()
        late    = g[g["Jahr"] >= g["Jahr"].max() - 9]["Effizienz"].mean()
        delta   = (late - early) / early * 100 if early else 0
        h_early = g[g["Jahr"] <= g["Jahr"].min() + 9]["Heizbedarf"].mean()
        h_late  = g[g["Jahr"] >= g["Jahr"].max() - 9]["Heizbedarf"].mean()

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Effizienz · frühe Jahre", f"{early:.2f}",
                      help="kWh/Kopf je Heizbedarf-Einheit")
        with c2:
            st.metric("Effizienz · letzte Jahre", f"{late:.2f}",
                      delta=f"{delta:+.1f} %", delta_color="inverse",
                      help="negativ = sparsamer bei gleicher Kälte")
        with c3:
            st.metric("Heizbedarf Δ", f"{h_late - h_early:+.0f}",
                      help="Heizgradtage: negativ = mildere Winter")
        st.markdown("")

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=g["Jahr"], y=g["Effizienz"],
            mode="lines+markers",
            name="Effizienz (Verbrauch/Kopf je Heizbedarf)",
            line=dict(color=ORANGE, width=2.5, shape="spline"),
            marker=dict(size=7, color=ORANGE, line=dict(color=BG, width=1.5)),
            hovertemplate="<b>%{x}</b><br>Effizienz: %{y:.2f}<extra></extra>",
        ))
        if len(g) > 2:
            z = np.polyfit(g["Jahr"], g["Effizienz"], 1)
            p = np.poly1d(z)
            richtung = "sparsamer" if z[0] < 0 else "ineffizienter"
            fig.add_trace(go.Scatter(
                x=g["Jahr"], y=p(g["Jahr"]), mode="lines",
                name=f"Trend ({z[0]:+.3f}/Jahr → {richtung})",
                line=dict(color=AMBER, width=2, dash="dash"),
            ))
        fig.update_layout(
            xaxis=dict(title="Jahr"),
            yaxis=dict(title="kWh/Kopf je Heizbedarf", color=ORANGE, fixedrange=True),
        )
        style_fig(fig, title="Witterungsbereinigte Effizienz · tiefer = sparsamer",
                  height=480)
        st.plotly_chart(fig, use_container_width=True,
                        config={"displayModeBar": False, "scrollZoom": False})

        st.caption(
            "Heizbedarf ≈ Heizgradtage aus den Temperaturdaten (Quelle: MeteoSchweiz / "
            "teils geschätzt). Er misst die Heiz-*notwendigkeit* durch Kälte, nicht den "
            "gemessenen Heiz-Stromverbrauch. Durch die Division wird der Wettereffekt "
            "herausgerechnet — übrig bleiben Verhaltens- und Effizienzänderungen."
        )


# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; font-family: Inter, sans-serif; "
    "color: #6b7280; font-size: 0.7rem; letter-spacing: 0.18em; "
    "text-transform: uppercase;'>"
    "Strom Schweiz · VDSS FS26 · Gruppe 4 · Energie-Edition"
    "</div>",
    unsafe_allow_html=True,
)
