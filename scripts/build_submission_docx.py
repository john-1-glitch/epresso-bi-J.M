"""Build Mey_EPresso_Submission_Package.docx with 1.5 line spacing, dark-green/orange
theme on a white background, and small italic captions beneath every table and figure."""
from pathlib import Path
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parent.parent
SHOTS = ROOT / 'docs' / 'screenshots'

DARK_GREEN = RGBColor(0x14, 0x53, 0x2D)   # #14532D
EMERALD = RGBColor(0x16, 0xA3, 0x4A)      # #16A34A
ORANGE = RGBColor(0xEA, 0x58, 0x0C)       # #EA580C
CHARCOAL = RGBColor(0x11, 0x18, 0x27)     # #111827
MUTED = RGBColor(0x4B, 0x55, 0x63)        # #4B5563
WHITE = RGBColor(0xFF, 0xFF, 0xFF)


def set_cell_bg(cell, hex_color: str):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tc_pr.append(shd)


def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = OxmlElement('w:tcMar')
    for side, val in (('top', top), ('bottom', bottom), ('left', left), ('right', right)):
        node = OxmlElement(f'w:{side}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tc_mar.append(node)
    tc_pr.append(tc_mar)


def build():
    doc = Document()

    for section in doc.sections:
        section.top_margin = Inches(0.85)
        section.bottom_margin = Inches(0.85)
        section.left_margin = Inches(0.85)
        section.right_margin = Inches(0.85)

    normal = doc.styles['Normal']
    normal.font.name = 'Calibri'
    normal.font.size = Pt(11)
    normal.font.color.rgb = CHARCOAL
    normal.paragraph_format.line_spacing = 1.5
    normal.paragraph_format.space_after = Pt(6)

    def add_para(text='', bold_prefix='', space_after=6):
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_after = Pt(space_after)
        if bold_prefix:
            rb = p.add_run(bold_prefix)
            rb.bold = True
            rb.font.color.rgb = DARK_GREEN
        if text:
            r = p.add_run(text)
            r.font.color.rgb = CHARCOAL
        return p

    def add_caption(label: str):
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(12)
        r = p.add_run(label)
        r.italic = True
        r.font.name = 'Georgia'
        r.font.size = Pt(9)
        r.font.color.rgb = MUTED
        return p

    def add_section_heading(title: str, level: int = 1):
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_before = Pt(14 if level == 1 else 10)
        p.paragraph_format.space_after = Pt(4)
        tag = p.add_run('// ')
        tag.bold = True
        tag.font.size = Pt(14 if level == 1 else 11.5)
        tag.font.color.rgb = ORANGE
        r = p.add_run(title)
        r.bold = True
        r.font.size = Pt(14 if level == 1 else 11.5)
        r.font.color.rgb = DARK_GREEN if level == 1 else CHARCOAL
        return p

    def add_styled_table(headers, rows, caption_text: str):
        t = doc.add_table(rows=1, cols=len(headers))
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.style = 'Table Grid'
        hdr = t.rows[0].cells
        for i, h in enumerate(headers):
            hdr[i].text = ''
            set_cell_bg(hdr[i], '14532D')
            set_cell_margins(hdr[i], top=110, bottom=110, left=130, right=130)
            p = hdr[i].paragraphs[0]
            p.paragraph_format.line_spacing = 1.5
            p.paragraph_format.space_after = Pt(0)
            run = p.add_run(h)
            run.bold = True
            run.font.size = Pt(9.5)
            run.font.color.rgb = WHITE

        for r_idx, row in enumerate(rows):
            cells = t.add_row().cells
            bg = 'F0FDF4' if r_idx % 2 == 0 else 'FFFFFF'
            for c_idx, val in enumerate(row):
                cells[c_idx].text = ''
                set_cell_bg(cells[c_idx], bg)
                set_cell_margins(cells[c_idx], top=90, bottom=90, left=130, right=130)
                p = cells[c_idx].paragraphs[0]
                p.paragraph_format.line_spacing = 1.5
                p.paragraph_format.space_after = Pt(0)
                run = p.add_run(str(val))
                run.font.size = Pt(9.5)
                if c_idx == 0:
                    run.bold = True
                    run.font.color.rgb = DARK_GREEN
                else:
                    run.font.color.rgb = CHARCOAL

        add_caption(caption_text)

    def add_figure(filename: str, caption_text: str, width: float = 6.1):
        img_path = SHOTS / filename
        if img_path.exists():
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(2)
            p.add_run().add_picture(str(img_path), width=Inches(width))
            add_caption(caption_text)

    # Document Header
    title_p = doc.add_paragraph()
    title_p.paragraph_format.line_spacing = 1.2
    title_p.paragraph_format.space_after = Pt(2)
    t_tag = title_p.add_run('E-PRESSO // ')
    t_tag.bold = True
    t_tag.font.size = Pt(18)
    t_tag.font.color.rgb = ORANGE
    t_main = title_p.add_run('BI ANALYST & AI AGENT SUBMISSION')
    t_main.bold = True
    t_main.font.size = Pt(18)
    t_main.font.color.rgb = DARK_GREEN

    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.line_spacing = 1.4
    sub_p.paragraph_format.space_after = Pt(10)
    sub_r = sub_p.add_run('Jonathan Mey  |  MSIM Data Analytics  |  Montana State University')
    sub_r.font.size = Pt(10)
    sub_r.font.color.rgb = MUTED

    # 1 & 2. Links
    add_section_heading('1 & 2. Live Application & GitHub Repository URLs', level=1)
    add_para('https://epreapp-bi-jm-7ysc8gurgjgzaxkaez96kq.streamlit.app/',
             bold_prefix='Live Hosted Application URL: ', space_after=2)
    add_para('https://github.com/john-1-glitch/epresso-bi-J.M',
             bold_prefix='GitHub Repository URL: ', space_after=4)
    add_para('The hosted app preloads the default E-Presso files from data/raw/ on startup. '
             'Any file uploaded in the sidebar takes priority over the default table and '
             'recalculates every metric and chart immediately without code edits or a restart.')

    # 3. Validation Evidence
    add_section_heading('3. Validation Evidence', level=1)
    add_section_heading('Power BI vs. Streamlit Comparison', level=2)
    add_styled_table(
        ['Metric', 'Power BI Result', 'Streamlit App Result', 'Match? / Explanation'],
        [
            ['Total revenue (5 years)', '$42,174,440', '$42,174,440', 'Match. All 25,200 sales rows match row for row.'],
            ['Website revenue', '$27,218,880', '$27,218,880', 'Match. StoreType = Website (store SH00).'],
            ['Brick-and-mortar revenue', '$14,955,560', '$14,955,560', 'Match. StoreType = Brick & Mortar (SH01 to SH20).'],
            ['Revenue by year', '2025: $7,181,750; 2026: $8,016,950; 2027: $8,824,720; 2028: $8,969,470; 2029: $9,181,550', 'Same five values', 'Match for every year.'],
            ['Monthly revenue pattern', 'Jan 7.74% to Nov 12.71%, Dec 25.61%', 'Same 12 monthly shares', 'Match. Monthly revenue divided by total revenue.'],
            ['Additional: Revenue by category', 'Espresso Machines $27,093,220; Beans $5,672,720; Frothers $4,329,350; Syrups $2,712,040; Accessories $2,367,110', 'Same five values', 'Match across all five product categories.'],
        ],
        'Table 1: Power BI versus Streamlit validation comparison across all five required measures.'
    )
    add_para('In Power BI, Sales links to Stores indirectly through Survey Results. In the Streamlit app, Sales joins directly to Stores on Store ID through check_merge(), keeping Survey Results separate so its store-year grain never duplicates across the 240 monthly product rows per store-year.',
             bold_prefix='Modeling comparison: ')
    add_para('scripts/independent_check.py recalculates all five measures using plain pandas and none of the app code, confirming $42,174,440.00 in total revenue and identical breakdowns.',
             bold_prefix='Independent check: ')

    add_section_heading('$1,000 Modified-Data Test', level=2)
    add_styled_table(
        ['Test Item', 'Recorded Result'],
        [
            ['Table and row identifier', 'Sales table, Sales ID S0020250101'],
            ['Date / store / channel', '2025-01-31 / SH00 Website / Website; Category Beans (C1), Product French Roast (P01)'],
            ['Original vs. Modified value', '$6,780.00 changed to $7,780.00 (+$1,000.00 in Sales_PLUS_1000_TEST.csv)'],
            ['Expected vs. Actual total revenue', 'Expected: $42,175,440.00  |  Actual: $42,175,440.00'],
            ['Charts and KPIs changed', 'Website channel rose from $27,218,880.00 to $27,219,880.00; Website 2025 rose from $3,160,230 to $3,161,230; January and Beans each rose by $1,000. Brick & Mortar and 2026 to 2029 did not change.'],
            ['Filter combinations checked', 'Changed: 2025 + Website ($3,160,230 to $3,161,230). Unchanged: 2025 + Brick & Mortar ($4,021,520); 2026 + Website ($4,784,750); SH01 ($727,080).'],
            ['Assistant before and after', 'Asking for Website revenue in 2025 returned $3,160,230.00 before and $3,161,230.00 after uploading the modified CSV.'],
            ['Code changes / Original restored?', 'No code edits or restart required (cache keys on file bytes). Clearing the upload restored $42,174,440.00.'],
        ],
        'Table 2: $1,000 modified-data test predictions and verified outcomes.'
    )

    add_figure('before_plus_1000.png',
               'Figure 1: Command Dashboard KPIs and channel trajectory on default data before the +$1,000 upload ($42,174,440.00 total revenue, $27,218,880.00 Website).')
    add_figure('after_plus_1000.png',
               'Figure 2: Command Dashboard KPIs and channel trajectory after uploading Sales_PLUS_1000_TEST.csv ($42,175,440.00 total revenue, $27,219,880.00 Website).')

    # 4. Agent Testing Evidence
    add_section_heading('4. Agent Testing Evidence', level=1)
    add_styled_table(
        ['Test Case', 'Question Asked', 'Function Used', 'Expected Behavior', 'Actual Result', 'Outcome / Revision'],
        [
            ['1. Numerical calculation', 'How much revenue did the website generate in 2028?', 'total_revenue(year=2028, channel="Website")', '$6,339,640 (15.03% of total)', '$6,339,640 across 240 rows (15.0% of total). Scope stated.', 'Pass'],
            ['2. Numerical comparison', 'Which store experienced the greatest percentage revenue decline?', 'revenue_change_by_store()', 'SH11 Chicago, $539,740 to $179,130 (-66.81%); states plainly if no store declined', 'SH11 Chicago dropped 66.81% ($539,740 to $179,130); 20 of 21 stores declined.', 'Pass (Fix 1: added year-over-year change tools)'],
            ['3. Missing information', 'Which E-Presso store is the most profitable?', 'None (refused before model call)', 'Refuse: no cost or margin data; list supported questions', 'Refused cleanly explaining revenue is not profit and listing supported topics.', 'Pass'],
            ['4. Analytical judgment', 'Does higher customer satisfaction cause higher revenue?', 'satisfaction_vs_revenue()', 'r = 0.235 across 100 store-years (5 website rows excluded); association is not causation', 'Reported r = 0.235, average score 3.4, noted 5 excluded rows, and stated correlation is not causation.', 'Pass'],
            ['5. Updated data', 'How much revenue did the website generate in 2025?', 'total_revenue(year=2025, channel="Website")', 'Before: $3,160,230; After +$1,000 upload: $3,161,230', 'Returned $3,160,230 on default data and $3,161,230 after uploading modified CSV.', 'Pass'],
            ['Extra: Fix & retest', 'Should E-Presso close its Chicago store?', 'revenue_by_year(store="Chicago")', 'Show trend (-66.81%), give no recommendation, list missing cost/lease data', 'Showed Chicago trend and stated no recommendation is supported without cost and lease data.', 'Pass (Fix 2: thinking_budget=0 + backup model retry)'],
        ],
        'Table 3: Analytical assistant evaluation across all five required test categories plus documented fixes.'
    )

    add_para('(1) Early testing routed store-decline questions to top_stores, which ranked total revenue instead of year-over-year change; adding revenue_change_by_store and revenue_change_by_channel resolved this. (2) Gemini free-tier quota (20 requests/day) and default reasoning latency caused timeouts; setting thinking_budget=0 cut response times from ~22s to ~2s, and _with_backup() retries gemini-3.5-flash-lite before falling back to the rules router.',
             bold_prefix='Documented fixes and retests: ')

    add_figure('test1_website_2028_answer.png',
               'Figure 3: Test 1 numerical calculation response (Website revenue in 2028 = $6,339,640) answered by Gemini.')
    add_figure('test1_website_2028_log.png',
               'Figure 4: Test 1 expanded tool-call log showing total_revenue arguments and raw JSON output.')
    add_figure('test2_decline_answer.png',
               'Figure 5: Test 2 numerical comparison response identifying SH11 Chicago (-66.81% decline from $539,740 to $179,130).')
    add_figure('test2_decline_log.png',
               'Figure 6: Test 2 expanded tool-call log showing revenue_change_by_store execution and store values.')
    add_figure('test3_profit_refusal.png',
               'Figure 7: Test 3 missing-information refusal for profitability question, confirming no tool was called.')
    add_figure('test4_satisfaction_causation.png',
               'Figure 8: Test 4 analytical judgment response (r = 0.235 across 100 store-years) distinguishing association from causation.')
    add_figure('test5_website_2025.png',
               'Figure 9: Test 5 baseline response for 2025 Website revenue ($3,160,230) with expanded tool-call log.')

    # 5. Reflection
    add_section_heading('5. Project Reflection', level=1)
    ref_lines = (ROOT / 'docs' / 'reflection_draft.md').read_text().strip().splitlines()
    for line in ref_lines:
        if line.startswith('# ') or not line.strip():
            continue
        add_para(line.strip())

    # 6. Contribution & Defense
    add_section_heading('6. Contribution & Project Defense Statement', level=1)
    add_para('Hayden and I originally intended to work together as a team on this project, but we could not figure out an effective workflow to collaborate cleanly on the same codebase and repository. Because I also wanted hands-on experience building and understanding the full stack myself, we decided that each of us would build and deploy our own complete system independently.')
    add_styled_table(
        ['Student', 'Main Responsibilities', 'Key Calculations & Design Decisions I Can Explain', 'Commits'],
        [
            ['Jonathan Mey',
             'Full-stack build: data loading, check_merge() validation, Power BI reconciliation, sleek modern dark-mode dashboard with preloaded data and upload priority, 10 analytical tools, Gemini function calling + rules fallback, 91 unit tests, and documentation',
             'Why Survey Results is not joined to Sales (store-year vs. product-store-month grain); how check_merge() verifies 25,200 rows and $42,174,440; how byte-keyed caching updates all figures on a +$1,000 upload; and how unsupported_numbers() blocks unverified LLM figures',
             '20+']
        ],
        'Table 4: Individual project contribution and oral defense summary.'
    )

    out_path = ROOT / 'Mey_EPresso_Submission_Package.docx'
    doc.save(str(out_path))
    print('Built:', out_path, 'size:', out_path.stat().st_size)


if __name__ == '__main__':
    build()
