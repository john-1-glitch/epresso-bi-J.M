"""Main app: loads the E-Presso tables, checks each join, shows revenue, a filtered
dashboard and the analytical assistant. Calculations live in analytics.py and the
assistant in agent.py."""
import logging
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import agent
import analytics

MAX_QUESTIONS = 15  # per-session limit for the assistant
FILE_TYPES = ['csv', 'txt', 'tsv', 'xlsx', 'xls', 'accdb', 'mdb']
RAW_DIR = Path(__file__).parent / 'data' / 'raw'
DEFAULT_FILES = {
    'sales': RAW_DIR / 'Support_EX_B_Sales.accdb',
    'stores': RAW_DIR / 'Support_EX_B_Stores.csv',
    'survey': RAW_DIR / 'Support_EX_B_Survey.xlsx',
}

logging.basicConfig(level=logging.INFO)  # merge checks are logged to the terminal

st.set_page_config(page_title='E-Presso BI Analyst', layout='wide')

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Space+Grotesk:wght@600;700&display=swap');

  @keyframes andurilReveal {
    0% { opacity: 0; transform: translateY(10px); }
    100% { opacity: 1; transform: translateY(0); }
  }
  @keyframes pulseDot {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.45; transform: scale(0.92); }
  }

  html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  }
  .stApp {
    background-color: #FFFFFF;
    background-image:
      linear-gradient(to right, rgba(20, 83, 45, 0.04) 1px, transparent 1px),
      linear-gradient(to bottom, rgba(20, 83, 45, 0.04) 1px, transparent 1px);
    background-size: 40px 40px;
  }
  [data-testid="stSidebar"] {
    background: rgba(244, 247, 245, 0.94);
    backdrop-filter: blur(20px);
    border-right: 1px solid rgba(20, 83, 45, 0.18);
  }

  /* Anduril Tactical Hero Banner */
  .anduril-hero {
    position: relative;
    background: linear-gradient(135deg, rgba(255,255,255,0.96) 0%, rgba(240,253,244,0.88) 100%);
    border: 1px solid rgba(20, 83, 45, 0.28);
    border-left: 4px solid #14532D;
    padding: 22px 28px;
    margin-bottom: 20px;
    animation: andurilReveal 0.45s cubic-bezier(0.16, 1, 0.3, 1);
    box-shadow: 0 10px 30px rgba(20, 83, 45, 0.05);
  }
  .anduril-meta {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.73rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #14532D;
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 6px;
  }
  .anduril-dot {
    width: 8px;
    height: 8px;
    background: #16A34A;
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 8px #16A34A;
    animation: pulseDot 2.2s infinite ease-in-out;
  }
  .anduril-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.0rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: #0B130E;
    margin: 0 0 4px 0;
    line-height: 1.15;
  }
  .anduril-sub {
    font-size: 0.92rem;
    color: #4B5563;
    margin: 0;
  }

  /* Anduril Full-Width Architectural Top Navigation Bar */
  .stTabs [data-baseweb="tab-list"] {
    display: grid !important;
    grid-template-columns: repeat(4, minmax(180px, 1fr)) !important;
    width: 100% !important;
    gap: 0px !important;
    background: #FFFFFF !important;
    padding: 0 !important;
    border: 1px solid rgba(20, 83, 45, 0.28) !important;
    border-radius: 4px !important;
    overflow: hidden;
    margin-bottom: 18px;
  }
  .stTabs [data-baseweb="tab"] {
    width: 100% !important;
    height: 52px !important;
    margin: 0 !important;
    padding: 0 18px !important;
    border-radius: 0 !important;
    border-right: 1px solid rgba(20, 83, 45, 0.16) !important;
    background: rgba(255, 255, 255, 0.92) !important;
    justify-content: center !important;
    transition: all 0.28s cubic-bezier(0.16, 1, 0.3, 1) !important;
  }
  .stTabs [data-baseweb="tab"]:last-child {
    border-right: none !important;
  }
  .stTabs [data-baseweb="tab"] p {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: #1F2937 !important;
    white-space: nowrap !important;
    transition: color 0.25s ease !important;
  }
  .stTabs [data-baseweb="tab"]:hover {
    background: rgba(255, 247, 237, 0.75) !important;
    box-shadow: inset 0 -2px 0 #EA580C !important;
  }
  .stTabs [aria-selected="true"] {
    background: #14532D !important;
    box-shadow: inset 0 -3px 0 #EA580C !important;
  }
  .stTabs [aria-selected="true"] p {
    color: #FFFFFF !important;
  }
  .stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {
    display: none !important;
  }

  /* Subheaders across all pages with tactical orange accent bar */
  .stApp h2, .stApp h3 {
    font-family: 'Space Grotesk', sans-serif !important;
    border-left: 3px solid #EA580C;
    padding-left: 10px;
    letter-spacing: -0.01em;
  }
  .anduril-badge-orange {
    background: rgba(234, 88, 12, 0.12);
    color: #C2410C;
    border: 1px solid rgba(234, 88, 12, 0.35);
    padding: 2px 8px;
    border-radius: 3px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.70rem;
    font-weight: 600;
  }

  /* Tactical KPI Telemetry Cards with Smooth Hover Transition */
  [data-testid="stMetric"] {
    position: relative;
    background: rgba(255, 255, 255, 0.90);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(20, 83, 45, 0.22);
    border-top: 3px solid #14532D;
    border-radius: 4px;
    padding: 16px 20px;
    box-shadow: 0 6px 20px rgba(20, 83, 45, 0.05);
    transition: transform 0.28s cubic-bezier(0.16, 1, 0.3, 1),
                box-shadow 0.28s cubic-bezier(0.16, 1, 0.3, 1),
                border-color 0.28s ease;
    animation: andurilReveal 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  }
  [data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 28px rgba(234, 88, 12, 0.10);
    border-color: rgba(234, 88, 12, 0.45);
    border-top-color: #EA580C;
  }
  [data-testid="stMetricLabel"] {
    font-family: 'JetBrains Mono', monospace !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-size: 0.72rem !important;
    color: #4B5563;
  }
  [data-testid="stMetricValue"] {
    font-family: 'Space Grotesk', sans-serif !important;
    color: #14532D;
    font-weight: 700;
  }

  /* Light-green tactical tables */
  [data-testid="stDataFrame"], [data-testid="stTable"] {
    background: rgba(220, 252, 231, 0.45);
    border: 1px solid rgba(20, 83, 45, 0.24);
    border-left: 3px solid #14532D;
    border-radius: 6px;
    padding: 10px;
    animation: andurilReveal 0.38s cubic-bezier(0.16, 1, 0.3, 1);
  }

  /* Expanders, Alerts & Chat Containers */
  [data-testid="stExpander"], [data-testid="stChatMessage"] {
    background: rgba(255, 255, 255, 0.92);
    border: 1px solid rgba(20, 83, 45, 0.18);
    border-radius: 6px;
    transition: border-color 0.25s ease, box-shadow 0.25s ease;
    animation: andurilReveal 0.35s cubic-bezier(0.16, 1, 0.3, 1);
  }
  [data-testid="stExpander"]:hover {
    border-color: #EA580C;
  }
  [data-testid="stChatMessage"] {
    border-left: 3px solid #EA580C;
  }
  [data-testid="stPlotlyChart"] {
    background: rgba(255, 255, 255, 0.92);
    border: 1px solid rgba(20, 83, 45, 0.16);
    border-radius: 6px;
    padding: 8px 12px;
    margin-bottom: 8px;
    transition: border-color 0.28s ease, box-shadow 0.28s ease;
    animation: andurilReveal 0.45s cubic-bezier(0.16, 1, 0.3, 1);
  }
  [data-testid="stPlotlyChart"]:hover {
    border-color: rgba(20, 83, 45, 0.42);
    box-shadow: 0 8px 24px rgba(20, 83, 45, 0.07);
  }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="anduril-hero">
  <div class="anduril-meta">
    <span class="anduril-dot"></span>
    <span>SYS // E-PRESSO RETAIL INTELLIGENCE</span>
    <span>·</span>
    <span>STATUS: ACTIVE TELEMETRY</span>
    <span>·</span>
    <span class="anduril-badge-orange">UPLOAD PRIORITY ARMED</span>
  </div>
  <h1 class="anduril-title">E-PRESSO // BI COMMAND &amp; ANALYTICAL AGENT</h1>
  <p class="anduril-sub">Real-time multi-channel revenue telemetry, verified schema joins, and constrained function-calling AI analysis.</p>
