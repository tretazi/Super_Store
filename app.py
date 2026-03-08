import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Superstore Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;700&family=DM+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .main { background-color: #0f1117; }
    .block-container { padding: 2rem 2.5rem 2rem 2.5rem; }

    /* SIDEBAR */
    section[data-testid="stSidebar"] {
        background: #161b27;
        border-right: 1px solid #2a3042;
    }
    section[data-testid="stSidebar"] * { color: #c9d1e0 !important; }
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stMultiSelect label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #6b7a99 !important;
        font-weight: 500;
    }

    /* TITLE */
    .dash-title {
        font-size: 1.75rem;
        font-weight: 700;
        color: #e8edf5;
        letter-spacing: -0.02em;
        margin-bottom: 0.1rem;
    }
    .dash-subtitle {
        font-size: 0.85rem;
        color: #6b7a99;
        margin-bottom: 1.5rem;
        font-family: 'DM Mono', monospace;
    }

    /* KPI CARDS */
    .kpi-card {
        background: #161b27;
        border: 1px solid #2a3042;
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
        position: relative;
        overflow: hidden;
    }
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: var(--accent);
        border-radius: 12px 12px 0 0;
    }
    .kpi-label {
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #6b7a99;
        font-weight: 500;
        margin-bottom: 0.4rem;
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #e8edf5;
        letter-spacing: -0.03em;
        line-height: 1;
    }
    .kpi-delta {
        font-size: 0.78rem;
        margin-top: 0.4rem;
        font-family: 'DM Mono', monospace;
    }
    .kpi-delta.positive { color: #34d399; }
    .kpi-delta.negative { color: #f87171; }
    .kpi-delta.neutral  { color: #6b7a99; }

    /* SECTION HEADERS */
    .section-header {
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #6b7a99;
        font-weight: 600;
        margin: 1.8rem 0 0.8rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #2a3042;
    }

    /* TABLES */
    .top-flop-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.82rem;
    }
    .top-flop-table th {
        background: #1e2535;
        color: #6b7a99;
        text-transform: uppercase;
        font-size: 0.68rem;
        letter-spacing: 0.08em;
        padding: 0.6rem 0.8rem;
        text-align: left;
        border-bottom: 1px solid #2a3042;
    }
    .top-flop-table td {
        padding: 0.55rem 0.8rem;
        color: #c9d1e0;
        border-bottom: 1px solid #1e2535;
    }
    .top-flop-table tr:hover td { background: #1e2535; }
    .badge-top {
        background: #0d2818;
        color: #34d399;
        border: 1px solid #34d399;
        border-radius: 4px;
        padding: 2px 7px;
        font-size: 0.68rem;
        font-weight: 600;
        font-family: 'DM Mono', monospace;
    }
    .badge-flop {
        background: #2d0f0f;
        color: #f87171;
        border: 1px solid #f87171;
        border-radius: 4px;
        padding: 2px 7px;
        font-size: 0.68rem;
        font-weight: 600;
        font-family: 'DM Mono', monospace;
    }
    .profit-positive { color: #34d399; font-family: 'DM Mono', monospace; }
    .profit-negative { color: #f87171; font-family: 'DM Mono', monospace; }

    /* Plotly charts background */
    .js-plotly-plot { border-radius: 12px; overflow: hidden; }

    /* Hide streamlit branding */
    #MainMenu, footer, header { visibility: hidden; }
    .stDeployButton { display: none; }
</style>
""", unsafe_allow_html=True)

# ── PLOTLY THEME ──────────────────────────────────────────────────────────────
CHART_BG    = "#161b27"
GRID_COLOR  = "#2a3042"
TEXT_COLOR  = "#c9d1e0"
ACCENT1     = "#6366f1"   # indigo
ACCENT2     = "#34d399"   # emerald
ACCENT3     = "#f59e0b"   # amber
ACCENT4     = "#f87171"   # red
REGION_COLORS = {"West": "#6366f1", "East": "#34d399", "Central": "#f59e0b", "South": "#f87171"}

def chart_layout(fig, title="", height=320):
    fig.update_layout(
        title=dict(text=title, font=dict(size=13, color=TEXT_COLOR, family="DM Sans"), x=0, pad=dict(l=4)),
        paper_bgcolor=CHART_BG,
        plot_bgcolor=CHART_BG,
        font=dict(family="DM Sans", color=TEXT_COLOR, size=11),
        height=height,
        margin=dict(l=10, r=10, t=40 if title else 10, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)", font=dict(size=11)),
        xaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR, tickfont=dict(size=10)),
        yaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR, tickfont=dict(size=10)),
    )
    return fig

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("Sample-Superstore.csv", encoding="latin1")
    df.columns = df.columns.str.strip()
    df["Order Date"] = pd.to_datetime(df["Order Date"], dayfirst=False)
    df["Ship Date"]  = pd.to_datetime(df["Ship Date"],  dayfirst=False)
    df["Year"]       = df["Order Date"].dt.year
    df["Month"]      = df["Order Date"].dt.to_period("M").astype(str)
    df["Delivery_Days"] = (df["Ship Date"] - df["Order Date"]).dt.days
    return df

df = load_data()

# ── SIDEBAR FILTERS ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔽 Filtres")
    st.markdown("---")

    years = sorted(df["Year"].unique())
    sel_years = st.multiselect("Années", years, default=years)

    regions = sorted(df["Region"].unique())
    sel_regions = st.multiselect("Régions", regions, default=regions)

    categories = sorted(df["Category"].unique())
    sel_cats = st.multiselect("Catégories", categories, default=categories)

    st.markdown("---")
    st.markdown(
        "<div style='font-size:0.72rem;color:#3d4d6b;text-align:center;font-family:DM Mono'>Superstore Dashboard<br/>Portfolio — Data Analyst</div>",
        unsafe_allow_html=True
    )

# ── FILTERED DATA ─────────────────────────────────────────────────────────────
dff = df[
    df["Year"].isin(sel_years) &
    df["Region"].isin(sel_regions) &
    df["Category"].isin(sel_cats)
]

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown('<div class="dash-title">📊 Superstore Sales Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="dash-subtitle">{len(dff):,} commandes · {len(sel_years)} an(s) · {", ".join(sel_regions)}</div>',
    unsafe_allow_html=True
)

# ── KPIs ──────────────────────────────────────────────────────────────────────
total_ca     = dff["Sales"].sum()
total_profit = dff["Profit"].sum()
marge_rate   = total_profit / total_ca if total_ca > 0 else 0
total_orders = dff["Order ID"].nunique()
avg_delivery = dff["Delivery_Days"].mean()

# YoY for KPI delta (last 2 selected years)
if len(sel_years) >= 2:
    y_last  = max(sel_years)
    y_prev  = sorted(sel_years)[-2]
    ca_last = dff[dff["Year"] == y_last]["Sales"].sum()
    ca_prev = dff[dff["Year"] == y_prev]["Sales"].sum()
    yoy = (ca_last - ca_prev) / ca_prev if ca_prev > 0 else 0
    yoy_str = f"{'▲' if yoy >= 0 else '▼'} {abs(yoy):.1%} vs {y_prev}"
    yoy_cls = "positive" if yoy >= 0 else "negative"
else:
    yoy_str = "— sélectionne 2+ années"
    yoy_cls = "neutral"

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f"""
    <div class="kpi-card" style="--accent:#6366f1">
        <div class="kpi-label">Chiffre d'affaires</div>
        <div class="kpi-value">${total_ca:,.0f}</div>
        <div class="kpi-delta {yoy_cls}">{yoy_str}</div>
    </div>""", unsafe_allow_html=True)

with k2:
    p_cls = "positive" if total_profit >= 0 else "negative"
    st.markdown(f"""
    <div class="kpi-card" style="--accent:#34d399">
        <div class="kpi-label">Profit total</div>
        <div class="kpi-value">${total_profit:,.0f}</div>
        <div class="kpi-delta {p_cls}">{'▲' if total_profit >= 0 else '▼'} Bénéfice net</div>
    </div>""", unsafe_allow_html=True)

with k3:
    m_cls = "positive" if marge_rate >= 0.12 else "negative" if marge_rate < 0.08 else "neutral"
    st.markdown(f"""
    <div class="kpi-card" style="--accent:#f59e0b">
        <div class="kpi-label">Taux de marge</div>
        <div class="kpi-value">{marge_rate:.1%}</div>
        <div class="kpi-delta {m_cls}">{'✓ Saine' if marge_rate >= 0.10 else '⚠ Attention'}</div>
    </div>""", unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-card" style="--accent:#a78bfa">
        <div class="kpi-label">Commandes uniques</div>
        <div class="kpi-value">{total_orders:,}</div>
        <div class="kpi-delta neutral">⏱ Livraison moy. {avg_delivery:.1f}j</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)

# ── ROW 1 : CA par année + CA par région ──────────────────────────────────────
st.markdown('<div class="section-header">Analyse temporelle & géographique</div>', unsafe_allow_html=True)
col1, col2 = st.columns([3, 2])

with col1:
    yearly = dff.groupby("Year").agg(Sales=("Sales","sum"), Profit=("Profit","sum")).reset_index()
    yearly["Marge %"] = yearly["Profit"] / yearly["Sales"]

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=yearly["Year"], y=yearly["Sales"], name="CA",
                         marker_color=ACCENT1, opacity=0.85), secondary_y=False)
    fig.add_trace(go.Bar(x=yearly["Year"], y=yearly["Profit"], name="Profit",
                         marker_color=ACCENT2, opacity=0.85), secondary_y=False)
    fig.add_trace(go.Scatter(x=yearly["Year"], y=yearly["Marge %"], name="Marge %",
                             mode="lines+markers", line=dict(color=ACCENT3, width=2),
                             marker=dict(size=7)), secondary_y=True)
    fig.update_layout(barmode="group")
    fig.update_yaxes(tickformat="$,.0f", secondary_y=False, gridcolor=GRID_COLOR)
    fig.update_yaxes(tickformat=".0%", secondary_y=True, showgrid=False)
    chart_layout(fig, "CA, Profit & Marge par année", height=320)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    regional = dff.groupby("Region").agg(Sales=("Sales","sum"), Profit=("Profit","sum")).reset_index()
    regional = regional.sort_values("Sales", ascending=True)
    regional["Marge"] = regional["Profit"] / regional["Sales"]
    colors = [REGION_COLORS.get(r, ACCENT1) for r in regional["Region"]]

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        y=regional["Region"], x=regional["Sales"],
        orientation="h", marker_color=colors, opacity=0.85,
        text=[f"${v:,.0f}" for v in regional["Sales"]],
        textposition="inside", textfont=dict(size=10, color="white"),
        name="CA"
    ))
    chart_layout(fig2, "CA par région", height=320)
    fig2.update_xaxes(tickformat="$,.0f")
    st.plotly_chart(fig2, use_container_width=True)

# ── ROW 2 : Catégories + Sous-catégories ─────────────────────────────────────
st.markdown('<div class="section-header">Analyse produit</div>', unsafe_allow_html=True)
col3, col4 = st.columns([2, 3])

with col3:
    cat_data = dff.groupby("Category").agg(Sales=("Sales","sum"), Profit=("Profit","sum")).reset_index()
    cat_data["Marge"] = cat_data["Profit"] / cat_data["Sales"]

    fig3 = px.pie(cat_data, values="Sales", names="Category",
                  color_discrete_sequence=[ACCENT1, ACCENT2, ACCENT3],
                  hole=0.55)
    fig3.update_traces(textposition="outside", textinfo="percent+label",
                       textfont_size=11, marker=dict(line=dict(color=CHART_BG, width=2)))
    chart_layout(fig3, "Répartition CA par catégorie", height=320)
    fig3.update_layout(showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    sub_data = dff.groupby("Sub-Category").agg(Sales=("Sales","sum"), Profit=("Profit","sum")).reset_index()
    sub_data["Marge"] = sub_data["Profit"] / sub_data["Sales"]
    sub_data = sub_data.sort_values("Profit", ascending=True)
    bar_colors = [ACCENT2 if p >= 0 else ACCENT4 for p in sub_data["Profit"]]

    fig4 = go.Figure(go.Bar(
        y=sub_data["Sub-Category"], x=sub_data["Profit"],
        orientation="h", marker_color=bar_colors, opacity=0.85,
        text=[f"${v:,.0f}" for v in sub_data["Profit"]],
        textposition="outside", textfont=dict(size=9)
    ))
    chart_layout(fig4, "Profit par sous-catégorie (vert = rentable, rouge = perte)", height=320)
    fig4.update_xaxes(tickformat="$,.0f")
    st.plotly_chart(fig4, use_container_width=True)

# ── ROW 3 : TOP / FLOP produits ───────────────────────────────────────────────
st.markdown('<div class="section-header">Top 5 & Flop 5 produits</div>', unsafe_allow_html=True)

prod_data = dff.groupby("Product Name").agg(
    Sales=("Sales","sum"),
    Profit=("Profit","sum"),
    Qty=("Quantity","sum")
).reset_index()
prod_data["Marge"] = prod_data["Profit"] / prod_data["Sales"]

top5  = prod_data.nlargest(5,  "Profit")
flop5 = prod_data.nsmallest(5, "Profit")

def render_table(data, badge_class, badge_label):
    rows = ""
    for _, r in data.iterrows():
        name = r["Product Name"][:42] + "…" if len(r["Product Name"]) > 42 else r["Product Name"]
        profit_cls = "profit-positive" if r["Profit"] >= 0 else "profit-negative"
        profit_sign = "+" if r["Profit"] >= 0 else ""
        rows += f"""
        <tr>
            <td><span class="{badge_class}">{badge_label}</span></td>
            <td>{name}</td>
            <td style="text-align:right">${r['Sales']:,.0f}</td>
            <td class="{profit_cls}" style="text-align:right">{profit_sign}${r['Profit']:,.0f}</td>
            <td style="text-align:right">{r['Marge']:.1%}</td>
        </tr>"""
    return rows

t1, t2 = st.columns(2)
with t1:
    st.markdown(f"""
    <table class="top-flop-table">
        <thead><tr><th></th><th>Produit</th><th style="text-align:right">CA</th><th style="text-align:right">Profit</th><th style="text-align:right">Marge</th></tr></thead>
        <tbody>{render_table(top5, 'badge-top', 'TOP')}</tbody>
    </table>""", unsafe_allow_html=True)

with t2:
    st.markdown(f"""
    <table class="top-flop-table">
        <thead><tr><th></th><th>Produit</th><th style="text-align:right">CA</th><th style="text-align:right">Profit</th><th style="text-align:right">Marge</th></tr></thead>
        <tbody>{render_table(flop5, 'badge-flop', 'FLOP')}</tbody>
    </table>""", unsafe_allow_html=True)

# ── ROW 4 : Évolution mensuelle ───────────────────────────────────────────────
st.markdown('<div class="section-header">Tendance mensuelle</div>', unsafe_allow_html=True)

monthly = dff.groupby("Month").agg(Sales=("Sales","sum")).reset_index().sort_values("Month")
monthly["MA3"] = monthly["Sales"].rolling(3, min_periods=1).mean()

fig5 = go.Figure()
fig5.add_trace(go.Scatter(
    x=monthly["Month"], y=monthly["Sales"],
    mode="lines", name="CA mensuel",
    line=dict(color=ACCENT1, width=1.5), opacity=0.5,
    fill="tozeroy", fillcolor="rgba(99,102,241,0.08)"
))
fig5.add_trace(go.Scatter(
    x=monthly["Month"], y=monthly["MA3"],
    mode="lines", name="Moyenne mobile 3 mois",
    line=dict(color=ACCENT3, width=2.5)
))
chart_layout(fig5, "Évolution du CA mensuel avec moyenne mobile", height=260)
fig5.update_xaxes(tickangle=45, nticks=20)
fig5.update_yaxes(tickformat="$,.0f")
st.plotly_chart(fig5, use_container_width=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:1.5rem 0 0.5rem;color:#3d4d6b;font-size:0.72rem;font-family:'DM Mono',monospace;border-top:1px solid #2a3042;margin-top:1rem">
    Superstore Sales Dashboard · Portfolio Data Analyst · Données 2014–2017
</div>
""", unsafe_allow_html=True)