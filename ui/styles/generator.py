"""CSS generator — assembles token-driven CSS strings for injection."""

from ui.styles.tokens import tokens


def generate_css_variables() -> str:
    """Emit a :root CSS block with all design tokens as CSS custom properties."""
    r, g, b = tokens._hex_to_rgb_tuple(tokens.PRIMARY)
    ar, ag, ab = tokens._hex_to_rgb_tuple(tokens.ACCENT)
    return f"""
:root {{
  --color-primary: {tokens.PRIMARY};
  --color-primary-rgb: {r}, {g}, {b};
  --color-secondary: {tokens.SECONDARY};
  --color-accent: {tokens.ACCENT};
  --color-accent-rgb: {ar}, {ag}, {ab};
  --color-bg: {tokens.BG};
  --color-surface: {tokens.SURFACE};
  --color-surface-raised: {tokens.SURFACE_RAISED};
  --color-surface-inset: {tokens.SURFACE_INSET};
  --color-text-primary: {tokens.TEXT_PRIMARY};
  --color-text-secondary: {tokens.TEXT_SECONDARY};
  --color-text-tertiary: {tokens.TEXT_TERTIARY};
  --color-border: {tokens.BORDER};
  --color-border-strong: {tokens.BORDER_STRONG};
  --color-success: {tokens.SUCCESS};
  --color-warning: {tokens.WARNING};
  --color-error: {tokens.ERROR};
  --color-primary-dim: {tokens.primary_dim};
  --color-secondary-dim: {tokens.secondary_dim};

  --radius-sm: {tokens.RADIUS_SM};
  --radius-md: {tokens.RADIUS_MD};
  --radius-lg: {tokens.RADIUS_LG};
  --radius-xl: {tokens.RADIUS_XL};
  --radius-full: {tokens.RADIUS_FULL};

  --shadow-sm: {tokens.SHADOW_SM};
  --shadow-md: {tokens.SHADOW_MD};
  --shadow-lg: {tokens.SHADOW_LG};

  --space-1: {tokens.SPACE_1}px;
  --space-2: {tokens.SPACE_2}px;
  --space-3: {tokens.SPACE_3}px;
  --space-4: {tokens.SPACE_4}px;
  --space-5: {tokens.SPACE_5}px;
  --space-6: {tokens.SPACE_6}px;
  --space-7: {tokens.SPACE_7}px;
  --space-8: {tokens.SPACE_8}px;

  --font-heading: '{tokens.FONT_HEADING}', sans-serif;
  --font-body: '{tokens.FONT_BODY}', sans-serif;
  --font-english: '{tokens.FONT_ENGLISH}', sans-serif;
}}
"""


