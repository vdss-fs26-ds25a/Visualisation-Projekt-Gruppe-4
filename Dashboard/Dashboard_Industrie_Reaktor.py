# ============================================================
#  STROM SCHWEIZ — INDUSTRIE/ENERGIE DASHBOARD
# ============================================================
#  Parallel-Version zu Dashboard.py von Salomon und zur
#  Cyber-Edition. Schwerer Industrial-Look mit warmer
#  Orange/Amber-Palette auf Anthrazit. Seriös statt neon.
#
#  Installation (einmalig):
#      pip install streamlit pandas plotly openpyxl
#
#  Start:
#      streamlit run Dashboard_Industrie.py
#
#  Datenquelle: Data_Strom.xlsx (muss im gleichen Ordner liegen)
# ============================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# ------------------------------------------------------------
#  PAGE CONFIG
# ------------------------------------------------------------
st.set_page_config(
    page_title="STROM SCHWEIZ — Energie Dashboard",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------
#  CUSTOM CSS — Industrial / Energy Look
# ------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

    /* Main background — warm anthracite */
    .stApp {
        background:
            linear-gradient(180deg, #1c2025 0%, #181b1f 100%);
        color: #d4d8de;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #15171b;
        border-right: 1px solid #2a2e35;
    }

    section[data-testid="stSidebar"] * {
        color: #d4d8de !important;
        font-family: 'Inter', sans-serif;
    }

    /* Headers */
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

    /* Subtitle / Label */
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

    /* Metrics — clean control-room cards (both legacy + new Streamlit testids) */
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
    [data-testid="stMetricValue"] > div,
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1.85rem !important;
    }

    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] > div,
    [data-testid="stMetricLabel"] p,
    [data-testid="metric-container"] [data-testid="stMetricLabel"] {
        color: #e5e7eb !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.72rem !important;
        letter-spacing: 0.12em !important;
        text-transform: uppercase !important;
        font-weight: 600 !important;
        opacity: 1 !important;
    }

    /* Radio buttons (Reaktor 3 Period selector) */
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

    /* Plotly container */
    [data-testid="stPlotlyChart"] {
        background: #21252b;
        border: 1px solid #2a2e35;
        border-radius: 4px;
        padding: 0.75rem;
    }

    /* Info / alerts */
    .stAlert {
        background: #21252b !important;
        border-left: 3px solid #ff8c42 !important;
        color: #d4d8de !important;
        border-radius: 4px;
    }

    /* Hide default Streamlit chrome (but keep header so the sidebar toggle works) */
    #MainMenu, footer { visibility: hidden; }
    header { background: transparent !important; }

    /* Make the sidebar collapse/expand control clearly visible */
    [data-testid="collapsedControl"] {
        background: #ff8c42 !important;
        color: #1c2025 !important;
        border-radius: 4px;
        padding: 6px;
        box-shadow: 0 2px 8px rgba(255, 140, 66, 0.4);
    }
    [data-testid="collapsedControl"]:hover {
        background: #ffd166 !important;
    }
    [data-testid="collapsedControl"] svg {
        fill: #1c2025 !important;
    }

    /* Sidebar inputs */
    [data-baseweb="select"] > div {
        background: #21252b !important;
        border: 1px solid #2a2e35 !important;
        color: #ffd166 !important;
        border-radius: 3px;
    }

    [data-testid="stSlider"] [role="slider"] {
        background: #ff8c42 !important;
    }

    /* Status indicator (decorative) */
    .status-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        background: #06d6a0;
        border-radius: 50%;
        margin-right: 8px;
        box-shadow: 0 0 8px rgba(6, 214, 160, 0.6);
        animation: pulse 2s ease-in-out infinite;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    /* Section dividers */
    hr {
        border-color: #2a2e35 !important;
        margin: 1.5rem 0 !important;
    }

    /* Sidebar headers */
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

    /* Block container */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------