</div>
""", unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def cached_dataset(uploads: tuple):
    # `uploads` holds each file's bytes, so the cache is keyed on the file CONTENTS:
    # a modified file (the $1,000 test) is recalculated, never served from the cache.
    return analytics.build_dataset(uploads)


def secret(name: str, default=None):
    """Read a Streamlit secret; returns the default when there is no secrets file."""
    try:
        return st.secrets.get(name, default)
    except Exception:  # no .streamlit/secrets.toml (local run without a key)
        return default


@st.cache_resource(show_spinner=False)
def gemini_client(api_key: str):
    from google import genai
    from google.genai import types
    return genai.Client(api_key=api_key, http_options=types.HttpOptions(timeout=20_000))


def money(x: float) -> str:
    return f'${x:,.2f}'


# Categorical colors in a fixed order: Deep Tactical Green (Website) & High-Contrast Signal Amber/Orange (Brick & Mortar).
# Each channel keeps its color whatever the filters.
SERIES_COLORS = ['#14532D', '#EA580C']
BAR_COLOR = '#14532D'


def style_chart(fig: go.Figure, title: str, height: int = 360) -> go.Figure:
    fig.update_layout(
        title=dict(text=title, x=0, font=dict(size=16, color='#111827')), height=height,
        margin=dict(l=8, r=8, t=56, b=8), hovermode='closest',
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation='h', yanchor='bottom', y=1.0, xanchor='left', x=0),
        barcornerradius=6, bargap=0.35,
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor='rgba(20, 83, 45, 0.08)', zeroline=False)
    return fig


def table_view(df: pd.DataFrame, money_cols=('Revenue',), pct_cols=('Share',)):
    """Same numbers as the chart, as a table (for screen readers and exact values)."""
    out = df.copy()
    for col in money_cols:
        if col in out:
            out[col] = out[col].map(money)
    for col in pct_cols:
        if col in out:
            out[col] = out[col].map('{:.1%}'.format)
    with st.expander('View as table'):
        st.dataframe(out, hide_index=True)


with st.sidebar:
    st.header('Data')
    st.caption('Default E-Presso files load automatically. Upload any file below to override '
               'that table (your uploads always take priority).')
    uploaded = {}
    for role in analytics.REQUIRED_COLUMNS:
        label = analytics.TABLE_INFO[role][0]
        if role not in analytics.REQUIRED_TABLES:
            label += ' (optional)'
        file = st.file_uploader(label, type=FILE_TYPES, key=f'upload_{role}')
        if file is not None:
            uploaded[role] = (file.name, file.getvalue(), True)

# Build active inputs: uploaded files always win; fall back to defaults in data/raw/
active_inputs = {}
for role, (name, raw_bytes, _) in uploaded.items():
    active_inputs[role] = (name, raw_bytes, True)

for role, path in DEFAULT_FILES.items():
    if role not in active_inputs and path.exists():
        active_inputs[role] = (path.name, path.read_bytes(), False)

# If Sales was overridden with a CSV (e.g. +$1,000 test) and Categories/Products weren't
# uploaded, fall back to the default Access DB for those lookup tables.
default_accdb = DEFAULT_FILES.get('sales')
if default_accdb and default_accdb.exists():
    sales_name = active_inputs.get('sales', ('',))[0].lower()
    if not sales_name.endswith(analytics.ACCESS_EXT):
        accdb_bytes = None
        for role in ('categories', 'products'):
            if role not in active_inputs:
                if accdb_bytes is None:
                    accdb_bytes = default_accdb.read_bytes()
                active_inputs[role] = (default_accdb.name, accdb_bytes, False)

with st.sidebar:
    st.divider()
    st.caption('Active sources')
    for role in analytics.REQUIRED_COLUMNS:
        if role in active_inputs:
            name, _, is_upload = active_inputs[role]
            badge = 'Uploaded' if is_upload else 'Default'
            st.caption(f'**{analytics.TABLE_INFO[role][0]}:** {badge} (`{name}`)')

has_access = any(name.lower().endswith(analytics.ACCESS_EXT) for name, _, _ in active_inputs.values())
waiting = [analytics.TABLE_INFO[r][0] for r in analytics.REQUIRED_TABLES
           if r not in active_inputs and not (has_access and r in ('categories', 'products'))]
if waiting:
    st.info('Upload these tables in the sidebar to begin: ' + ', '.join(waiting) + '.')
    st.stop()

data = cached_dataset(tuple((role, name, raw_bytes) for role, (name, raw_bytes, _) in active_inputs.items()))
if data['errors']:
    for message in data['errors']:
        st.error(message)
    st.stop()

tables, model, reports = data['tables'], data['model'], data['merge_reports']
merges_ok = not any(r['changed'] for r in reports)


def render_dashboard():
    """Filters, KPIs and three charts. A function so that an early `return`
    (bad joins, empty selection) leaves the other tabs running."""
    if not merges_ok:
        st.error('A join changed the revenue total (see "Revenue and merge checks"). '
                 'The dashboard is hidden until the data is fixed.')
        return

    options = analytics.filter_options(model)
    channel_color = dict(zip(options['channels'], SERIES_COLORS * 4))

    # Filters: one row above the charts. Empty means "all".
    f1, f2, f3, f4 = st.columns(4)
    years = f1.multiselect('Year', options['years'], placeholder='All years', key='flt_year')
    channels = f2.multiselect('Channel', options['channels'], placeholder='All channels',
                              key='flt_channel')
    stores = f3.multiselect('Store', list(options['stores']), placeholder='All stores', key='flt_store',
                            format_func=options['stores'].get)
    categories = f4.multiselect('Category', options['categories'], placeholder='All categories',
                                key='flt_category')

    view = analytics.filter_sales(model, years, channels, stores, categories)
    scope = ' · '.join([
        ', '.join(map(str, years)) if years else 'All years',
        ', '.join(channels) if channels else 'all channels',
        f'{len(stores)} store(s)' if stores else 'all stores',
        ', '.join(categories) if categories else 'all categories',
    ])
    st.caption(f'Scope: {scope}')

    if view.empty:
        st.info('No sales match these filters. Remove a filter to see results.')
        return

    all_revenue = float(model['Revenue'].sum())
    view_revenue = float(view['Revenue'].sum())
    web_rev = float(view.loc[view['StoreType'] == 'Website', 'Revenue'].sum()) if 'StoreType' in view else 0.0
    web_share = (web_rev / view_revenue) if view_revenue else 0.0
    yr_totals = view.groupby('Year')['Revenue'].sum().sort_index()
    if len(yr_totals) >= 2 and yr_totals.iloc[0]:
        yoy_span = (yr_totals.iloc[-1] - yr_totals.iloc[0]) / yr_totals.iloc[0]
        span_label = f"{int(yr_totals.index[0])}→{int(yr_totals.index[-1])}: {yoy_span:+.1%}"
    else:
        span_label = 'Single period'

    k1, k2, k3, k4 = st.columns(4)
    k1.metric('01 // Revenue in Selection', money(view_revenue),
              delta=f'{view_revenue / all_revenue:.1%} of dataset' if all_revenue else 'n/a', delta_color='off')
    k2.metric('02 // Website Channel', money(web_rev),
              delta=f'{web_share:.1%} of selection', delta_color='off')
    k3.metric('03 // Period Trajectory', money(float(yr_totals.iloc[-1])) if len(yr_totals) else '$0.00',
              delta=span_label, delta_color='off')
    k4.metric('04 // Active Stores', f"{view['Store ID'].nunique()} / {model['Store ID'].nunique()}",
              delta=f"{len(view):,} records in scope", delta_color='off')
    st.caption('TELEMETRY NOTE // Revenue is gross top-line sales (not profit): cost and margin data are not present.')

    # Chart 1: Multi-Layer Spline Area Trajectory (Revenue by Year & Channel)
    by_year = analytics.revenue_by_year_channel(view)
    fig = go.Figure()
    color_map = {'Website': '#14532D', 'Brick & Mortar': '#EA580C'}
    fill_map = {'Website': 'rgba(22, 163, 74, 0.22)', 'Brick & Mortar': 'rgba(234, 88, 12, 0.16)'}
    for channel, part in by_year.groupby('StoreType'):
        c_hex = color_map.get(channel, channel_color.get(channel, BAR_COLOR))
        fig.add_trace(go.Scatter(
            x=part['Year'], y=part['Revenue'], name=channel, mode='lines+markers+text',
            line=dict(width=3.5, color=c_hex, shape='spline'),
            marker=dict(size=10, color='#FFFFFF', line=dict(width=3, color=c_hex)),
            fill='tozeroy', fillcolor=fill_map.get(channel, 'rgba(20, 83, 45, 0.14)'),
            text=[f'${v / 1e6:.2f}M' for v in part['Revenue']],
            textposition='top center', textfont=dict(size=11, color=c_hex),
            hovertemplate=f'<b>{channel}</b><br>%{{x}}: $%{{y:,.0f}}<extra></extra>'))
    fig.update_xaxes(dtick=1)
    fig.update_yaxes(tickprefix='$', tickformat='~s', rangemode='tozero')
    fig = style_chart(fig, '01 // CHANNEL TRAJECTORY — ANNUAL REVENUE BY CHANNEL', height=390)
    fig.update_layout(hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)
    table_view(by_year.rename(columns={'StoreType': 'Channel'}))

    left, right = st.columns(2)

    # Chart 2: Category Precision Telemetry Bar
    with left:
        by_cat = analytics.category_breakdown(view).iloc[::-1]  # largest at the top
        palette = ['#86EFAC', '#4ADE80', '#22C55E', '#16A34A', '#14532D']
        cat_colors = (palette * 3)[:len(by_cat)]
        fig = go.Figure(go.Bar(
            x=by_cat['Revenue'], y=by_cat['Category'], orientation='h',
            marker=dict(color=cat_colors, line=dict(color='#14532D', width=1)),
            customdata=by_cat['Share'],
            text=[f'${v / 1e6:,.2f}M  ({s:.1%})' for v, s in zip(by_cat['Revenue'], by_cat['Share'])],
            textposition='outside', cliponaxis=False,
            hovertemplate='<b>%{y}</b><br>$%{x:,.0f} (%{customdata:.1%} of selection)<extra></extra>'))
        fig.update_xaxes(tickprefix='$', tickformat='~s', showgrid=True,
                         gridcolor='rgba(20, 83, 45, 0.08)')
        st.plotly_chart(style_chart(fig, '02 // PRODUCT CATEGORY TELEMETRY', height=380),
                        use_container_width=True)
        table_view(by_cat.iloc[::-1])

    # Chart 3: Dual-Axis Monthly Seasonality & Cumulative Share Curve
    with right:
        by_month = analytics.revenue_by_month(view).copy()
        by_month['Cumulative Share'] = by_month['Share'].cumsum()
        month_colors = ['#EA580C' if s == by_month['Share'].max() else '#14532D'
                        for s in by_month['Share']]
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=by_month['Month'], y=by_month['Revenue'], name='Monthly Revenue',
            marker=dict(color=month_colors),
            customdata=by_month['Share'],
            hovertemplate='<b>%{x}</b><br>$%{y:,.0f} (%{customdata:.1%} of selection)<extra></extra>'))
        fig.add_trace(go.Scatter(
            x=by_month['Month'], y=by_month['Cumulative Share'], name='Cumulative Share',
            yaxis='y2', mode='lines+markers',
            line=dict(color='#EA580C', width=2.5, dash='dot'),
            marker=dict(size=7, color='#EA580C'),
            hovertemplate='<b>%{x}</b> Cumulative: %{y:.1%}<extra></extra>'))
        fig = style_chart(fig, '03 // MONTHLY SEASONALITY & CUMULATIVE CURVE', height=380)
        fig.update_yaxes(tickprefix='$', tickformat='~s')
        fig.update_layout(yaxis2=dict(
            overlaying='y', side='right', range=[0, 1.08], tickformat='.0%',
            showgrid=False, title=dict(text='Cumulative %', font=dict(size=11, color='#4B5563'))))
        st.plotly_chart(fig, use_container_width=True)
        table_view(by_month, pct_cols=('Share', 'Cumulative Share'))

    # Chart 4: Store Performance Telemetry Ranking
    store_grp = (view.groupby(['Store ID', 'City', 'Location', 'StoreType'], dropna=False)['Revenue']
                 .sum().reset_index().sort_values('Revenue', ascending=False).head(12))
    if not store_grp.empty:
        store_grp['Label'] = [analytics.store_label(r['Store ID'], r['City'], r['Location'])
                              for _, r in store_grp.iterrows()]
        store_grp['Share'] = store_grp['Revenue'] / view_revenue if view_revenue else 0.0
        rev_ord = store_grp.iloc[::-1]
        bar_cols = [channel_color.get(ch, BAR_COLOR) for ch in rev_ord['StoreType']]
        fig4 = go.Figure(go.Bar(
            x=rev_ord['Revenue'], y=rev_ord['Label'], orientation='h',
            marker=dict(color=bar_cols),
            customdata=list(zip(rev_ord['StoreType'], rev_ord['Share'])),
            text=[f"${v / 1e6:,.2f}M · {s:.1%}" for v, s in zip(rev_ord['Revenue'], rev_ord['Share'])],
            textposition='outside', cliponaxis=False,
            hovertemplate='<b>%{y}</b> (%{customdata[0]})<br>$%{x:,.0f} · %{customdata[1]:.1%}<extra></extra>'))
        fig4.update_xaxes(tickprefix='$', tickformat='~s', showgrid=True,
                          gridcolor='rgba(20, 83, 45, 0.08)')
        st.plotly_chart(style_chart(fig4, '04 // TOP PERFORMING STORES IN SELECTION (COLORED BY CHANNEL)',
                                    height=400), use_container_width=True)


tab_dash, tab_assistant, tab_revenue, tab_data = st.tabs([
    '01 // COMMAND DASHBOARD',
    '02 // ANALYTICAL AGENT',
    '03 // REVENUE & MERGE AUDIT',
    '04 // DATA & QUALITY',
])

with tab_data:
    st.subheader('Grain statements')
    st.dataframe(analytics.grain_table(tables, data['sources']), hide_index=True, use_container_width=True)

    st.subheader('Data quality')
    issues = {k: v for k, v in data['sales_issues'].items() if v}
    if issues:
        for issue, count in issues.items():
            st.warning(f'Sales: {count:,} row(s) with {issue.lower()}.')
    else:
        st.success('Sales: no blank or invalid dates or revenue, no negative revenue, '
                   'no duplicate Sales IDs.')
    if 'survey' in tables:
        n_blank = int(tables['survey']['Satisfaction'].isna().sum())
        if n_blank:
            st.info(f'Survey Results: {n_blank} row(s) have no Satisfaction score (for example, '
                    'the website is not surveyed). They are left out of averages, not counted as zero.')

    role = st.selectbox('Profile a table', list(tables),
                        format_func=lambda r: analytics.TABLE_INFO[r][0])
    df = tables[role]
    profile = analytics.profile_table(df)
    c1, c2, c3 = st.columns(3)
    c1.metric('Rows', f"{profile['rows']:,}")
    c2.metric('Columns', profile['columns'])
    c3.metric('Duplicate rows', profile['duplicate_rows'])
    st.dataframe(df.head(50))
    left, right = st.columns(2)
    left.subheader('Missing values')
    left.dataframe(profile['missing'], hide_index=True)
    right.subheader('Data types')
    right.dataframe(profile['dtypes'], hide_index=True)

with tab_revenue:
    summary = analytics.revenue_summary(tables['sales'])
    c1, c2, c3 = st.columns(3)
    c1.metric('Total revenue', money(summary['total']))
    c2.metric('Sales rows used', f"{summary['rows_used']:,}")
    c3.metric('Rows excluded (blank revenue)', f"{summary['rows_excluded']:,}")

    st.subheader('Revenue by year')
    by_year_items = list(summary['by_year'].items())
    if by_year_items:
        year_cols = st.columns(len(by_year_items))
        total_rev = summary['total'] or 0.0
        for col, (yr, val) in zip(year_cols, by_year_items):
            share_pct = f'{val / total_rev:.1%} of total' if total_rev else 'n/a'
            col.metric(str(yr), money(val), delta=share_pct, delta_color='off')
        with st.expander('View revenue by year as table'):
            st.dataframe(pd.DataFrame({
                'Year': [str(yr) for yr, _ in by_year_items],
                'Revenue': [money(val) for _, val in by_year_items],
                'Share of total': [f'{val / total_rev:.1%}' if total_rev else 'n/a'
                                   for _, val in by_year_items],
            }), hide_index=True, use_container_width=True)

    st.subheader('Merge checks')
    st.caption('Every lookup table is joined to Sales one at a time. Each join must leave '
               'the row count and the revenue total unchanged.')
    st.dataframe(pd.DataFrame([{
        'Join': r['merge'],
        'Rows before': f"{r['rows_before']:,}",
        'Rows after': f"{r['rows_after']:,}",
        'Revenue before': money(r['sum_before']),
        'Revenue after': money(r['sum_after']),
        'Unmatched rows': r['unmatched_rows'],
        'Status': 'Changed' if r['changed'] else 'OK',
    } for r in reports]), hide_index=True, use_container_width=True)
    for r in reports:
        if r['warning']:
            (st.error if r['changed'] else st.warning)(f"{r['merge']}: {r['warning']}")
    if merges_ok:
        st.success('All joins kept the same rows and the same revenue total.')

with tab_dash:
    render_dashboard()

with tab_assistant:
    api_key = secret('GEMINI_API_KEY')
    gemini_model = secret('GEMINI_MODEL', agent.GEMINI_MODEL)
    use_llm = bool(api_key) and st.toggle('Use Gemini (language-model agent)', value=True)
    if use_llm:
        st.caption(f'Mode: Gemini ({gemini_model}) agent. Gemini chooses ONE approved analytical '
                   'function through function calling, our code runs it on the loaded data, and '
                   'Gemini explains the result. Any number in its explanation that is not in '
                   'the tool result is caught and the standard answer is shown instead. If '
                   'Gemini fails or its quota runs out, the rules-based assistant answers.')
    else:
        st.caption('Mode: rules-based assistant. Keyword rules choose one approved analytical '
                   'function; the numbers come only from that function.'
                   + ('' if api_key else ' (No GEMINI_API_KEY in the app secrets.)'))
    with st.expander('What can I ask?'):
        st.markdown(agent.CAN_ANSWER + '\n\nExamples: "What was total revenue in 2029?", '
                    '"Website revenue by year", "Revenue by category for SH09", '
                    '"Top 3 stores in 2027", "Which store had the greatest percentage revenue '
                    'decline?", "Which sales channel grew the most?", "Does higher customer '
                    'satisfaction cause higher revenue?", "Should E-Presso close its Chicago '
                    'store?"')
    active = {name: st.session_state.get(f'flt_{key}') for key, name in
              (('year', 'Year'), ('channel', 'Channel'), ('store', 'Store'), ('category', 'Category'))}
    active = {k: v for k, v in active.items() if v}
    if active:
        st.info('Your dashboard filters (' + '; '.join(f"{k}: {', '.join(map(str, v))}"
                for k, v in active.items()) + ') do not apply here. The assistant answers from '
                'the full loaded dataset; name a year, channel or store in your question to '
                'narrow it.')
    st.session_state.setdefault('n_questions', 0)
    st.session_state.setdefault('history', [])
    st.caption(f"Questions used: {st.session_state['n_questions']} of {MAX_QUESTIONS}")
    for item in st.session_state['history']:
        answer = item['answer']
        with st.chat_message('user'):
            st.write(item['question'])
        with st.chat_message('assistant'):
            provider = 'Gemini' if answer['answered_by'].startswith('Gemini') else 'Rules'
            st.markdown(
                f"**{answer['scope']}** · <span class='anduril-badge-orange'>Answered by: {provider}</span>",
                unsafe_allow_html=True,
            )
            st.markdown(f"**Findings**  \n{answer['findings']}")
            if answer['interpretation'] or answer['caveats']:
                st.markdown('**Interpretation**  \n' + answer['interpretation'] + ''.join(
                    f'\n- {c}' for c in answer['caveats']))
            st.markdown(f"**Next steps**  \n{answer['next_steps']}")
            if answer['note']:
                st.warning(answer['note'])
            st.caption(f"Answered by: {answer['answered_by']}")
            with st.expander('Tool-call log'):
                if answer['tool_log']:
                    st.json(answer['tool_log'])
                else:
                    st.write('No tool was called.')
    question = st.chat_input('Ask a question about the loaded data')
    if question:
        if st.session_state['n_questions'] >= MAX_QUESTIONS:
            st.warning('Question limit reached for this session. Reload the page to start over.')
        else:
            st.session_state['n_questions'] += 1
            if use_llm:
                try:
                    client = gemini_client(api_key)
                except Exception:  # SDK missing or bad key format: answer_question falls back
                    client = None
                answer = agent.answer_question(question, model, mode='llm', llm_client=client,
                                               model=gemini_model, survey=tables.get('survey'))
            else:
                answer = agent.answer_question(question, model, mode='rules',
                                               survey=tables.get('survey'))
            st.session_state['history'].append({'question': question, 'answer': answer})
            st.rerun()