def generate_global_css(lang: str = "ar") -> str:
    """Generate the full global CSS for Streamlit pages."""
    direction = "rtl" if lang == "ar" else "ltr"
    font_family = f"'{tokens.FONT_HEADING}', sans-serif" if lang == "ar" else f"'{tokens.FONT_ENGLISH}', sans-serif"

    css_vars = generate_css_variables()

    return f"""
<style>
{css_vars}

/* ── Base ── */
.stApp {{
  direction: {direction};
  font-family: {font_family} !important;
  background-color: var(--color-bg) !important;
  color: var(--color-text-primary);
}}

h1, h2, h3, h4, h5, h6, p, div {{
  font-family: {font_family} !important;
}}
span:not(.material-symbols-rounded):not([data-testid="stIconMaterial"]) {{
  font-family: {font_family} !important;
}}

h1 {{ font-weight: 700; color: var(--color-text-primary); }}
h2 {{ font-weight: 600; color: var(--color-text-primary); }}
h3 {{ font-weight: 600; color: var(--color-text-secondary); }}

/* ── Animations ── */
@keyframes fadeInUp {{
  from {{ opacity: 0; transform: translateY(20px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes fadeInDown {{
  from {{ opacity: 0; transform: translateY(-20px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes fadeInScale {{
  from {{ opacity: 0; transform: scale(0.95); }}
  to {{ opacity: 1; transform: scale(1); }}
}}
@keyframes slideInLeft {{
  from {{ opacity: 0; transform: translateX(-30px); }}
  to {{ opacity: 1; transform: translateX(0); }}
}}
@keyframes slideInRight {{
  from {{ opacity: 0; transform: translateX(30px); }}
  to {{ opacity: 1; transform: translateX(0); }}
}}
@keyframes shimmer {{
  0% {{ background-position: -200% center; }}
  100% {{ background-position: 200% center; }}
}}
@keyframes pulse {{
  0%, 100% {{ opacity: 1; }}
  50% {{ opacity: 0.5; }}
}}
@keyframes glow {{
  0%, 100% {{ box-shadow: 0 0 5px var(--color-primary-dim), 0 0 10px transparent; }}
  50% {{ box-shadow: 0 0 15px var(--color-primary-dim), 0 0 30px var(--color-primary-dim); }}
}}
@keyframes borderGlow {{
  0%, 100% {{ border-color: var(--color-border); }}
  50% {{ border-color: var(--color-primary); }}
}}
@keyframes float {{
  0%, 100% {{ transform: translateY(0); }}
  50% {{ transform: translateY(-6px); }}
}}
@keyframes gradientShift {{
  0% {{ background-position: 0% 50%; }}
  50% {{ background-position: 100% 50%; }}
  100% {{ background-position: 0% 50%; }}
}}
@keyframes spin {{
  from {{ transform: rotate(0deg); }}
  to {{ transform: rotate(360deg); }}
}}

/* ── Surface Card ── */
.surface-card, div[data-testid="stVerticalBlockBorderWrapper"] {{
  background: var(--color-surface) !important;
  border: 1px solid var(--color-border) !important;
  border-radius: var(--radius-lg) !important;
  padding: var(--space-5) !important;
  margin-bottom: var(--space-4) !important;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03), var(--shadow-sm) !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
  animation: fadeInUp 0.5s ease both;
}}
.surface-card:hover, div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
  border-color: var(--color-primary) !important;
  box-shadow: 0 8px 30px rgba(var(--color-primary-rgb), 0.08), var(--shadow-md) !important;
  transform: translateY(-2px);
}}

/* ── Inputs ── */
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {{
  background-color: var(--color-surface-inset) !important;
  border: 1px solid var(--color-border) !important;
  border-radius: var(--radius-sm);
  color: var(--color-text-primary) !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}}
.stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox div[data-baseweb="select"]:focus-within {{
  border-color: var(--color-primary) !important;
  box-shadow: 0 0 0 3px var(--color-primary-dim), 0 4px 15px rgba(var(--color-primary-rgb), 0.05) !important;
  background-color: var(--color-surface) !important;
  transform: translateY(-1px);
}}

/* ── Buttons ── */
.stButton > button {{
  border-radius: var(--radius-sm);
  font-weight: 600;
  transition: all 0.2s ease-in-out;
  border: none;
  padding: 0.5rem 1.5rem;
  height: 44px;
}}

.stButton > button[kind="primary"] {{
  background: var(--color-primary) !important;
  color: #FFFFFF !important;
  box-shadow: none !important;
}}
.stButton > button[kind="primary"]:hover {{
  background: #8F1D1B !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(103, 13, 12, 0.15) !important;
}}
.stButton > button[kind="primary"]:active {{
  transform: translateY(0);
}}

.stButton > button[kind="secondary"] {{
  background: var(--color-surface-raised) !important;
  color: var(--color-text-secondary) !important;
  border: 1px solid var(--color-border) !important;
}}
.stButton > button[kind="secondary"]:hover {{
  border-color: var(--color-primary) !important;
  color: var(--color-text-primary) !important;
  background: rgba(103, 13, 12, 0.02) !important;
}}

/* ── Top Navigation Buttons Styling (6 columns layout) ── */
div[data-testid="stHorizontalBlock"]:has(> div:nth-child(6)) div.stButton > button {{
  height: 40px !important;
  border-radius: var(--radius-sm) !important;
  font-size: 0.95rem !important;
  font-weight: 600 !important;
  padding: 0 12px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  text-align: center !important;
  width: auto !important;
  margin: 0 auto !important;
  transition: all 0.2s ease-in-out !important;
  white-space: nowrap !important;
  word-break: keep-all !important;
}}

div[data-testid="stHorizontalBlock"]:has(> div:nth-child(6)) div.stButton > button * {{
  white-space: nowrap !important;
  word-break: keep-all !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  text-align: center !important;
  margin: 0 auto !important;
}}

/* Inactive Nav Buttons */
div[data-testid="stHorizontalBlock"]:has(> div:nth-child(6)) div.stButton > button[kind="secondary"] {{
  background: transparent !important;
  color: var(--color-text-secondary) !important;
  border: 1px solid transparent !important;
  width: auto !important;
  margin: 0 auto !important;
}}
div[data-testid="stHorizontalBlock"]:has(> div:nth-child(6)) div.stButton > button[kind="secondary"]:hover {{
  background: rgba(103, 13, 12, 0.05) !important;
  color: var(--color-primary) !important;
}}

/* Active Nav Button */
div[data-testid="stHorizontalBlock"]:has(> div:nth-child(6)) div.stButton > button[kind="primary"] {{
  background: transparent !important;
  color: var(--color-primary) !important;
  border: none !important;
  box-shadow: none !important;
  font-weight: 700 !important;
  border-bottom: 2px solid var(--color-primary) !important;
  border-radius: 0 !important;
  width: auto !important;
  margin: 0 auto !important;
}}

/* ── Stepper ── */
.step-container {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 6px 0 !important;
  padding: 4px var(--space-5) !important;
  animation: fadeInDown 0.6s ease both;
}}
.step-item {{
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  opacity: 0.5;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}}
.step-item.active {{ opacity: 1; transform: scale(1.05); }}
.step-item.done {{ opacity: 0.85; }}
.step-dot {{
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 2px solid var(--color-border);
  font-size: 11px;
  font-weight: 700;
  color: var(--color-text-tertiary);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}}
.step-item.active .step-dot {{
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: var(--color-bg);
  box-shadow: 0 0 0 4px var(--color-primary-dim), 0 4px 12px rgba(var(--color-primary-rgb), 0.3);
  animation: glow 2s ease-in-out infinite;
}}
.step-item.done .step-dot {{
  background: var(--color-success);
  border-color: var(--color-success);
  color: white;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.15);
}}
.step-connector {{
  flex: 1;
  height: 2px;
  background: var(--color-border);
  margin: 0 var(--space-3);
  position: relative;
  top: -10px;
  transition: all 0.5s ease;
  border-radius: 1px;
}}
.step-connector.done {{
  background: linear-gradient(90deg, var(--color-success), var(--color-primary));
  box-shadow: 0 0 6px rgba(16, 185, 129, 0.3);
}}

/* ── File Uploader ── */
.stFileUploader section {{
  background-color: var(--color-surface-inset) !important;
  border: 1px dashed var(--color-border-strong) !important;
  border-radius: var(--radius-md) !important;
  padding: 2.5rem 1rem !important;
  min-height: 150px !important;
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 1rem !important;
  transition: all 0.3s ease;
}}
.stFileUploader section:hover {{
  border-color: var(--color-primary) !important;
  background-color: var(--color-surface) !important;
}}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
  gap: 4px;
}}
.stTabs [data-baseweb="tab"] {{
  transition: all 0.3s ease;
  border-radius: var(--radius-sm) var(--radius-sm) 0 0;
}}
.stTabs [aria-selected="true"] {{
  background: var(--color-surface) !important;
  border-bottom: 2px solid var(--color-primary) !important;
}}

/* ── Utilities ── */
hr {{
  border-color: var(--color-border) !important;
  margin: var(--space-5) 0;
}}

header {{ visibility: hidden; }}
footer {{ visibility: hidden; }}

/* ── Animated Headings ── */
.stApp h1 {{
  animation: fadeInUp 0.6s ease both;
}}
.stApp h2 {{
  animation: fadeInUp 0.5s 0.1s ease both;
}}
.stApp h3 {{
  animation: fadeInUp 0.4s 0.15s ease both;
}}

/* ── Download Button ── */
.stDownloadButton > button {{
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}}
.stDownloadButton > button:hover {{
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(var(--color-primary-rgb), 0.2);
}}

/* ── Expander ── */
.streamlit-expanderHeader {{
  transition: all 0.3s ease;
  border-radius: var(--radius-sm);
}}
.streamlit-expanderHeader:hover {{
  background: var(--color-surface-raised) !important;
}}

/* ── Responsive ── */
@media (max-width: {tokens.BP_MOBILE}px) {{
  .step-container {{ padding: var(--space-3); }}
  .step-item span {{ font-size: 10px; }}
  .step-dot {{ width: 22px; height: 22px; }}
}}

/* ══════════════════════════════════════════════════════════════════════
   ── COMPREHENSIVE STREAMLIT ELEMENT THEMING ──
   ══════════════════════════════════════════════════════════════════════ */

/* ── Metric Cards ── */
div[data-testid="stMetric"] {{
  background: var(--color-surface) !important;
  border: 1px solid var(--color-border) !important;
  border-radius: var(--radius-lg) !important;
  padding: var(--space-4) var(--space-5) !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  animation: fadeInUp 0.5s ease both;
}}
div[data-testid="stMetric"]:hover {{
  border-color: var(--color-primary) !important;
  box-shadow: 0 4px 20px rgba(var(--color-primary-rgb), 0.12);
  transform: translateY(-2px);
}}
div[data-testid="stMetric"] label {{
  color: var(--color-text-tertiary) !important;
  font-size: 0.8rem !important;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  font-weight: 600 !important;
}}
div[data-testid="stMetricValue"] {{
  font-size: 1.8rem !important;
  font-weight: 800 !important;
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}}
div[data-testid="stMetricDelta"] {{
  font-weight: 600 !important;
}}
div[data-testid="stMetricDelta"] svg {{
  stroke: var(--color-success) !important;
}}

/* ── Alert Boxes (info / warning / success / error) ── */
div[data-testid="stAlert"] {{
  border-radius: var(--radius-md) !important;
  border: 1px solid var(--color-border) !important;
  backdrop-filter: blur(8px) !important;
  -webkit-backdrop-filter: blur(8px) !important;
  animation: fadeInUp 0.4s ease both;
}}
div.stAlert [data-testid="stAlertContentInfo"] {{
  background: rgba(var(--color-primary-rgb), 0.04) !important;
  border-left: 3px solid var(--color-primary) !important;
  border-color: rgba(var(--color-primary-rgb), 0.15) !important;
}}
div.stAlert [data-testid="stAlertContentWarning"] {{
  background: rgba(245, 158, 11, 0.06) !important;
  border-left: 3px solid var(--color-warning) !important;
  border-color: rgba(245, 158, 11, 0.2) !important;
}}
div.stAlert [data-testid="stAlertContentSuccess"] {{
  background: rgba(16, 185, 129, 0.06) !important;
  border-left: 3px solid var(--color-success) !important;
  border-color: rgba(16, 185, 129, 0.2) !important;
}}
div.stAlert [data-testid="stAlertContentError"] {{
  background: rgba(239, 68, 68, 0.06) !important;
  border-left: 3px solid var(--color-error) !important;
  border-color: rgba(239, 68, 68, 0.2) !important;
}}

/* ── Spinner ── */
.stSpinner > div {{
  border-top-color: var(--color-primary) !important;
}}
.stSpinner > div > span {{
  color: var(--color-text-secondary) !important;
}}

/* ── Toast Notifications ── */
div[data-testid="stToast"] {{
  background: var(--color-surface) !important;
  border: 1px solid var(--color-border) !important;
  border-radius: var(--radius-md) !important;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(var(--color-primary-rgb), 0.1) !important;
  backdrop-filter: blur(16px) !important;
  -webkit-backdrop-filter: blur(16px) !important;
  color: var(--color-text-primary) !important;
}}

/* ── Selectbox Dropdown Menus ── */
div[data-baseweb="popover"] {{
  background: var(--color-surface) !important;
  border: 1px solid var(--color-border-strong) !important;
  border-radius: var(--radius-md) !important;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6) !important;
  backdrop-filter: blur(16px) !important;
}}
ul[data-baseweb="menu"] {{
  background: var(--color-surface) !important;
}}
ul[data-baseweb="menu"] li {{
  color: var(--color-text-secondary) !important;
  transition: all 0.15s ease;
}}
ul[data-baseweb="menu"] li:hover {{
  background: rgba(var(--color-primary-rgb), 0.08) !important;
  color: var(--color-text-primary) !important;
}}
ul[data-baseweb="menu"] li[aria-selected="true"] {{
  background: rgba(var(--color-primary-rgb), 0.15) !important;
  color: var(--color-primary) !important;
}}

/* ── Number Input ── */
.stNumberInput > div {{
  transition: all 0.3s ease;
}}
.stNumberInput input {{
  background-color: var(--color-surface-inset) !important;
  border: 1px solid var(--color-border) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--color-text-primary) !important;
}}
.stNumberInput input:focus {{
  border-color: var(--color-primary) !important;
  box-shadow: 0 0 0 3px var(--color-primary-dim) !important;
}}
.stNumberInput button {{
  background: var(--color-surface-raised) !important;
  border-color: var(--color-border) !important;
  color: var(--color-text-secondary) !important;
  transition: all 0.2s ease;
}}
.stNumberInput button:hover {{
  background: var(--color-primary) !important;
  color: var(--color-bg) !important;
  border-color: var(--color-primary) !important;
}}

/* ── Radio Buttons ── */
.stRadio > div {{
  gap: var(--space-2) !important;
}}
.stRadio label {{
  transition: all 0.2s ease;
  padding: var(--space-2) var(--space-3) !important;
  border-radius: var(--radius-sm) !important;
}}
.stRadio label:hover {{
  background: rgba(var(--color-primary-rgb), 0.06);
}}
.stRadio [data-testid="stMarkdownContainer"] p {{
  color: var(--color-text-secondary) !important;
}}

/* ── Checkboxes ── */
.stCheckbox label {{
  transition: all 0.2s ease;
}}
.stCheckbox label:hover {{
  color: var(--color-text-primary) !important;
}}

/* ── Toggle Switch ── */
div[data-testid="stToggle"] label {{
  transition: all 0.2s ease;
}}

/* ── Slider ── */
.stSlider > div > div > div {{
  color: var(--color-text-secondary) !important;
}}
.stSlider [data-testid="stTickBarMin"],
.stSlider [data-testid="stTickBarMax"] {{
  color: var(--color-text-tertiary) !important;
  font-size: 0.8rem !important;
}}

/* ── Bordered Containers ── */
div[data-testid="stVerticalBlockBorderWrapper"] > div {{
  border-color: var(--color-border) !important;
  border-radius: var(--radius-lg) !important;
}}
div[data-testid="stVerticalBlockBorderWrapper"]:hover > div {{
  border-color: rgba(var(--color-primary-rgb), 0.3) !important;
}}

/* ── Custom Scrollbar ── */
::-webkit-scrollbar {{
  width: 8px;
  height: 8px;
}}
::-webkit-scrollbar-track {{
  background: var(--color-bg);
  border-radius: 4px;
}}
::-webkit-scrollbar-thumb {{
  background: var(--color-border-strong);
  border-radius: 4px;
  transition: background 0.2s ease;
}}
::-webkit-scrollbar-thumb:hover {{
  background: var(--color-primary);
}}
* {{
  scrollbar-width: thin;
  scrollbar-color: var(--color-border-strong) var(--color-bg);
}}

/* ── Tooltips / Popovers ── */
div[data-baseweb="tooltip"] {{
  background: var(--color-surface-raised) !important;
  border: 1px solid var(--color-border) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--color-text-primary) !important;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5) !important;
}}

/* ── Multiselect ── */
.stMultiSelect [data-baseweb="tag"] {{
  background: rgba(var(--color-primary-rgb), 0.15) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--color-primary) !important;
  border: 1px solid rgba(var(--color-primary-rgb), 0.25) !important;
}}
.stMultiSelect [data-baseweb="tag"] span {{
  color: var(--color-primary) !important;
}}

/* ── Dividers ── */
.stDivider {{
  border-color: var(--color-border) !important;
}}

/* ── Caption Text ── */
.stCaption, div[data-testid="stCaptionContainer"] {{
  color: var(--color-text-tertiary) !important;
  font-size: 0.8rem !important;
}}

/* ── Forms ── */
div[data-testid="stForm"] {{
  background: var(--color-surface) !important;
  border: 1px solid var(--color-border) !important;
  border-radius: var(--radius-lg) !important;
  padding: var(--space-5) !important;
}}

/* ── Sidebar (if visible) ── */
section[data-testid="stSidebar"] {{
  background: var(--color-surface) !important;
  border-right: 1px solid var(--color-border) !important;
}}
section[data-testid="stSidebar"] .stButton > button {{
  background: var(--color-surface-raised) !important;
  border: 1px solid var(--color-border) !important;
}}

/* ── Color Picker ── */
.stColorPicker > div > div {{
  border: 1px solid var(--color-border) !important;
  border-radius: var(--radius-sm) !important;
  overflow: hidden;
}}

/* ── Data Elements (tables, dataframes) ── */
.stDataFrame, .stTable {{
  border: 1px solid var(--color-border) !important;
  border-radius: var(--radius-md) !important;
  overflow: hidden;
}}
.stDataFrame thead th {{
  background: var(--color-surface-raised) !important;
  color: var(--color-text-secondary) !important;
  border-bottom: 1px solid var(--color-border) !important;
}}
.stDataFrame tbody td {{
  background: var(--color-surface) !important;
  color: var(--color-text-primary) !important;
  border-bottom: 1px solid var(--color-border) !important;
}}

/* ── Expander (enhanced) ── */
details[data-testid="stExpander"] {{
  border: 1px solid var(--color-border) !important;
  border-radius: var(--radius-md) !important;
  background: var(--color-surface) !important;
  transition: all 0.3s ease;
}}
details[data-testid="stExpander"]:hover {{
  border-color: rgba(var(--color-primary-rgb), 0.3) !important;
}}
details[data-testid="stExpander"] summary {{
  color: var(--color-text-primary) !important;
  font-weight: 600;
}}

/* ── Status elements ── */
div[data-testid="stStatusWidget"] {{
  background: var(--color-surface) !important;
  border: 1px solid var(--color-border) !important;
  border-radius: var(--radius-md) !important;
}}

/* ── Image captions ── */
div[data-testid="stImage"] + div {{
  color: var(--color-text-tertiary) !important;
  font-size: 0.8rem !important;
}}

/* ── Selection highlight color ── */
::selection {{
  background: rgba(var(--color-primary-rgb), 0.3);
  color: var(--color-text-primary);
}}

/* ── Prevent selecting text globally for a native app experience ── */
html, body, div, span, p, h1, h2, h3, h4, h5, h6, label, button, section, table, td, th {{
  -webkit-user-select: none !important;
  -moz-user-select: none !important;
  -ms-user-select: none !important;
  user-select: none !important;
}}

/* Allow selection inside input fields, textareas, code editors, and contenteditable blocks */
input, textarea, [contenteditable], [contenteditable] *, .stTextInput input, .stTextArea textarea, code, pre, span[data-baseweb="select"] {{
  -webkit-user-select: text !important;
  -moz-user-select: text !important;
  -ms-user-select: text !important;
  user-select: text !important;
}}

/* ── Placeholder text ── */
::placeholder {{
  color: var(--color-text-tertiary) !important;
  opacity: 0.7;
}}

/* ── Focus visible outlines for accessibility ── */
*:focus-visible {{
  outline: 2px solid var(--color-primary) !important;
  outline-offset: 2px;
  border-radius: var(--radius-sm);
}}
</style>
"""