#  DATA LOADING
# ------------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("Data_Strom.xlsx", sheet_name=0)
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
    df = df.sort_values("Datum")
    df["Bevölkerung"] = (
        df["Bevölkerung"]
        .astype(str)
        .str.replace("’", "", regex=False)
        .str.replace(" ", "", regex=False)
        .astype(float)
    )
    # Stromverbrauch pro Kopf korrekt berechnen (kWh/Person/Monat)
    df["Stromverbrauch_pro_Kopf"] = (
        df["Stromverbrauch"] * 1_000_000 / df["Bevölkerung"]
    )
    return df


df = load_data()


# ------------------------------------------------------------
#  PALETTE
# ------------------------------------------------------------
ORANGE       = "#ff8c42"   # Primary energy accent
AMBER        = "#ffd166"   # Secondary highlight
TEAL         = "#06d6a0"   # Status / positive
RED          = "#ef476f"   # Warning / negative
BLUE         = "#118ab2"   # Cool counterpart
TEXT         = "#d4d8de"
MUTED        = "#9ca3af"
WHITE        = "#ffffff"
SURFACE      = "#21252b"
SURFACE_LINE = "#2a2e35"
BG           = "#1c2025"


# ------------------------------------------------------------
#  PLOTLY THEME
# ------------------------------------------------------------
def style_fig(fig, title=None, height=480):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=BG,
        font=dict(family="Inter, sans-serif", color=TEXT, size=13),
        title=dict(
            text=title,
            font=dict(family="Space Grotesk, sans-serif",
                      color=WHITE, size=16),
            x=0.02, xanchor="left",
        ) if title else None,
        margin=dict(l=60, r=80, t=70, b=50),
        height=height,
        hoverlabel=dict(
            bgcolor=SURFACE, bordercolor=ORANGE,
            font=dict(family="Inter, sans-serif", color=TEXT),
        ),
        xaxis=dict(
            gridcolor=SURFACE_LINE, zerolinecolor=SURFACE_LINE,
            color=MUTED, linecolor=SURFACE_LINE, showline=True,
            tickfont=dict(family="Inter, sans-serif", size=11),
        ),
        yaxis=dict(
            gridcolor=SURFACE_LINE, zerolinecolor=SURFACE_LINE,
            color=MUTED, linecolor=SURFACE_LINE, showline=True,
            tickfont=dict(family="Inter, sans-serif", size=11),
        ),
        showlegend=True,
        legend=dict(
            bgcolor=SURFACE, bordercolor=SURFACE_LINE, borderwidth=1,
            font=dict(color=TEXT), orientation="h", y=-0.15,
        ),
    )
    return fig


