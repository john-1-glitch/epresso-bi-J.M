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
  html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Inter", sans-serif;
  }
  .stApp {
    background: #FFFFFF;
  }
  [data-testid="stSidebar"] {
    background: rgba(244, 247, 245, 0.85);
    backdrop-filter: blur(20px) saturate(160%);
    -webkit-backdrop-filter: blur(20px) saturate(160%);
    border-right: 1px solid rgba(20, 83, 45, 0.10);
  }
  /* Liquid glass KPI cards */
  [data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.72);
    backdrop-filter: blur(18px) saturate(180%);
    -webkit-backdrop-filter: blur(18px) saturate(180%);
    border: 1px solid rgba(20, 83, 45, 0.14);
    border-radius: 16px;
    padding: 16px 20px;
    box-shadow: 0 8px 24px rgba(20, 83, 45, 0.06), inset 0 1px 0 rgba(255, 255, 255, 0.9);
  }
  [data-testid="stMetricLabel"] {
    color: #4B5563;
    font-weight: 500;
  }
  [data-testid="stMetricValue"] {
    color: #14532D;
    font-weight: 700;
  }
  /* Glass tabs */
  .stTabs [data-baseweb="tab-list"] {
    gap: 10px;
    background: rgba(244, 247, 245, 0.85);
    backdrop-filter: blur(14px);
    padding: 8px;
    border-radius: 16px;
    border: 1px solid rgba(20, 83, 45, 0.12);
    flex-wrap: wrap;
  }
  .stTabs [data-baseweb="tab"] {
    border-radius: 12px;
    padding: 10px 24px !important;
    min-width: 150px;
    justify-content: center;
    color: #1F2937;
    font-weight: 500;
    white-space: nowrap;
  }
  .stTabs [aria-selected="true"] {
    background: #14532D !important;
    color: #FFFFFF !important;
    box-shadow: 0 4px 12px rgba(20, 83, 45, 0.22);
  }
  .stTabs [aria-selected="true"] p {
    color: #FFFFFF !important;
    font-weight: 600 !important;
  }
  .stTabs [data-baseweb="tab-highlight"] {
    display: none;
  }
  /* Light green liquid-glass tables */
  [data-testid="stDataFrame"], [data-testid="stTable"] {
    background: rgba(220, 252, 231, 0.42);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(20, 83, 45, 0.18);
    border-radius: 16px;
    padding: 10px;
  }
  /* Glass expanders & chat cards */
  [data-testid="stExpander"], [data-testid="stChatMessage"] {
    background: rgba(255, 255, 255, 0.78);
    backdrop-filter: blur(16px) saturate(160%);
    -webkit-backdrop-filter: blur(16px) saturate(160%);
    border: 1px solid rgba(20, 83, 45, 0.12);
    border-radius: 16px;
    box-shadow: 0 4px 18px rgba(15, 23, 42, 0.04);
  }
</style>
""", unsafe_allow_html=True)

st.title('E-Presso BI Analyst')
st.caption('Revenue analysis for E-Presso stores and the website. Preloaded with default data—any file you upload takes priority.')


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


# Categorical colors in a fixed order: Dark Green (Website) & Slate (Brick & Mortar).
# Each channel keeps its color whatever the filters.
SERIES_COLORS = ['#14532D', '#64748B']
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
    k1, k2, k3 = st.columns(3)
    k1.metric('Revenue in selection', money(view_revenue))
    k2.metric('Share of all revenue', f'{view_revenue / all_revenue:.1%}' if all_revenue else 'n/a')
    k3.metric('Stores in selection', view['Store ID'].nunique())
    st.caption('Revenue is not profit: the data has no costs, so margins cannot be shown.')

    # Chart 1: is revenue growing, and in which channel?
    by_year = analytics.revenue_by_year_channel(view)
    fig = go.Figure()
    for channel, part in by_year.groupby('StoreType'):
        fig.add_trace(go.Scatter(
            x=part['Year'], y=part['Revenue'], name=channel, mode='lines+markers',
            line=dict(width=2, color=channel_color[channel]), marker=dict(size=8),
            hovertemplate=f'<b>{channel}</b><br>%{{x}}: $%{{y:,.0f}}<extra></extra>'))
    fig.update_xaxes(dtick=1)
    fig.update_yaxes(tickprefix='$', tickformat='~s', rangemode='tozero')
    st.plotly_chart(style_chart(fig, 'Revenue by year and channel'), use_container_width=True)
    table_view(by_year.rename(columns={'StoreType': 'Channel'}))

    left, right = st.columns(2)

    # Chart 2: which product categories bring in the money?
    with left:
        by_cat = analytics.category_breakdown(view).iloc[::-1]  # largest at the top
        fig = go.Figure(go.Bar(
            x=by_cat['Revenue'], y=by_cat['Category'], orientation='h',
            marker_color=BAR_COLOR, customdata=by_cat['Share'],
            text=[f'${v / 1e6:,.1f}M · {s:.0%}' for v, s in zip(by_cat['Revenue'], by_cat['Share'])],
            textposition='outside', cliponaxis=False,
            hovertemplate='<b>%{y}</b><br>$%{x:,.0f} (%{customdata:.1%} of selection)<extra></extra>'))
        fig.update_xaxes(tickprefix='$', tickformat='~s', showgrid=True,
                         gridcolor='rgba(128,128,128,0.2)')
        st.plotly_chart(style_chart(fig, 'Revenue by category'), use_container_width=True)
        table_view(by_cat.iloc[::-1])

    # Chart 3: when in the year does revenue come in?
    with right:
        by_month = analytics.revenue_by_month(view)
        fig = go.Figure(go.Bar(
            x=by_month['Month'], y=by_month['Revenue'], marker_color=BAR_COLOR,
            customdata=by_month['Share'],
            hovertemplate='<b>%{x}</b><br>$%{y:,.0f} (%{customdata:.1%} of selection)<extra></extra>'))
        fig.update_yaxes(tickprefix='$', tickformat='~s')
        st.plotly_chart(style_chart(fig, 'Revenue by month (selected years combined)'),
                        use_container_width=True)
        table_view(by_month)


tab_data, tab_revenue, tab_dash, tab_assistant = st.tabs(
    ['Data and quality', 'Revenue and merge checks', 'Dashboard', 'Assistant'])

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
            st.markdown(f"**{answer['scope']}** · *Answered by: {provider}*")
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