def generate_component_css() -> str:
    """Generate shared CSS for iframe HTML components (outline/slide editors)."""
    return f"""
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
  font-family: var(--font-heading);
  background: var(--color-bg);
  color: var(--color-text-primary);
  overflow-x: hidden;
}}
body.ltr {{ direction: ltr; font-family: var(--font-english); }}
body.rtl {{ direction: rtl; }}

/* ── Icons ── */
.icon {{ width: 16px; height: 16px; fill: none; stroke: currentColor; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; flex-shrink: 0; }}

/* ── Buttons ── */
.btn {{
  display: inline-flex; align-items: center; justify-content: center; gap: 6px;
  padding: 10px 20px; border-radius: var(--radius-sm); border: none;
  font-weight: 600; font-size: 0.875rem; cursor: pointer; font-family: inherit;
  transition: all 0.15s ease;
}}
.btn-primary {{
  background: var(--color-primary); color: var(--color-bg);
}}
.btn-primary:hover {{ filter: brightness(1.08); box-shadow: 0 0 0 3px var(--color-primary-dim); }}
.btn-secondary {{
  background: var(--color-surface-raised); color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
}}
.btn-secondary:hover {{ border-color: var(--color-border-strong); color: var(--color-text-primary); }}
.btn-danger:hover {{ color: var(--color-error); background: rgba(239,68,68,0.08); }}

/* ── Cards ── */
.card {{
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  transition: background 0.15s, border-color 0.15s;
}}
.card:hover {{ background: var(--color-surface-raised); }}

/* ── Form elements ── */
[contenteditable] {{ outline: none; cursor: text; }}
[contenteditable]:focus {{ box-shadow: inset 0 0 0 2px var(--color-primary-dim); border-radius: var(--radius-sm); }}

/* ── Responsive ── */
@media (max-width: {tokens.BP_TABLET}px) {{
  .hide-mobile {{ display: none !important; }}
}}
@media (min-width: {tokens.BP_TABLET + 1}px) {{
  .show-mobile-only {{ display: none !important; }}
}}
</style>
"""