def animated_line(df_plot, x_col, y_col, color=ORANGE, n_frames=25):
    """Plotly line with subtle build-in animation."""
    step = max(1, len(df_plot) // n_frames)
    frames = []
    for i in range(step, len(df_plot) + 1, step):
        sub = df_plot.iloc[:i]
        frames.append(go.Frame(
            data=[
                go.Scatter(
                    x=sub[x_col], y=sub[y_col], mode="lines",
                    line=dict(color=color, width=2.5, shape="spline"),
                    name=y_col,
                ),
            ],
            name=str(i)
        ))
    frames.append(go.Frame(
        data=[
            go.Scatter(
                x=df_plot[x_col], y=df_plot[y_col], mode="lines",
                line=dict(color=color, width=2.5, shape="spline"),
                name=y_col,
            ),
        ],
    ))

    fig = go.Figure(
        data=[
            # Start with FULL data visible — replay button triggers animation
            go.Scatter(
                x=df_plot[x_col], y=df_plot[y_col],
                mode="lines",
                line=dict(color=color, width=2.5, shape="spline"),
                name=y_col,
            ),
        ],
        frames=frames,
        layout=go.Layout(
            updatemenus=[dict(
                type="buttons",
                showactive=False,
                y=1.15, x=1.0, xanchor="right",
                bgcolor=SURFACE, bordercolor=ORANGE,
                font=dict(color=ORANGE, family="Inter, sans-serif",
                          size=11),
                buttons=[dict(
                    label="↻ Replay",
                    method="animate",
                    args=[None, {
                        "frame": {"duration": 35, "redraw": True},
                        "fromcurrent": True,
                        "transition": {"duration": 0},
                    }]
                )],
            )],
        )
    )
    return fig


# ------------------------------------------------------------
#  SIDEBAR
# ------------------------------------------------------------
with st.sidebar:
    st.markdown(
        "<div style='font-family: Space Grotesk, sans-serif; "
        "font-size: 1.3rem; font-weight: 700; color: #ffffff;'>"
        "⚡ STROM <span style='color: #ff8c42;'>SCHWEIZ</span></div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='font-family: Inter, sans-serif; font-size: 0.75rem; "
        "color: #9ca3af; letter-spacing: 0.1em;'>"
        "<span class='status-dot'></span>SYSTEM ONLINE · ENERGIE-EDITION"
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    st.markdown("### MODUL")
    page = st.selectbox(
        " ",
        ["Übersicht", "Verbrauch × Temperatur", "Korrelation"],
        label_visibility="collapsed",
    )

    st.markdown("### ZEITBEREICH")
    jahr_min = int(df["Jahr"].min())
    jahr_max = int(df["Jahr"].max())
    jahr_range = st.slider(
        " ", min_value=jahr_min, max_value=jahr_max,
        value=(jahr_min, jahr_max),
        label_visibility="collapsed",
    )

    df_filtered = df[
        (df["Jahr"] >= jahr_range[0]) & (df["Jahr"] <= jahr_range[1])
    ].copy()

    st.markdown("---")
    st.markdown(
        f"<div style='font-family: Inter, sans-serif; font-size: 0.75rem;"
        f" color: #9ca3af;'>"
        f"<div style='color: #ff8c42; font-weight: 600;"
        f" letter-spacing: 0.12em; margin-bottom: 6px;'>STATUS</div>"
        f"Datenpunkte: <b style='color: #ffd166;'>{len(df_filtered)}</b><br>"
        f"Zeitraum: <b style='color: #ffd166;'>"
        f"{jahr_range[0]} – {jahr_range[1]}</b>"
        f"</div>",
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------
#  PAGE: ÜBERSICHT
# ------------------------------------------------------------
if page == "Übersicht":
    st.markdown(
        "<div class='meta-label'>▌ REAKTOR 1 · LANGFRIST-ANALYSE</div>",
        unsafe_allow_html=True,
    )
    st.title("Stromverbrauch Schweiz")
    st.markdown(
        "<div class='meta-subtitle'>"
        "Wer treibt den Verbrauch? Die Bevölkerung wuchs von 6.75 auf 9 Mio. — "
        "vor allem durch Einwanderung. Seit 2009 stagniert der Verbrauch trotz "
        "weiter wachsender Bevölkerung. Erste Hypothese: Effizienz und mildere Winter."
        "</div>",
        unsafe_allow_html=True,
    )

    # KPIs — narrativ ausgerichtet
    bev_max = df_filtered["Bevölkerung"].dropna().max() if df_filtered["Bevölkerung"].notna().any() else 0
    bev_min = df_filtered["Bevölkerung"].dropna().min() if df_filtered["Bevölkerung"].notna().any() else 0
    bev_growth = (bev_max - bev_min) / bev_min * 100 if bev_min > 0 else 0
    verbrauch_growth = (df_filtered["Stromverbrauch"].iloc[-12:].mean() - df_filtered["Stromverbrauch"].iloc[:12].mean()) / df_filtered["Stromverbrauch"].iloc[:12].mean() * 100 if len(df_filtered) > 24 else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Bevölkerung heute", f"{bev_max/1_000_000:.2f} Mio")
    with c2:
        st.metric("Bevölkerung Δ", f"+{bev_growth:.1f} %")
    with c3:
        st.metric("Verbrauch Δ", f"+{verbrauch_growth:.1f} %")
    with c4:
        st.metric("Datenpunkte", f"{len(df_filtered):,}")

    st.markdown("")

    df_plot = df_filtered.sort_values("Datum").copy()
    df_plot["Trend"] = df_plot["Stromverbrauch"].rolling(12).mean()
    df_plot = df_plot.dropna(subset=["Trend"])

    if len(df_plot) > 1:
        # Stromverbrauch-Trend
        fig = animated_line(df_plot, "Datum", "Trend", color=ORANGE)

        # Bevölkerung als zweite Linie — jahresweise aggregiert (sonst Treppe)
        df_bev = df_plot.dropna(subset=["Bevölkerung"]).copy()
        if len(df_bev) > 1:
            df_bev_y = (df_bev.groupby("Jahr")["Bevölkerung"]
                              .mean().reset_index())
            df_bev_y["Datum"] = pd.to_datetime(
                df_bev_y["Jahr"].astype(str) + "-06-15")
            fig.add_trace(go.Scatter(
                x=df_bev_y["Datum"],
                y=df_bev_y["Bevölkerung"] / 1_000_000,
                mode="lines", name="Bevölkerung",
                line=dict(color=BLUE, width=2.5, shape="spline"),
                yaxis="y2",
                hovertemplate="<b>Bevölkerung</b> %{y:.2f} Mio.<extra></extra>",
            ))

        fig.add_vrect(
            x0="1990-01-01", x1="1999-12-01",
            fillcolor=BLUE, opacity=0.08, line_width=0,
            annotation_text="STABIL", annotation_position="top left",
            annotation_font=dict(color=BLUE, family="Inter, sans-serif", size=10),
        )
        fig.add_vrect(
            x0="2000-01-01", x1="2008-12-01",
            fillcolor=TEAL, opacity=0.08, line_width=0,
            annotation_text="WACHSTUM ← Bevölkerung explodiert",
            annotation_position="top left",
            annotation_font=dict(color=TEAL, family="Inter, sans-serif", size=10),
        )
        fig.add_vrect(
            x0="2009-01-01", x1="2025-12-01",
            fillcolor=AMBER, opacity=0.08, line_width=0,
            annotation_text="SÄTTIGUNG ← trotz mehr Menschen",
            annotation_position="top left",
            annotation_font=dict(color=AMBER, family="Inter, sans-serif", size=10),
        )
        style_fig(fig, title="Stromverbrauch · 12-Monats-Trend mit Bevölkerung",
                  height=520)
        # Zweite Y-Achse aktivieren
        fig.update_layout(
            yaxis=dict(title="Stromverbrauch (GWh)", color=ORANGE),
            yaxis2=dict(title="Bevölkerung (Mio.)", color=BLUE,
                        overlaying="y", side="right",
                        gridcolor="rgba(0,0,0,0)"),
        )
        st.plotly_chart(fig, use_container_width=True,
                        config={"displayModeBar": False})


# ------------------------------------------------------------
#  PAGE: VERBRAUCH × TEMPERATUR
# ------------------------------------------------------------
elif page == "Verbrauch × Temperatur":
    st.markdown(
        "<div class='meta-label'>▌ REAKTOR 2 · DUAL SIGNAL</div>",
        unsafe_allow_html=True,
    )
    st.title("Verbrauch × Temperatur")
    st.markdown(
        "<div class='meta-subtitle'>"
        "Werden die Winter wärmer? Die Trendlinie auf der Temperatur "
        "zeigt eine klare Erwärmung — und das passt zur Verbrauchs-Sättigung."
        "</div>",
        unsafe_allow_html=True,
    )

    df_year = df_filtered.groupby("Jahr")[
        ["Stromverbrauch", "Temperatur (C°)"]
    ].mean().reset_index()

    # KPIs — Erwärmung zeigen
    if len(df_year) >= 20:
        t_old = df_year[df_year["Jahr"] < df_year["Jahr"].min() + 10]["Temperatur (C°)"].mean()
        t_new = df_year[df_year["Jahr"] > df_year["Jahr"].max() - 10]["Temperatur (C°)"].mean()
        delta_t = t_new - t_old
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Ø Temp · Ältere Dekade", f"{t_old:.2f} °C")
        with c2:
            st.metric("Ø Temp · Letzte Dekade", f"{t_new:.2f} °C")
        with c3:
            st.metric("Erwärmung Δ", f"+{delta_t:.2f} °C")
        st.markdown("")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_year["Jahr"], y=df_year["Stromverbrauch"],
        mode="lines+markers", name="Stromverbrauch",
        line=dict(color=ORANGE, width=2.5, shape="spline"),
        marker=dict(size=7, color=ORANGE,
                    line=dict(color=BG, width=1.5)),
        yaxis="y1",
    ))
    fig.add_trace(go.Scatter(
        x=df_year["Jahr"], y=df_year["Temperatur (C°)"],
        mode="lines+markers", name="Temperatur",
        line=dict(color=BLUE, width=2.5, shape="spline"),
        marker=dict(size=7, color=BLUE,
                    line=dict(color=BG, width=1.5)),
        yaxis="y2",
    ))

    # Trendlinie auf Temperatur — der Beweis für Erwärmung
    if len(df_year) > 2:
        z = np.polyfit(df_year["Jahr"], df_year["Temperatur (C°)"], 1)
        p = np.poly1d(z)
        fig.add_trace(go.Scatter(
            x=df_year["Jahr"], y=p(df_year["Jahr"]),
            mode="lines", name=f"Trend Temperatur ({z[0]:+.3f} °C/Jahr)",
            line=dict(color=AMBER, width=2, dash="dash"),
            yaxis="y2",
        ))

    fig.update_layout(
        yaxis=dict(title="Stromverbrauch", color=ORANGE,
                   gridcolor=SURFACE_LINE),
        yaxis2=dict(title="Temperatur (°C)", color=BLUE,
                    overlaying="y", side="right", gridcolor="rgba(0,0,0,0)"),
        xaxis=dict(title="Jahr"),
    )
    style_fig(fig, title="Verbrauch und Temperatur · Jahresmittel + Trend",
              height=520)
    st.plotly_chart(fig, use_container_width=True,
                    config={"displayModeBar": False})


# ------------------------------------------------------------
#  PAGE: KORRELATION
# ------------------------------------------------------------
elif page == "Korrelation":
    st.markdown(
        "<div class='meta-label'>▌ REAKTOR 3 · KORRELATION</div>",
        unsafe_allow_html=True,
    )
    st.title("Temperatur und Stromverbrauch")
    st.markdown(
        "<div class='meta-subtitle'>"
        "Hat sich der Zusammenhang verschoben? Vergleich zweier Perioden: "
        "1990–2008 (Wachstumsphase) gegen 2009–2025 (Sättigung). "
        "Wenn die Wolke nach unten gewandert ist, brauchen wir bei gleicher "
        "Temperatur heute weniger Strom — Hinweis auf Effizienzgewinne."
        "</div>",
        unsafe_allow_html=True,
    )

    # Periode auswählen
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

    def season(m):
        if m in [12, 1, 2]:
            return "Winter"
        elif m in [3, 4, 5]:
            return "Frühling"
        elif m in [6, 7, 8]:
            return "Sommer"
        return "Herbst"

    df_sc["Jahreszeit"] = df_sc["Monat_num"].apply(season)
    season_colors = {
        "Winter":   BLUE,
        "Frühling": TEAL,
        "Sommer":   AMBER,
        "Herbst":   ORANGE,
    }

    Y_COL = "Stromverbrauch_pro_Kopf"
    Y_LABEL = "Stromverbrauch pro Kopf (kWh/Monat)"

    if periode == "Vergleich beider":
        df_a = df_filtered[df_filtered["Jahr"] <= 2008].dropna(subset=[Y_COL]).copy()
        df_b = df_filtered[df_filtered["Jahr"] >= 2009].dropna(subset=[Y_COL]).copy()
        corr_a = df_a["Temperatur (C°)"].corr(df_a[Y_COL])
        corr_b = df_b["Temperatur (C°)"].corr(df_b[Y_COL])
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Pearson · 1990–2008", f"{corr_a:.3f}")
        with c2:
            st.metric("Pearson · 2009–2025", f"{corr_b:.3f}")
        with c3:
            st.metric("Ø pro Kopf Δ",
                      f"{df_b[Y_COL].mean() - df_a[Y_COL].mean():+.0f} kWh")
    else:
        df_sc = df_sc.dropna(subset=[Y_COL])
        corr = df_sc["Temperatur (C°)"].corr(df_sc[Y_COL])
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Pearson", f"{corr:.3f}")
        with c2:
            st.metric("Ø Temperatur", f"{df_sc['Temperatur (C°)'].mean():.1f} °C")
        with c3:
            st.metric("Ø pro Kopf", f"{df_sc[Y_COL].mean():.0f} kWh")

    st.markdown("")

    fig = go.Figure()

    if periode == "Vergleich beider":
        for label, sub, color in [
            ("1990–2008 (Wachstum)",
             df_filtered[df_filtered["Jahr"] <= 2008].dropna(subset=[Y_COL]),
             ORANGE),
            ("2009–2025 (Sättigung)",
             df_filtered[df_filtered["Jahr"] >= 2009].dropna(subset=[Y_COL]),
             BLUE),
        ]:
            fig.add_trace(go.Scatter(
                x=sub["Temperatur (C°)"], y=sub[Y_COL],
                mode="markers", name=label,
                marker=dict(size=9, color=color, opacity=0.55,
                            line=dict(color=BG, width=0.8)),
            ))
            z = np.polyfit(sub["Temperatur (C°)"], sub[Y_COL], 1)
            p = np.poly1d(z)
            x_line = np.linspace(sub["Temperatur (C°)"].min(),
                                 sub["Temperatur (C°)"].max(), 50)
            fig.add_trace(go.Scatter(
                x=x_line, y=p(x_line), mode="lines",
                name=f"Trend {label}",
                line=dict(color=color, width=2, dash="dash"),
            ))
    else:
        for s, c in season_colors.items():
            sub = df_sc[df_sc["Jahreszeit"] == s]
            fig.add_trace(go.Scatter(
                x=sub["Temperatur (C°)"], y=sub[Y_COL],
                mode="markers", name=s,
                marker=dict(
                    size=10, color=c, opacity=0.75,
                    line=dict(color=BG, width=1.2),
                ),
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "Temp: %{x:.1f} °C<br>"
                    "pro Kopf: %{y:.0f} kWh<extra></extra>"
                ),
                text=sub["Datum"].dt.strftime("%b %Y"),
            ))


        z = np.polyfit(df_sc["Temperatur (C°)"], df_sc[Y_COL], 1)
        p = np.poly1d(z)
        x_line = np.linspace(df_sc["Temperatur (C°)"].min(),
                             df_sc["Temperatur (C°)"].max(), 50)
        fig.add_trace(go.Scatter(
            x=x_line, y=p(x_line),
            mode="lines", name="Trend",
            line=dict(color=WHITE, width=1.5, dash="dot"),
            opacity=0.6,
        ))

    fig.update_layout(
        xaxis=dict(title="Temperatur (°C)"),
        yaxis=dict(title=Y_LABEL),
    )
    style_fig(fig, title="Temperatur · Stromverbrauch pro Kopf · Scatter",
              height=560)
    st.plotly_chart(fig, use_container_width=True,
                    config={"displayModeBar": False})


# ------------------------------------------------------------
#  FOOTER
# ------------------------------------------------------------
st.markdown("---")
st.markdown(
    "<div style='text-align:center; font-family: Inter, sans-serif; "
    "color: #6b7280; font-size: 0.7rem; letter-spacing: 0.18em; "
    "text-transform: uppercase;'>"
    "Strom Schweiz · VDSS FS26 · Gruppe 4 · Energie-Edition"
    "</div>",
    unsafe_allow_html=True,
)
