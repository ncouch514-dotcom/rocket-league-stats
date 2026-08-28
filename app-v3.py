import random
import re
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components


# Dynamic font size helper based on character count
def get_dynamic_font_size(text):
    clean_text = re.sub(r"<[^<]+?>", "", text)
    length = len(clean_text)

    if length > 120:
        return "0.82rem"
    elif length > 95:
        return "0.92rem"
    elif length > 75:
        return "1.05rem"
    elif length > 55:
        return "1.25rem"
    else:
        return "1.45rem"


# Helper to convert hex colors to RGBA for Plotly overlays
def hex_to_rgba(hex_str, alpha=0.2):
    hex_str = hex_str.lstrip("#")
    r, g, b = tuple(int(hex_str[i : i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r}, {g}, {b}, {alpha})"


# Streamlit Page Config
st.set_page_config(
    page_title="Rocket League Newsroom | Rumble Session",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling & CSS with Mobile/Tablet Responsive Enhancements & Light/Dark Mode Support
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@600;700;900&family=Inter:wght@400;600;700&display=swap');

    /* Force default color scheme support for light/dark mode toggling */
    :root {
        color-scheme: dark light;
    }

    .stApp {
        font-family: 'Inter', sans-serif;
    }

    .main-title, .sidebar-title, .player-card-gamertag, .box-title, .sidebar-stat-value, .story-header-text {
        font-family: 'Rajdhani', sans-serif !important;
        text-transform: uppercase;
    }
    
    .story-body-text, .stat-lbl {
        font-family: 'Inter', sans-serif;
    }
    
    /* GLASSMORPHISM CARDS - Adapted for Light/Dark */
    .player-card-container, 
    .sidebar-control-card, 
    div[data-testid="stColumn"]:has([class*="card-border-"]) {
        background: var(--secondary-background-color, rgba(15, 23, 42, 0.6)) !important;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
    }

    /* Sidebar Styling */
    .sidebar-control-card {
        border-left: 4px solid #00A3FF !important;
        padding: 14px 16px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    .sidebar-title {
        font-size: 1.2rem;
        font-weight: 900;
        color: var(--text-color);
        letter-spacing: 1px;
        margin: 0;
    }
    .sidebar-subtitle {
        font-size: 0.8rem;
        color: #94a3b8;
        margin-top: 3px;
        font-weight: 500;
    }

    /* OVERHAULED FLOATING NEON PILL TAB BAR */
    div[data-testid="stTabs"] {
        width: 100% !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        display: flex !important;
        width: 100% !important;
        gap: 8px !important;
        background: var(--secondary-background-color, rgba(10, 16, 26, 0.85)) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        padding: 8px !important;
        border-radius: 14px !important;
        border: 1px solid rgba(0, 229, 255, 0.35) !important;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3), 0 0 15px rgba(0, 229, 255, 0.15) !important;
        margin-bottom: 24px !important;
        flex-wrap: wrap !important;
    }
    
    .stTabs [data-baseweb="tab"],
    .stTabs button[role="tab"] {
        flex: 1 1 0 !important;
        min-width: 110px !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        text-align: center !important;
        background: transparent !important;
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
        border-radius: 10px !important;
        color: var(--text-color) !important;
        opacity: 0.7;
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 800 !important;
        font-size: 0.9rem !important;
        padding: 10px 12px !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    .stTabs [data-baseweb="tab"]:hover,
    .stTabs button[role="tab"]:hover {
        opacity: 1;
        background: rgba(0, 229, 255, 0.18) !important;
        border-color: rgba(0, 229, 255, 0.5) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(0, 229, 255, 0.25) !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #00A3FF 0%, #00E5FF 100%) !important;
        color: #05070a !important;
        opacity: 1 !important;
        font-weight: 900 !important;
        border: 1px solid #00E5FF !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.5), inset 0 1px 1px rgba(255, 255, 255, 0.6) !important;
    }

    .stTabs [data-baseweb="tab-border"],
    .stTabs [data-testid="stTabsBorder"] {
        display: none !important;
    }
    
    /* Header Banner */
    .title-banner {
        background: linear-gradient(135deg, #00A3FF 0%, var(--background-color, #0b111a) 50%, #FF6B00 100%);
        padding: 1.8rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(128, 128, 128, 0.2);
    }
    .main-title {
        font-size: 3rem;
        font-weight: 900;
        color: #FFFFFF; /* Kept white for banner gradient contrast */
        letter-spacing: 2px;
        margin: 0;
        text-shadow: 0 0 20px rgba(0, 163, 255, 0.6), 2px 2px 8px rgba(0,0,0,0.5);
    }
    .subtitle {
        font-size: 1.15rem;
        color: #FF6B00;
        font-weight: 800;
        margin-top: 6px;
        letter-spacing: 1px;
    }

    /* UNIFIED CONNECTED FEED BAR OVERRIDES */
    div[data-testid="stHorizontalBlock"]:has(.live-ticker-box-connected) {
        gap: 0 !important;
        align-items: stretch !important;
        background: var(--secondary-background-color) !important;
        border: 1.5px solid #00A3FF !important;
        border-radius: 10px !important;
        padding: 0 !important;
        overflow: hidden !important;
        box-shadow: 0 0 20px rgba(0, 163, 255, 0.25) !important;
        margin-bottom: 1.5rem !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.live-ticker-box-connected) div[data-testid="stColumn"] {
        padding: 0 !important;
        margin: 0 !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.live-ticker-box-connected) div[data-testid="stElementContainer"] {
        margin: 0 !important;
        padding: 0 !important;
    }

    /* STYLED SHUFFLE BUTTON */
    div[data-testid="stHorizontalBlock"]:has(.live-ticker-box-connected) .stButton {
        height: 100% !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.live-ticker-box-connected) .stButton > button {
        width: 100% !important;
        background: linear-gradient(135deg, #ff2a4b 0%, #b91c1c 50%, #7f1d1d 100%) !important;
        color: #FFFFFF !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 900 !important;
        font-size: 0.95rem !important;
        letter-spacing: 1.2px !important;
        text-transform: uppercase !important;
        border: none !important;
        border-right: 1.5px solid rgba(0, 163, 255, 0.5) !important;
        border-radius: 0 !important;
        height: 48px !important;
        margin: 0 !important;
        box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.4), 0 0 12px rgba(239, 68, 68, 0.4) !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        cursor: pointer !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.live-ticker-box-connected) .stButton > button:hover {
        background: linear-gradient(135deg, #ff4d6d 0%, #dc2626 50%, #991b1b 100%) !important;
        color: #FFFFFF !important;
        box-shadow: inset 0 0 12px rgba(255, 255, 255, 0.5), 0 0 22px rgba(255, 51, 102, 0.85) !important;
        letter-spacing: 2px !important;
    }

    /* CONNECTED TICKER BOX */
    .live-ticker-box-connected {
        background: transparent !important;
        border: none !important;
        padding: 0 18px !important;
        height: 48px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }

    .live-desk-text {
        color: var(--text-color) !important;
        font-weight: 800;
        letter-spacing: 0.3px;
        line-height: 1.1;
        margin: 0;
        text-align: center !important;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        width: 100%;
    }
    .live-desk-text b {
        color: #38bdf8;
        font-weight: 900;
    }

    /* FEATURED HEADLINE CARD */
    @keyframes rotate-led-strip {
        0% { transform: translate(-50%, -50%) rotate(0deg); }
        100% { transform: translate(-50%, -50%) rotate(360deg); }
    }

    .featured-headline-card {
        position: relative;
        background: transparent;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        z-index: 1;
        overflow: hidden;
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.4);
    }

    .featured-headline-card::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 200%;
        height: 400%;
        background: conic-gradient(
            from 0deg,
            #CCFF00 0deg,
            #00E5FF 90deg,
            #FF3366 180deg,
            #FF9100 270deg,
            #CCFF00 360deg
        );
        animation: rotate-led-strip 4.5s linear infinite;
        z-index: -2;
        transform: translate(-50%, -50%);
        filter: blur(12px);
    }

    .featured-headline-card::after {
        content: '';
        position: absolute;
        inset: 3px;
        background: var(--background-color, #090e17);
        border-radius: 13px;
        z-index: -1;
    }

    /* STORY CARD BORDERS */
    div[data-testid="stColumn"]:has(.card-border-Nic),
    div[data-testid="stColumn"]:has(.card-border-Aryan),
    div[data-testid="stColumn"]:has(.card-border-Dillan),
    div[data-testid="stColumn"]:has(.card-border-Team) {
        border-radius: 16px !important;
        padding: 16px !important;
        margin-bottom: 15px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }

    div[data-testid="stColumn"]:has(.card-border-Nic) { border-top: 3px solid #00F0FF !important; }
    div[data-testid="stColumn"]:has(.card-border-Aryan) { border-top: 3px solid #FF003F !important; }
    div[data-testid="stColumn"]:has(.card-border-Dillan) { border-top: 3px solid #BF00FF !important; }
    div[data-testid="stColumn"]:has(.card-border-Team) { border-top: 3px solid #CCFF00 !important; }

    .story-header-text {
        font-size: 1.3rem;
        font-weight: 900;
        color: var(--text-color);
        margin-top: 8px;
        margin-bottom: 4px;
    }
    .story-body-text {
        color: var(--text-color);
        opacity: 0.85;
        font-size: 0.9rem;
        line-height: 1.4;
        margin-bottom: 4px;
    }

    /* GAMING SPORTS CARD STYLING */
    .player-card-container {
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
    }
    .player-card-header {
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        border-bottom: 2px solid rgba(128, 128, 128, 0.2);
        padding-bottom: 14px;
        margin-bottom: 16px;
    }
    .player-identity {
        display: flex !important;
        align-items: center !important;
        gap: 12px;
    }
    .player-avatar-badge {
        width: 46px;
        height: 46px;
        border-radius: 12px;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 1.4rem;
        font-weight: 900;
        color: #ffffff;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.4);
        flex-shrink: 0;
        font-family: 'Rajdhani', sans-serif !important;
    }
    .player-card-gamertag { font-weight: 900; color: var(--text-color); line-height: 1.1; }
    .player-card-role { font-size: 0.78rem; font-weight: 800; color: var(--text-color); opacity: 0.7; }

    /* RESPONSIVE GRID SYSTEM & MEDIA QUERIES */
    .card-grid-3 {
        display: grid !important;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)) !important;
        gap: 12px !important;
        width: 100% !important;
        margin-bottom: 8px !important;
    }
    .card-stat-box {
        background: var(--secondary-background-color, rgba(15, 23, 42, 0.75)) !important;
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
        border-radius: 12px !important;
        padding: 12px !important;
    }
    .box-title {
        font-size: 0.88rem;
        font-weight: 900;
        color: #38bdf8;
        letter-spacing: 0.8px;
        margin-bottom: 10px;
        border-bottom: 1px solid rgba(56, 189, 248, 0.2);
        padding-bottom: 4px;
    }
    .stat-row-dual {
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        margin-bottom: 6px;
    }
    .stat-lbl { font-size: 0.78rem; font-weight: 700; color: var(--text-color); opacity: 0.7; }
    .stat-v-sum { font-size: 0.88rem; font-weight: 900; color: var(--text-color); }
    .stat-v-avg { font-size: 0.8rem; font-weight: 800; color: #38bdf8; }
    .stat-v-gold { font-size: 0.88rem; font-weight: 900; color: #ffd700; }
    .stat-v-red { font-size: 0.88rem; font-weight: 900; color: #ef4444; }

    @media (max-width: 768px) {
        .main-title { font-size: 2rem !important; }
        .subtitle { font-size: 0.95rem !important; }
        .card-grid-3 { grid-template-columns: 1fr !important; }
        .stTabs [data-baseweb="tab-list"] { flex-direction: row !important; }
        .stTabs [data-baseweb="tab"] { flex: 1 1 45% !important; font-size: 0.8rem !important; }
        
        /* SHUFFLE FEED MOBILE WRAP FIX */
        .live-ticker-box-connected {
            height: auto !important;
            min-height: 48px;
            padding: 10px !important;
        }
        .live-desk-text { 
            font-size: 0.85rem !important; 
            white-space: normal !important;
            overflow: visible !important;
            text-overflow: clip !important;
            line-height: 1.3 !important;
        }
        div[data-testid="stHorizontalBlock"]:has(.live-ticker-box-connected) .stButton > button {
            height: 100% !important;
            min-height: 48px !important;
        }

        /* FIX FOR THE STACK UP TAB ON MOBILE (SIDE-BY-SIDE + SHRINK TO FIT) */
        .stack-up-grid {
            flex-direction: row !important;
            gap: 6px !important;
        }
        .stack-up-grid .player-card-container {
            padding: 8px !important;
            border-radius: 12px !important;
        }
        .stack-up-grid .player-avatar-badge {
            width: 28px !important;
            height: 28px !important;
            font-size: 1rem !important;
        }
        .stack-up-grid .player-identity {
            flex-direction: column !important;
            align-items: flex-start !important;
            gap: 4px !important;
        }
        .stack-up-grid .player-card-gamertag {
            font-size: 0.65rem !important;
        }
        .stack-up-grid .player-card-role {
            font-size: 0.55rem !important;
        }
        .stack-up-grid .box-title {
            font-size: 0.6rem !important;
            margin-bottom: 6px !important;
        }
        .stack-up-grid .stat-lbl {
            font-size: 0.5rem !important;
        }
        .stack-up-grid .stat-v-sum, .stack-up-grid .stat-v-gold, .stack-up-grid .stat-v-red {
            font-size: 0.6rem !important;
        }
        .stack-up-grid .stat-v-avg {
            font-size: 0.5rem !important;
        }
        /* Scale down the points pill to fit better on mobile */
        .stack-up-grid span[style*="background: rgba(255, 215, 0, 0.15)"] {
            font-size: 0.55rem !important;
            padding: 2px 4px !important;
        }
    }
</style>
""",
    unsafe_allow_html=True,
)


# SIMPLIFIED, CLEAN CHART THEME helper (Removed cartesian axis calls to prevent 'undefined' text)
def apply_balanced_chart_theme(fig):
    fig.update_layout(
        font=dict(color="#94a3b8", family="Inter, sans-serif", size=10),
        title_font=dict(
            color="#FFFFFF", size=12, family="Rajdhani, sans-serif", weight="bold"
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        dragmode=False,
        hovermode="closest",
        hoverlabel=dict(
            bgcolor="#0f172a",
            font_size=11,
            font_color="#FFFFFF",
            bordercolor="rgba(255,255,255,0.1)",
        ),
        margin=dict(l=20, r=20, t=35, b=20),
        showlegend=False,
    )
    return fig


@st.cache_data
def parse_uploaded_file(file):
    """Parses uploaded CSV, Excel, JSON, Parquet, Text, or Image files into a Pandas DataFrame."""
    try:
        fname = file.name.lower()
        if fname.endswith(".csv"):
            return pd.read_csv(file)
        elif fname.endswith((".tsv", ".txt")):
            try:
                return pd.read_csv(file, sep=None, engine="python")
            except Exception:
                return pd.read_csv(file)
        elif fname.endswith((".xlsx", ".xls", ".xlsm", ".xlsb")):
            return pd.read_excel(file)
        elif fname.endswith(".json"):
            return pd.read_json(file)
        elif fname.endswith(".parquet"):
            return pd.read_parquet(file)
        elif fname.endswith((".png", ".jpg", ".jpeg", ".webp", ".bmp")):
            try:
                from PIL import Image
                import pytesseract
                img = Image.open(file)
                text = pytesseract.image_to_string(img)
                lines = [line.strip() for line in text.split("\n") if line.strip()]
                data_dict = {}
                for line in lines:
                    parts = re.split(r'[:,\t]+', line)
                    if len(parts) >= 2:
                        key = parts[0].strip()
                        val = pd.to_numeric(parts[1].strip(), errors="ignore")
                        data_dict[key] = [val]
                if data_dict:
                    return pd.DataFrame(data_dict)
            except Exception:
                pass
            st.warning(f"Uploaded image '{file.name}' received. To auto-extract metrics from images, ensure readable text or OCR support.")
            return None
        else:
            return pd.read_csv(file)
    except Exception as e:
        st.error(f"Error reading file '{file.name}': {e}")
        return None

# GLOBAL SHARED STATE (For Sessions)
@st.cache_resource
def get_shared_state():
    return {"folders": {}, "active_sessions": set()}

shared_state = get_shared_state()


# Helper callback function to toggle session state cleanly without double rerun crashes
def toggle_session_state(folder_name, session_name):
    key = f"chk_{folder_name}_{session_name}"
    if st.session_state.get(key, False):
        shared_state["active_sessions"].add((folder_name, session_name))
    else:
        shared_state["active_sessions"].discard((folder_name, session_name))


# ==========================================
# 🎛️ SESSION CONTROLS (COLLAPSIBLE TAB)
# ==========================================
st.sidebar.markdown(
    """
    <div class="sidebar-control-card">
        <div class="sidebar-title">Session Controls</div>
        <div class="sidebar-subtitle">Command Center & Analytics</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- 1. CREATE NEW SESSION (FOLDER) ---
st.sidebar.markdown("**Create New Session**")
with st.sidebar.form("new_session_form", clear_on_submit=True):
    col_f1, col_f2 = st.columns([2.5, 1], vertical_alignment="bottom")
    new_folder_name = col_f1.text_input(
        "New Session Name", 
        label_visibility="collapsed", 
        placeholder="Name..."
    )
    add_submitted = col_f2.form_submit_button("Add", use_container_width=True)
    if add_submitted and new_folder_name.strip():
        clean_name = new_folder_name.strip()
        if clean_name not in shared_state["folders"]:
            shared_state["folders"][clean_name] = {}
            st.rerun()

st.sidebar.divider()

# --- 2. SESSIONS (ORGANIZATION & TOGGLES) ---
st.sidebar.markdown("### 📂 Sessions")

has_data = len(shared_state["folders"]) > 0

if has_data:
    for folder_name, files_dict in list(shared_state["folders"].items()):
        with st.sidebar.expander(f"📁 {folder_name}", expanded=True):
            st.caption("Drag & Drop match files here:")
            uploaded_files = st.file_uploader(
                f"Upload to {folder_name}",
                accept_multiple_files=True,
                label_visibility="collapsed",
                key=f"up_{folder_name}"
            )
            
            if uploaded_files:
                for file in uploaded_files:
                    raw_name = file.name.rsplit(".", 1)[0].replace("_", " ").replace("-", " ")
                    session_name = raw_name.strip().title()
                    
                    if session_name not in shared_state["folders"][folder_name]:
                        parsed_df = parse_uploaded_file(file)
                        if parsed_df is not None:
                            shared_state["folders"][folder_name][session_name] = parsed_df

            if not files_dict:
                st.caption("No files uploaded yet.")
                if st.button("🗑️ Delete Session", key=f"del_f_{folder_name}", use_container_width=True):
                    del shared_state["folders"][folder_name]
                    st.rerun()
            else:
                st.divider()
                
                for session_name in list(files_dict.keys()):
                    col_check, col_del = st.columns([0.75, 0.25], vertical_alignment="center")
                    
                    is_active = (folder_name, session_name) in shared_state["active_sessions"]
                    
                    col_check.checkbox(
                        session_name,
                        value=is_active,
                        key=f"chk_{folder_name}_{session_name}",
                        on_change=toggle_session_state,
                        args=(folder_name, session_name)
                    )

                    if col_del.button("🗑️", key=f"del_{folder_name}_{session_name}", help=f"Remove {session_name}", use_container_width=True):
                        del shared_state["folders"][folder_name][session_name]
                        shared_state["active_sessions"].discard((folder_name, session_name))
                        st.rerun()
else:
    st.sidebar.caption("No active sessions created yet.")

st.sidebar.divider()

# ==========================================
# BUILD THE FINAL ACTIVE DATAFRAME
# ==========================================
dataframes_to_combine = []

for f_name, s_name in list(shared_state["active_sessions"]):
    if f_name in shared_state["folders"] and s_name in shared_state["folders"][f_name]:
        temp_df = shared_state["folders"][f_name][s_name].copy()
        temp_df["Source_Session"] = f"{f_name} - {s_name}"
        dataframes_to_combine.append(temp_df)

if dataframes_to_combine:
    df = pd.concat(dataframes_to_combine, ignore_index=True)
    dataset_name = f"{len(dataframes_to_combine)} Active Session(s)"
else:
    df = pd.DataFrame()
    dataset_name = "No Active Session"


# ==========================================
# 3. PERFORMANCE TUNING & LIVE CALCULATIONS
# ==========================================
st.sidebar.markdown("### 🎯 Performance Tuning")
score_quota = st.sidebar.number_input(
    "Player Score Quota (Per Game):",
    min_value=250,
    max_value=500,
    value=250,
    step=25,
    help="Set the baseline score threshold."
)

if not df.empty:
    quick_wins = df["Win"].sum() if "Win" in df.columns else 0
    quick_total_games = len(df)
    quick_win_pct = (quick_wins / quick_total_games * 100) if quick_total_games > 0 else 0
    
    if "Team_Score" not in df.columns:
        if all(col in df.columns for col in ["Nic_Score", "Aryan_Score", "Dillan_Score"]):
            df["Team_Score"] = df["Nic_Score"] + df["Aryan_Score"] + df["Dillan_Score"]
        else:
            df["Team_Score"] = 0
            
    quick_avg_score = df["Team_Score"].mean() if "Team_Score" in df.columns else 0
    
    st.sidebar.markdown(
        f"""
        <div style="background: var(--secondary-background-color, rgba(15, 23, 42, 0.6)); padding: 12px; border-radius: 8px; border: 1px solid rgba(128,128,128,0.2); margin-top: 10px;">
            <div style="color: #38bdf8; font-size: 0.8rem; font-weight: 900; text-transform: uppercase; margin-bottom: 8px;">Live Calculations</div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span style="color: var(--text-color); opacity: 0.7; font-size: 0.8rem;">Active Games:</span>
                <span style="color: var(--text-color); font-weight: bold;">{quick_total_games}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span style="color: var(--text-color); opacity: 0.7; font-size: 0.8rem;">Win Rate:</span>
                <span style="color: #00FFA3; font-weight: bold;">{quick_win_pct:.1f}%</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span style="color: var(--text-color); opacity: 0.7; font-size: 0.8rem;">Avg Team Score:</span>
                <span style="color: #FF9100; font-weight: bold;">{quick_avg_score:.0f}</span>
            </div>
        </div>
        """, 
        unsafe_allow_html=True
    )

REQUIRED_METRICS = [
    "Nic_Score",
    "Nic_Goals",
    "Nic_Assists",
    "Nic_Saves",
    "Nic_Shots",
    "Aryan_Score",
    "Aryan_Goals",
    "Aryan_Assists",
    "Aryan_Saves",
    "Aryan_Shots",
    "Dillan_Score",
    "Dillan_Goals",
    "Dillan_Assists",
    "Dillan_Saves",
    "Dillan_Shots",
    "Win",
]

is_zero_state = df is None or df.empty

if is_zero_state:
    df = pd.DataFrame([{col: 0 for col in REQUIRED_METRICS}])
    dataset_name = "No Active Session (Zeroed Stats)"

filtered_df = df.copy()

for col in REQUIRED_METRICS:
    if col not in filtered_df.columns:
        filtered_df[col] = 0
    filtered_df[col] = pd.to_numeric(
        filtered_df[col], errors="coerce"
    ).fillna(0)

if "Team_Score" not in filtered_df.columns:
    filtered_df["Team_Score"] = (
        filtered_df["Nic_Score"]
        + filtered_df["Aryan_Score"]
        + filtered_df["Dillan_Score"]
    )
if "Team_Goals" not in filtered_df.columns:
    filtered_df["Team_Goals"] = (
        filtered_df["Nic_Goals"]
        + filtered_df["Aryan_Goals"]
        + filtered_df["Dillan_Goals"]
    )

filtered_df["Nic_Shooting_Pct"] = (
    filtered_df["Nic_Goals"] / filtered_df["Nic_Shots"].replace(0, np.nan)
) * 100
filtered_df["Aryan_Shooting_Pct"] = (
    filtered_df["Aryan_Goals"] / filtered_df["Aryan_Shots"].replace(0, np.nan)
) * 100
filtered_df["Dillan_Shooting_Pct"] = (
    filtered_df["Dillan_Goals"]
    / filtered_df["Dillan_Shots"].replace(0, np.nan)
) * 100
filtered_df.fillna(
    {
        "Nic_Shooting_Pct": 0,
        "Aryan_Shooting_Pct": 0,
        "Dillan_Shooting_Pct": 0,
    },
    inplace=True,
)

filtered_df["Session_Game"] = range(1, len(filtered_df) + 1)

players_meta = {
    "Nic": {
        "tag": "Hughligan",
        "prefix": "Nic",
        "color": "#00F0FF", # Touched up neon blue
        "complement": "#FF5B00",
        "role": "Player Card",
    },
    "Aryan": {
        "tag": "ShaggNazty5480",
        "prefix": "Aryan",
        "color": "#FF003F", # More neon red
        "complement": "#00E5FF",
        "role": "Player Card",
    },
    "Dillan": {
        "tag": "Shagnasty37",
        "prefix": "Dillan",
        "color": "#BF00FF",
        "complement": "#00FFA3",
        "role": "Player Card",
    },
    "Team": {
        "tag": "Squad Stats",
        "prefix": "Team",
        "color": "#CCFF00",
        "complement": "#7C4DFF",
        "role": "Team Card",
    },
}

total_active_games = 0 if is_zero_state else len(filtered_df)
active_wins = (
    0
    if is_zero_state
    else (filtered_df["Win"].sum() if "Win" in filtered_df.columns else 0)
)
active_win_pct = (
    (active_wins / total_active_games * 100) if total_active_games > 0 else 0
)
avg_team_score = (
    0 if is_zero_state else filtered_df["Team_Score"].mean()
)

st.markdown(
    f"""
<div class='title-banner'>
    <div class='main-title'>Rocket League Stats</div>
    <div class='subtitle'>{total_active_games} Game Rumble Session</div>
</div>
""",
    unsafe_allow_html=True,
)


def get_longest_dry_streak(df_in, player_prefix):
    if is_zero_state:
        return 0
    max_streak, current_streak = 0, 0
    for _, row in df_in.iterrows():
        if (
            row.get(f"{player_prefix}_Shots", 0) > 0
            and row.get(f"{player_prefix}_Goals", 0) == 0
        ):
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 0
    return max_streak


# DOWNLOAD TARGET IMAGE HELPER COMPONENT (HTML2CANVAS - CONVERTED TO JPEG)
def render_download_image_button(container_id, filename):
    html_code = f"""
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    <style>
        .dl-btn {{
            background: linear-gradient(135deg, #00A3FF 0%, #00E5FF 100%);
            color: #05070a;
            font-family: 'Rajdhani', sans-serif;
            font-weight: 900;
            font-size: 0.95rem;
            letter-spacing: 1.2px;
            text-transform: uppercase;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(0, 229, 255, 0.4);
            transition: all 0.2s ease;
            margin-bottom: 15px;
        }}
        .dl-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 229, 255, 0.7);
        }}
    </style>
    <div style="text-align: center;">
        <button class="dl-btn" onclick="captureAndDownload()">Download JPEG</button>
    </div>
    <script>
    function captureAndDownload() {{
        const mainDoc = window.parent.document;
        const targetElement = mainDoc.querySelector('{container_id}');
        
        if (!targetElement) return;

        html2canvas(targetElement, {{
            backgroundColor: '#090e17', // Solid dark background for JPEG conversion
            useCORS: true,
            scale: 2,
            windowWidth: 1400, // Explicitly locked to prevent Streamlit columns squishing on clone
            onclone: function(clonedDoc) {{
                const clonedTarget = clonedDoc.querySelector('{container_id}');
                if (clonedTarget) {{
                    clonedTarget.style.height = 'auto';
                    clonedTarget.style.maxHeight = 'none';
                    clonedTarget.style.overflow = 'visible';
                }}
            }}
        }}).then(canvas => {{
            const link = mainDoc.createElement('a');
            link.download = '{filename}';
            link.href = canvas.toDataURL('image/jpeg', 0.95);
            link.click();
        }});
    }}
    </script>
    """
    components.html(html_code, height=60)


# DYNAMIC GENERATOR: AT LEAST 25 RANDOM FUN FACTS (GOOD & BAD)
def generate_random_stat(data):
    if is_zero_state:
        return "SELECT A SESSION IN THE SIDEBAR TO POPULATE MATCH STATS AND HIGHLIGHTS."

    players = ["Nic", "Aryan", "Dillan"]
    p_rand = random.choice(players)

    # Calculate local metrics from incoming DataFrame safe from global scope issues
    tot_active_games = len(data)
    wins = data["Win"].sum() if "Win" in data.columns else 0
    w_rate = (wins / tot_active_games * 100) if tot_active_games > 0 else 0
    mean_team_score = data["Team_Score"].mean() if "Team_Score" in data.columns else 0

    nic_dry = get_longest_dry_streak(data, "Nic")
    aryan_dry = get_longest_dry_streak(data, "Aryan")
    dillan_dry = get_longest_dry_streak(data, "Dillan")
    
    max_score_p = max(players, key=lambda p: data[f"{p}_Score"].max())
    max_score_val = int(data[f"{max_score_p}_Score"].max())
    max_score_game = int(data.loc[data[f"{max_score_p}_Score"].idxmax(), "Session_Game"])

    min_score_p = min(players, key=lambda p: data[f"{p}_Score"].min())
    min_score_val = int(data[f"{min_score_p}_Score"].min())

    max_shots_no_goal = 0
    brick_layer = "None"
    for p in players:
        no_goal_shots = data[data[f"{p}_Goals"] == 0][f"{p}_Shots"].max()
        if not np.isnan(no_goal_shots) and no_goal_shots > max_shots_no_goal:
            max_shots_no_goal = int(no_goal_shots)
            brick_layer = players_meta[p]["tag"]

    best_acc_p = max(players, key=lambda p: (data[f"{p}_Goals"].sum() / data[f"{p}_Shots"].sum()) if data[f"{p}_Shots"].sum() > 0 else 0)
    best_acc_val = (data[f"{best_acc_p}_Goals"].sum() / data[f"{best_acc_p}_Shots"].sum() * 100) if data[f"{best_acc_p}_Shots"].sum() > 0 else 0

    most_saves_p = max(players, key=lambda p: data[f"{p}_Saves"].sum())
    most_saves_val = int(data[f"{most_saves_p}_Saves"].sum())

    most_assists_p = max(players, key=lambda p: data[f"{p}_Assists"].sum())
    most_assists_val = int(data[f"{most_assists_p}_Assists"].sum())

    team_max_score = int(data["Team_Score"].max())
    team_min_score = int(data["Team_Score"].min())
    tot_team_goals = int(data["Team_Goals"].sum())
    
    # Ranks & MVPs
    match_scores = data[["Nic_Score", "Aryan_Score", "Dillan_Score"]].copy()
    ranks = match_scores.rank(axis=1, method="min", ascending=False)
    p_3rd_counts = {p: int((ranks[f"{p}_Score"] == 3).sum()) for p in players}
    p_mvp_counts = {p: int((ranks[f"{p}_Score"] == 1).sum()) for p in players}
    
    passenger_p = max(p_3rd_counts, key=p_3rd_counts.get)
    mvp_king_p = max(p_mvp_counts, key=p_mvp_counts.get)

    pool = [
        # 1-5 Dry Streaks / Funny Bads
        f"OFFENSIVE DROUGHT: <b>{players_meta['Nic']['tag']}</b> went on a <b>{nic_dry}</b> match goal drought streak!",
        f"BRICK LAYER: <b>{players_meta['Aryan']['tag']}</b> experienced a <b>{aryan_dry}</b> match dry streak without scoring!",
        f"GHOST MODE: <b>{players_meta['Dillan']['tag']}</b> went <b>{dillan_dry}</b> consecutive games firing shots into thin air with 0 goals!",
        f"STORMTROOPER ACCURACY: <b>{brick_layer}</b> took <b>{max_shots_no_goal}</b> shots in a single game and scored absolutely ZERO goals!",
        f"PERMANENT PASSENGER: <b>{players_meta[passenger_p]['tag']}</b> finished in last place on the squad <b>{p_3rd_counts[passenger_p]}</b> times!",

        # 6-10 Highs & Peaks
        f"PEAK SCORE: <b>{players_meta[max_score_p]['tag']}</b> erupted for a session peak score of <b>{max_score_val:,}</b> Pts in Game {max_score_game}!",
        f"SQUAD ERUPTION: The team combined for a massive session high of <b>{team_max_score:,}</b> total points!",
        f"SNIPER ELITE: <b>{players_meta[best_acc_p]['tag']}</b> commands the team in goal conversion at <b>{best_acc_val:.1f}%</b> accuracy!",
        f"WALL OF CHINA: <b>{players_meta[most_saves_p]['tag']}</b> locked down the net with a total of <b>{most_saves_val}</b> saves!",
        f"PLAYMAKER SUPREME: <b>{players_meta[most_assists_p]['tag']}</b> dished out <b>{most_assists_val}</b> total assists to team mates!",

        # 11-15 Lows & Shames
        f"CARRIED HARD: <b>{players_meta[min_score_p]['tag']}</b> registered a session low of just <b>{min_score_val:,}</b> points in a match!",
        f"SQUAD SLUMP: The squad suffered a combined total match low of only <b>{team_min_score:,}</b> points!",
        f"MISSING IN ACTION: <b>{players_meta[min_score_p]['tag']}</b> finished under {score_quota} points in multiple games!",
        f"HEAVY CARGO: <b>{players_meta[passenger_p]['tag']}</b> occupied the bottom of the scoreboard in <b>{(p_3rd_counts[passenger_p]/tot_active_games*100):.0f}%</b> of games!",
        f"DEFENSIVE LEAK: Squad allowed opponents to outscore them while holding a <b>{(100-w_rate):.1f}%</b> loss rate!",

        # 16-20 Dynamic Good Stats
        f"MVP CROWN: <b>{players_meta[mvp_king_p]['tag']}</b> claimed top score MVP honors in <b>{p_mvp_counts[mvp_king_p]}</b> matches!",
        f"GOAL MACHINE: Squad racked up <b>{tot_team_goals}</b> total goals across <b>{tot_active_games}</b> matches!",
        f"DOMINANCE: Team boasts an impressive <b>{w_rate:.1f}%</b> win rate across active sessions!",
        f"HEAVY ARTILLERY: <b>{players_meta[p_rand]['tag']}</b> posted an average score of <b>{data[f'{p_rand}_Score'].mean():.1f}</b> Pts per game!",
        f"QUOTA BUSTER: <b>{players_meta[mvp_king_p]['tag']}</b> exceeded the {score_quota} Pts quota in <b>{int((data[f'{mvp_king_p}_Score'] >= score_quota).sum())}</b> matches!",

        # 21-27 Fun Mix & Roster Trivia
        f"SAVING GRACE: <b>{players_meta['Dillan']['tag']}</b> logged an average of <b>{data['Dillan_Saves'].mean():.2f}</b> saves per game!",
        f"TARGET PRACTICE: <b>{players_meta['Nic']['tag']}</b> put <b>{int(data['Nic_Shots'].sum())}</b> total shots towards opponent net!",
        f"UNSELFISH PLAY: <b>{players_meta['Aryan']['tag']}</b> has a total assist count of <b>{int(data['Aryan_Assists'].sum())}</b>!",
        f"SQUAD AVERAGE: Team maintains a solid average output of <b>{mean_team_score:.0f}</b> points per match!",
        f"POINT GUARD: <b>{players_meta[p_rand]['tag']}</b> scored over 500 Pts in <b>{int((data[f'{p_rand}_Score']>=500).sum())}</b> matches!",
        f"TOTAL OFFENSE: <b>{tot_team_goals}</b> total team goals scored with average <b>{(tot_team_goals/tot_active_games if tot_active_games>0 else 0):.1f}</b> goals/game!",
        f"LAST RESORT: Squad registered <b>{int(data['Nic_Saves'].sum()+data['Aryan_Saves'].sum()+data['Dillan_Saves'].sum())}</b> total epic saves!",
    ]
    return random.choice(pool)


# REUSABLE PLAYER CARD HTML GENERATOR
def generate_player_card_html(
    player_key, df_data, target_quota, compiled_single_column=False
):
    p_tag = players_meta[player_key]["tag"]
    p_color = players_meta[player_key]["color"]
    p_role = players_meta[player_key]["role"]
    p_initial = p_tag[0]

    tot_score = 0 if is_zero_state else int(df_data[f"{player_key}_Score"].sum())
    tot_goals = 0 if is_zero_state else int(df_data[f"{player_key}_Goals"].sum())
    tot_assists = 0 if is_zero_state else int(df_data[f"{player_key}_Assists"].sum())
    tot_saves = 0 if is_zero_state else int(df_data[f"{player_key}_Saves"].sum())
    tot_shots = 0 if is_zero_state else int(df_data[f"{player_key}_Shots"].sum())

    avg_score = 0.0 if is_zero_state else df_data[f"{player_key}_Score"].mean()
    avg_goals = 0.0 if is_zero_state else df_data[f"{player_key}_Goals"].mean()
    avg_assists = 0.0 if is_zero_state else df_data[f"{player_key}_Assists"].mean()
    avg_saves = 0.0 if is_zero_state else df_data[f"{player_key}_Saves"].mean()
    avg_shots = 0.0 if is_zero_state else df_data[f"{player_key}_Shots"].mean()

    max_score = 0 if is_zero_state else int(df_data[f"{player_key}_Score"].max())
    min_score = 0 if is_zero_state else int(df_data[f"{player_key}_Score"].min())

    shooting_avg = (tot_goals / tot_shots * 100) if tot_shots > 0 else 0.0

    tot_matches = 0 if is_zero_state else len(df_data)
    games_over_quota = (
        0
        if is_zero_state
        else int((df_data[f"{player_key}_Score"] >= target_quota).sum())
    )
    games_under_quota = (
        0
        if is_zero_state
        else int((df_data[f"{player_key}_Score"] < target_quota).sum())
    )
    quota_hit_rate = (
        (games_over_quota / tot_matches * 100) if tot_matches > 0 else 0
    )

    if not is_zero_state:
        match_scores = df_data[
            ["Nic_Score", "Aryan_Score", "Dillan_Score"]
        ].copy()
        ranks = match_scores.rank(axis=1, method="min", ascending=False)
        p_ranks = ranks[f"{player_key}_Score"]
        mvp_count = int((p_ranks == 1).sum())
        second_count = int((p_ranks == 2).sum())
        third_count = int((p_ranks == 3).sum())
    else:
        mvp_count = 0
        second_count = 0
        third_count = 0

    font_tag_size = "1.15rem" if compiled_single_column else "1.5rem"
    score_badge_font = "0.72rem" if compiled_single_column else "0.8rem"

    if compiled_single_column:
        body_content = f"""<div class="card-stat-box" style="width: 100%;">
<div class="box-title">Core Actions (Sum / Avg)</div>
<div class="stat-row-dual"><span class="stat-lbl">Goals:</span><div><span class="stat-v-sum">{tot_goals}</span> <span class="stat-v-avg">({avg_goals:.2f})</span></div></div>
<div class="stat-row-dual"><span class="stat-lbl">Assists:</span><div><span class="stat-v-sum">{tot_assists}</span> <span class="stat-v-avg">({avg_assists:.2f})</span></div></div>
<div class="stat-row-dual"><span class="stat-lbl">Saves:</span><div><span class="stat-v-sum">{tot_saves}</span> <span class="stat-v-avg">({avg_saves:.2f})</span></div></div>
<div class="stat-row-dual"><span class="stat-lbl">Shots:</span><div><span class="stat-v-sum">{tot_shots}</span> <span class="stat-v-avg">({avg_shots:.2f})</span></div></div>
<div class="box-title" style="margin-top: 14px;">Precision & Range</div>
<div class="stat-row-dual"><span class="stat-lbl">Avg Score:</span><span class="stat-v-sum">{avg_score:.1f} Pts</span></div>
<div class="stat-row-dual"><span class="stat-lbl">Shooting Avg:</span><span class="stat-v-gold">{shooting_avg:.1f}%</span></div>
<div class="stat-row-dual"><span class="stat-lbl">Max Score:</span><span class="stat-v-gold">{max_score:,}</span></div>
<div class="stat-row-dual"><span class="stat-lbl">Lowest Score:</span><span class="stat-v-red">{min_score:,}</span></div>
<div class="box-title" style="margin-top: 14px;">Quotas & Placements</div>
<div class="stat-row-dual"><span class="stat-lbl">Over/Under Quota:</span><span class="stat-v-sum">{games_over_quota}/{games_under_quota}</span></div>
<div class="stat-row-dual"><span class="stat-lbl">Quota Avg:</span><span class="stat-v-avg">{quota_hit_rate:.0f}%</span></div>
<div class="stat-row-dual"><span class="stat-lbl">MVP:</span><span class="stat-v-gold">{mvp_count}</span></div>
<div class="stat-row-dual"><span class="stat-lbl">2nd:</span><span class="stat-v-avg">{second_count}</span></div>
<div class="stat-row-dual"><span class="stat-lbl">3rd:</span><span class="stat-v-sum">{third_count}</span></div>
</div>"""
    else:
        body_content = f"""<div class="card-grid-3">
<div class="card-stat-box">
<div class="box-title">Core Actions (Sum / Avg)</div>
<div class="stat-row-dual"><span class="stat-lbl">Goals:</span><div><span class="stat-v-sum">{tot_goals}</span> <span class="stat-v-avg">({avg_goals:.2f})</span></div></div>
<div class="stat-row-dual"><span class="stat-lbl">Assists:</span><div><span class="stat-v-sum">{tot_assists}</span> <span class="stat-v-avg">({avg_assists:.2f})</span></div></div>
<div class="stat-row-dual"><span class="stat-lbl">Saves:</span><div><span class="stat-v-sum">{tot_saves}</span> <span class="stat-v-avg">({avg_saves:.2f})</span></div></div>
<div class="stat-row-dual"><span class="stat-lbl">Shots:</span><div><span class="stat-v-sum">{tot_shots}</span> <span class="stat-v-avg">({avg_shots:.2f})</span></div></div>
</div>
<div class="card-stat-box">
<div class="box-title">Precision & Range</div>
<div class="stat-row-dual"><span class="stat-lbl">Avg Score:</span><span class="stat-v-sum">{avg_score:.1f} Pts</span></div>
<div class="stat-row-dual"><span class="stat-lbl">Shooting Avg:</span><span class="stat-v-gold">{shooting_avg:.1f}%</span></div>
<div class="stat-row-dual"><span class="stat-lbl">Max Score:</span><span class="stat-v-gold">{max_score:,}</span></div>
<div class="stat-row-dual"><span class="stat-lbl">Lowest Score:</span><span class="stat-v-red">{min_score:,}</span></div>
</div>
<div class="card-stat-box">
<div class="box-title">Quotas & Placements</div>
<div class="stat-row-dual"><span class="stat-lbl">Over/Under Quota:</span><span class="stat-v-sum">{games_over_quota}/{games_under_quota}</span></div>
<div class="stat-row-dual"><span class="stat-lbl">Quota Avg:</span><span class="stat-v-avg">{quota_hit_rate:.0f}%</span></div>
<div class="stat-row-dual"><span class="stat-lbl">MVP:</span><span class="stat-v-gold">{mvp_count}</span></div>
<div class="stat-row-dual"><span class="stat-lbl">2nd:</span><span class="stat-v-avg">{second_count}</span></div>
<div class="stat-row-dual"><span class="stat-lbl">3rd:</span><span class="stat-v-sum">{third_count}</span></div>
</div>
</div>"""

    card_html = f"""<div class="player-card-container" style="border: 2px solid {p_color}; box-shadow: 0 0 25px {p_color}44;">
<div class="player-card-header">
<div class="player-identity">
<div class="player-avatar-badge" style="background: {p_color}; border: 2px solid #ffffff;">{p_initial}</div>
<div>
<div class="player-card-gamertag" style="font-size: {font_tag_size};">{p_tag}</div>
<div style="display: flex; align-items: center; gap: 8px; margin-top: 4px; flex-wrap: wrap;">
<span class="player-card-role">{p_role}</span>
<span style="background: rgba(255, 215, 0, 0.15); border: 1px solid #ffd700; color: #ffd700; padding: 2px 8px; border-radius: 6px; font-weight: 900; font-size: {score_badge_font}; white-space: nowrap;">{tot_score:,} PTS</span>
</div>
</div>
</div>
</div>
{body_content}
</div>"""
    return card_html


# REUSABLE TEAM CARD HTML GENERATOR
def generate_team_card_html(df_data, target_quota):
    t_color = players_meta["Team"]["color"]
    t_tag = players_meta["Team"]["tag"]

    tot_goals = 0 if is_zero_state else sum(df_data[f"{p}_Goals"].sum() for p in ["Nic", "Aryan", "Dillan"])
    tot_assists = 0 if is_zero_state else sum(df_data[f"{p}_Assists"].sum() for p in ["Nic", "Aryan", "Dillan"])
    tot_saves = 0 if is_zero_state else sum(df_data[f"{p}_Saves"].sum() for p in ["Nic", "Aryan", "Dillan"])
    tot_shots = 0 if is_zero_state else sum(df_data[f"{p}_Shots"].sum() for p in ["Nic", "Aryan", "Dillan"])

    team_game_scores = (
        df_data["Nic_Score"]
        + df_data["Aryan_Score"]
        + df_data["Dillan_Score"]
    )
    tot_score = 0 if is_zero_state else int(team_game_scores.sum())

    tot_matches = 0 if is_zero_state else len(df_data)
    avg_score = team_game_scores.mean() if tot_matches > 0 else 0
    avg_goals = tot_goals / tot_matches if tot_matches > 0 else 0
    avg_assists = tot_assists / tot_matches if tot_matches > 0 else 0
    avg_saves = tot_saves / tot_matches if tot_matches > 0 else 0
    avg_shots = tot_shots / tot_matches if tot_matches > 0 else 0

    max_score = int(team_game_scores.max()) if tot_matches > 0 else 0
    min_score = int(team_game_scores.min()) if tot_matches > 0 else 0
    shooting_avg = (tot_goals / tot_shots * 100) if tot_shots > 0 else 0

    team_target_quota = target_quota * 3
    games_over_quota = (
        0
        if is_zero_state
        else int((team_game_scores >= team_target_quota).sum())
    )
    games_under_quota = (
        0
        if is_zero_state
        else int((team_game_scores < team_target_quota).sum())
    )
    quota_hit_rate = (
        (games_over_quota / tot_matches * 100) if tot_matches > 0 else 0
    )

    wins = (
        0
        if is_zero_state
        else int(df_data["Win"].sum() if "Win" in df_data.columns else 0)
    )
    losses = max(0, tot_matches - wins)
    win_pct = (wins / tot_matches * 100) if tot_matches > 0 else 0

    card_html = f"""<div class="player-card-container" style="border: 2px solid {t_color}; box-shadow: 0 0 25px {t_color}44;">
<div class="player-card-header">
<div class="player-identity">
<div class="player-avatar-badge" style="background: {t_color}; border: 2px solid #ffffff; color: #000000;">T</div>
<div>
<div class="player-card-gamertag" style="font-size: 1.5rem;">{t_tag}</div>
<div style="display: flex; align-items: center; gap: 8px; margin-top: 4px; flex-wrap: wrap;">
<span class="player-card-role">Team Card</span>
<span style="background: rgba(255, 215, 0, 0.15); border: 1px solid #ffd700; color: #ffd700; padding: 2px 8px; border-radius: 6px; font-weight: 900; font-size: 0.8rem; white-space: nowrap;">{tot_score:,} PTS</span>
</div>
</div>
</div>
</div>
<div class="card-grid-3">
<div class="card-stat-box">
<div class="box-title">Core Actions (Sum / Avg)</div>
<div class="stat-row-dual"><span class="stat-lbl">Goals:</span><div><span class="stat-v-sum">{tot_goals}</span> <span class="stat-v-avg">({avg_goals:.2f})</span></div></div>
<div class="stat-row-dual"><span class="stat-lbl">Assists:</span><div><span class="stat-v-sum">{tot_assists}</span> <span class="stat-v-avg">({avg_assists:.2f})</span></div></div>
<div class="stat-row-dual"><span class="stat-lbl">Saves:</span><div><span class="stat-v-sum">{tot_saves}</span> <span class="stat-v-avg">({avg_saves:.2f})</span></div></div>
<div class="stat-row-dual"><span class="stat-lbl">Shots:</span><div><span class="stat-v-sum">{tot_shots}</span> <span class="stat-v-avg">({avg_shots:.2f})</span></div></div>
</div>
<div class="card-stat-box">
<div class="box-title">Precision & Range</div>
<div class="stat-row-dual"><span class="stat-lbl">Avg Score:</span><span class="stat-v-sum">{avg_score:.1f} Pts</span></div>
<div class="stat-row-dual"><span class="stat-lbl">Shooting Avg:</span><span class="stat-v-gold">{shooting_avg:.1f}%</span></div>
<div class="stat-row-dual"><span class="stat-lbl">Max Score:</span><span class="stat-v-gold">{max_score:,}</span></div>
<div class="stat-row-dual"><span class="stat-lbl">Lowest Score:</span><span class="stat-v-red">{min_score:,}</span></div>
</div>
<div class="card-stat-box">
<div class="box-title">Match Performance</div>
<div class="stat-row-dual"><span class="stat-lbl">Over/Under Quota:</span><span class="stat-v-sum">{games_over_quota}/{games_under_quota}</span></div>
<div class="stat-row-dual"><span class="stat-lbl">Quota Avg ({team_target_quota} Pts):</span><span class="stat-v-avg">{quota_hit_rate:.0f}%</span></div>
<div class="stat-row-dual"><span class="stat-lbl">Record (W-L):</span><span class="stat-v-gold">{wins}W - {losses}L</span></div>
<div class="stat-row-dual"><span class="stat-lbl">Win Rate:</span><span class="stat-v-avg">{win_pct:.1f}%</span></div>
</div>
</div>
</div>"""
    return card_html


# RENDER INDIVIDUAL PLAYER TAB
def render_player_tab(player_key, df_data, target_quota):
    card_html = generate_player_card_html(
        player_key, df_data, target_quota, compiled_single_column=False
    )
    st.markdown(card_html, unsafe_allow_html=True)

    p_tag = players_meta[player_key]["tag"]
    p_color = players_meta[player_key]["color"]

    tot_goals = 0 if is_zero_state else df_data[f"{player_key}_Goals"].sum()
    tot_assists = 0 if is_zero_state else df_data[f"{player_key}_Assists"].sum()
    tot_saves = 0 if is_zero_state else df_data[f"{player_key}_Saves"].sum()
    tot_shots = 0 if is_zero_state else df_data[f"{player_key}_Shots"].sum()

    radar_categories = ["Assists", "Goals", "Shots", "Saves", "Assists"]
    radar_values = [tot_assists, tot_goals, tot_shots, tot_saves, tot_assists]
    max_val = max(radar_values) if max(radar_values) > 0 else 10
    radar_texts = [str(v) for v in radar_values]
    text_positions = [
        "top center",
        "middle right",
        "bottom center",
        "middle left",
        "top center",
    ]

    fig_p_radar = go.Figure()

    # FIX: Combined fill, lines, markers, and text into a single cohesive trace
    fig_p_radar.add_trace(
        go.Scatterpolar(
            r=radar_values,
            theta=radar_categories,
            text=radar_texts,
            mode="lines+markers+text",
            fill="toself",
            fillcolor=hex_to_rgba(p_color, 0.25),
            textposition=text_positions,
            textfont=dict(color="#FFFFFF", size=12, weight="bold"),
            name=p_tag,
            line=dict(color=p_color, width=3),
            marker=dict(size=8, color=p_color),
            cliponaxis=False,
            hoverinfo="theta+text",
        )
    )

    fig_p_radar.update_layout(
        title=None,
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            angularaxis=dict(
                direction="clockwise",
                rotation=90,
                tickfont=dict(color="#FFFFFF", size=12, weight="bold"),
                gridcolor="rgba(128,128,128,0.2)",
            ),
            radialaxis=dict(
                visible=True,
                range=[0, max_val * 1.15],
                tickfont=dict(color="#94a3b8", size=9),
                showticklabels=False,
                gridcolor="rgba(128,128,128,0.2)",
            ),
        ),
        template="plotly_dark",
        height=450,
        margin=dict(l=60, r=60, t=20, b=30),
    )
    fig_p_radar = apply_balanced_chart_theme(fig_p_radar)
    st.plotly_chart(
        fig_p_radar, use_container_width=True, config={"displayModeBar": False}
    )


# MAIN NAVIGATION (Consolidated Tabs)
(
    tab_news,
    tab_playercard,
    tab_stackup,
    tab_team,
    tab_raw,
) = st.tabs([
    "News",
    "Playercard",
    "The Stack Up",
    "Team Card",
    "Raw Data",
])

# TAB 1: NEWS 
with tab_news:
    if "current_desk_stat" not in st.session_state:
        st.session_state.current_desk_stat = generate_random_stat(filtered_df)

    btn_col, ticker_col = st.columns(
        [1.8, 8.2], gap="small", vertical_alignment="center"
    )

    with btn_col:
        if st.button("SHUFFLE FEED", use_container_width=True):
            st.session_state.current_desk_stat = generate_random_stat(
                filtered_df
            )
            st.session_state.manual_shuffled = True

    with ticker_col:

        @st.fragment(run_every=6)
        def render_live_ticker():
            if st.session_state.get("manual_shuffled", False):
                st.session_state.manual_shuffled = False
            else:
                st.session_state.current_desk_stat = generate_random_stat(
                    filtered_df
                )

            font_size = get_dynamic_font_size(
                st.session_state.current_desk_stat
            )

            st.markdown(
                f"""
                <div class="live-ticker-box-connected">
                    <div class="live-desk-text" style="font-size: {font_size} !important;">
                        {st.session_state.current_desk_stat}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        render_live_ticker()

    # BEST STAT COMPUTATION FOR FEATURED HEADLINE
    if not is_zero_state:
        peak_p = max(["Nic", "Aryan", "Dillan"], key=lambda p: filtered_df[f"{p}_Score"].max())
        peak_p_tag = players_meta[peak_p]["tag"]
        peak_score = int(filtered_df[f"{peak_p}_Score"].max())
        peak_game = int(filtered_df.loc[filtered_df[f"{peak_p}_Score"].idxmax(), "Session_Game"])
        featured_title = f"{peak_p_tag} Erupts For Session Record {peak_score:,} Pts!"
        featured_desc = f"In Game {peak_game}, <b>{peak_p_tag}</b> delivered the highest single-game performance of the active session selection, securing <b>{peak_score:,}</b> points. Overall, the squad maintained a <b>{active_win_pct:.1f}%</b> win rate with <b>{int(filtered_df['Team_Goals'].sum())}</b> total goals."
    else:
        featured_title = "No Active Session Data Selected"
        featured_desc = "Select a session in the sidebar to populate session metrics and featured highlights."

    st.markdown(
        f"""
        <div class="featured-headline-card">
            <span style="background: rgba(204, 255, 0, 0.2); color: #CCFF00; border: 1px solid #CCFF00; 
                         padding: 4px 12px; border-radius: 6px; font-size: 0.75rem; font-weight: 900; letter-spacing: 1px;">
                FEATURED HEADLINE
            </span>
            <div style="font-size: 1.8rem; font-weight: 900; color: var(--text-color); margin-top: 10px; margin-bottom: 6px; font-family: 'Rajdhani', sans-serif;">
                {featured_title}
            </div>
            <div style="color: var(--text-color); opacity: 0.85; font-size: 1rem; line-height: 1.5;">
                {featured_desc}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # RENDER STORY COLUMN WITHOUT GRAPHS
    def render_story_column(col, owner_key, badge_label, story_title, story_body):
        p_color = players_meta[owner_key]["color"]
        with col:
            st.markdown(
                f"""
                <div class="card-border-{owner_key}">
                    <span style="background: {p_color}22; color: {p_color}; border: 1px solid {p_color}; 
                                 padding: 3px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 900; letter-spacing: 1px;">
                        {badge_label}
                    </span>
                    <div class="story-header-text">{story_title}</div>
                    <div class="story-body-text">{story_body}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ARYAN STORIES
    col_aryan_hi, col_aryan_lo = st.columns(2)
    max_aryan_score = int(filtered_df["Aryan_Score"].max()) if not is_zero_state else 0
    dry_aryan = get_longest_dry_streak(filtered_df, "Aryan")

    render_story_column(
        col=col_aryan_hi,
        owner_key="Aryan",
        badge_label="SHAGGNAZTY5480 HIGHLIGHT",
        story_title=f"Peak Score: {max_aryan_score:,} Points",
        story_body=f"ShaggNazty5480 recorded a peak match score of <b>{max_aryan_score:,}</b> points in current sessions.",
    )
    render_story_column(
        col=col_aryan_lo,
        owner_key="Aryan",
        badge_label="SHAGGNAZTY5480 LOWLIGHT",
        story_title=f"Goal Drought Streak: {dry_aryan} Matches",
        story_body=f"ShaggNazty5480 went <b>{dry_aryan}</b> consecutive games where high shot volume yielded zero goals.",
    )

    # NIC STORIES
    col_nic_hi, col_nic_lo = st.columns(2)
    nic_goals_tot = int(filtered_df["Nic_Goals"].sum()) if not is_zero_state else 0
    min_nic_score = int(filtered_df["Nic_Score"].min()) if not is_zero_state else 0
    min_nic_game = filtered_df.loc[filtered_df["Nic_Score"].idxmin(), "Session_Game"] if not is_zero_state else 0

    render_story_column(
        col=col_nic_hi,
        owner_key="Nic",
        badge_label="HUGHLIGAN HIGHLIGHT",
        story_title=f"Offensive Leadership: {nic_goals_tot} Goals",
        story_body=f"Hughligan spearheaded the offensive attack with <b>{nic_goals_tot}</b> total goals.",
    )
    render_story_column(
        col=col_nic_lo,
        owner_key="Nic",
        badge_label="HUGHLIGAN LOWLIGHT",
        story_title=f"Session Low: {min_nic_score:,} Points",
        story_body=f"Hughligan hit a low point on Game {min_nic_game} with <b>{min_nic_score:,}</b> points.",
    )

    # DILLAN STORIES
    col_dillan_hi, col_dillan_lo = st.columns(2)
    d_saves = int(filtered_df["Dillan_Saves"].sum()) if not is_zero_state else 0
    dry_dillan = get_longest_dry_streak(filtered_df, "Dillan")

    render_story_column(
        col=col_dillan_hi,
        owner_key="Dillan",
        badge_label="SHAGNASTY37 HIGHLIGHT",
        story_title=f"Defensive Anchor: {d_saves} Saves",
        story_body=f"Shagnasty37 anchored defense with a total of <b>{d_saves}</b> saves.",
    )
    render_story_column(
        col=col_dillan_lo,
        owner_key="Dillan",
        badge_label="SHAGNASTY37 LOWLIGHT",
        story_title=f"Offensive Drought: {dry_dillan} Games",
        story_body=f"Shagnasty37 experienced a <b>{dry_dillan}</b> match dry patch without scoring goals.",
    )

    # TEAM STORIES
    col_team_hi, col_team_lo = st.columns(2)
    max_team_score = int(filtered_df["Team_Score"].max()) if not is_zero_state else 0
    loss_pct = (100 - active_win_pct) if not is_zero_state else 0

    render_story_column(
        col=col_team_hi,
        owner_key="Team",
        badge_label="TEAM HIGHLIGHT",
        story_title=f"Peak Session Output: {max_team_score:,} Points",
        story_body=f"The squad combined for a session peak score of <b>{max_team_score:,}</b> points.",
    )
    render_story_column(
        col=col_team_lo,
        owner_key="Team",
        badge_label="TEAM LOWLIGHT",
        story_title=f"Loss Ratio: {loss_pct:.1f}%",
        story_body=f"The team dropped <b>{loss_pct:.1f}%</b> of matches in the current selection.",
    )

# CONSOLIDATED PLAYER TABS W/ DROPDOWN
with tab_playercard:
    st.markdown("### Player Select")
    selected_player = st.selectbox(
        "Choose a player to view their card:", 
        ["Hughligan", "ShaggNazty5480", "Shagnasty37"]
    )
    
    st.divider()
    
    if selected_player == "Hughligan":
        render_player_tab("Nic", filtered_df, score_quota)
    elif selected_player == "ShaggNazty5480":
        render_player_tab("Aryan", filtered_df, score_quota)
    else:
        render_player_tab("Dillan", filtered_df, score_quota)

# TAB 5: THE STACK UP 
with tab_stackup:
    render_download_image_button("#stack-up-export", "stack_up_overview.jpeg")

    export_html = f"""
    <div id="stack-up-export" style="background: transparent; padding: 20px; width: 100%;">
        <div class="stack-up-grid" style="display: flex; flex-wrap: nowrap; justify-content: space-between; gap: 15px; width: 100%;">
            <div style="flex: 1 1 0; min-width: 0;">{generate_player_card_html("Nic", filtered_df, score_quota, compiled_single_column=True)}</div>
            <div style="flex: 1 1 0; min-width: 0;">{generate_player_card_html("Aryan", filtered_df, score_quota, compiled_single_column=True)}</div>
            <div style="flex: 1 1 0; min-width: 0;">{generate_player_card_html("Dillan", filtered_df, score_quota, compiled_single_column=True)}</div>
        </div>
    </div>
    """
    st.markdown(export_html, unsafe_allow_html=True)

    st.markdown(
        """
        <div style="display: flex; justify-content: center; align-items: center; gap: 28px; background: var(--secondary-background-color, rgba(15, 23, 42, 0.75)); border: 1px solid rgba(128, 128, 128, 0.2); border-radius: 12px; padding: 10px 20px; margin-top: 10px; margin-bottom: 25px; max-width: 650px; margin-left: auto; margin-right: auto; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 14px; height: 14px; border-radius: 50%; background-color: #00F0FF; box-shadow: 0 0 8px #00F0FF;"></div>
                <span style="color: var(--text-color); font-weight: 800; font-size: 0.9rem;">Hughligan</span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 14px; height: 14px; border-radius: 50%; background-color: #FF003F; box-shadow: 0 0 8px #FF003F;"></div>
                <span style="color: var(--text-color); font-weight: 800; font-size: 0.9rem;">ShaggNazty5480</span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 14px; height: 14px; border-radius: 50%; background-color: #BF00FF; box-shadow: 0 0 8px #BF00FF;"></div>
                <span style="color: var(--text-color); font-weight: 800; font-size: 0.9rem;">Shagnasty37</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    radar_cats = ["Assists", "Goals", "Shots", "Saves", "Assists"]

    fig_indiv_radar = go.Figure()
    indiv_max_val = 10

    # Layer 1: Add all fill areas first so no trace fill covers another player's dots/lines
    for p_key in ["Nic", "Aryan", "Dillan"]:
        p_col = players_meta[p_key]["color"]

        tot_a = 0 if is_zero_state else filtered_df[f"{p_key}_Assists"].sum()
        tot_g = 0 if is_zero_state else filtered_df[f"{p_key}_Goals"].sum()
        tot_sh = 0 if is_zero_state else filtered_df[f"{p_key}_Shots"].sum()
        tot_s = 0 if is_zero_state else filtered_df[f"{p_key}_Saves"].sum()

        radar_vals = [tot_a, tot_g, tot_sh, tot_s, tot_a]
        indiv_max_val = max(indiv_max_val, max(radar_vals))

        fig_indiv_radar.add_trace(
            go.Scatterpolar(
                r=radar_vals,
                theta=radar_cats,
                mode="none",
                fill="toself",
                fillcolor=hex_to_rgba(p_col, 0.22),
                hoverinfo="skip",
                showlegend=False,
            )
        )

    # Layer 2: Add all lines and markers on top of all fills
    for p_key in ["Nic", "Aryan", "Dillan"]:
        p_tag = players_meta[p_key]["tag"]
        p_col = players_meta[p_key]["color"]

        tot_a = 0 if is_zero_state else filtered_df[f"{p_key}_Assists"].sum()
        tot_g = 0 if is_zero_state else filtered_df[f"{p_key}_Goals"].sum()
        tot_sh = 0 if is_zero_state else filtered_df[f"{p_key}_Shots"].sum()
        tot_s = 0 if is_zero_state else filtered_df[f"{p_key}_Saves"].sum()

        radar_vals = [tot_a, tot_g, tot_sh, tot_s, tot_a]

        fig_indiv_radar.add_trace(
            go.Scatterpolar(
                r=radar_vals,
                theta=radar_cats,
                mode="lines+markers",
                name=p_tag,
                line=dict(color=p_col, width=3),
                marker=dict(size=8, color=p_col),
                cliponaxis=False,
                hoverinfo="name+theta+r",
            )
        )

    fig_indiv_radar.update_layout(
        title=None,
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            angularaxis=dict(
                direction="clockwise",
                rotation=90,
                tickfont=dict(color="#FFFFFF", size=12, weight="bold"),
                gridcolor="rgba(128,128,128,0.2)",
            ),
            radialaxis=dict(
                visible=True,
                range=[0, indiv_max_val * 1.15],
                tickfont=dict(color="#94a3b8", size=9),
                showticklabels=False,
                gridcolor="rgba(128,128,128,0.2)",
            ),
        ),
        showlegend=False,
        template="plotly_dark",
        height=520,
        margin=dict(l=60, r=60, t=50, b=50),
    )
    fig_indiv_radar = apply_balanced_chart_theme(fig_indiv_radar)

    # CENTERED STACK UP RADAR DISPLAY
    col_r1, col_r2, col_r3 = st.columns([1, 10, 1])
    with col_r2:
        st.plotly_chart(
            fig_indiv_radar,
            use_container_width=True,
            config={"displayModeBar": False},
        )

# TAB 6: TEAM CARD 
with tab_team:
    render_download_image_button("#team-export", "team_overview.jpeg")

    team_export_html = f"""
    <div id="team-export" style="background: transparent; padding: 20px; width: 100%;">
        <div style="max-width: 800px; margin: 0 auto;">
            {generate_team_card_html(filtered_df, score_quota)}
        </div>
    </div>
    """
    st.markdown(team_export_html, unsafe_allow_html=True)

    # MOVED & CENTERED TEAM RADAR
    team_color = players_meta["Team"]["color"]
    radar_cats = ["Assists", "Goals", "Shots", "Saves", "Assists"]

    team_tot_a = (
        0
        if is_zero_state
        else sum(filtered_df[f"{p}_Assists"].sum() for p in ["Nic", "Aryan", "Dillan"])
    )
    team_tot_g = (
        0
        if is_zero_state
        else sum(filtered_df[f"{p}_Goals"].sum() for p in ["Nic", "Aryan", "Dillan"])
    )
    team_tot_sh = (
        0
        if is_zero_state
        else sum(filtered_df[f"{p}_Shots"].sum() for p in ["Nic", "Aryan", "Dillan"])
    )
    team_tot_s = (
        0
        if is_zero_state
        else sum(filtered_df[f"{p}_Saves"].sum() for p in ["Nic", "Aryan", "Dillan"])
    )

    team_radar_vals = [
        team_tot_a,
        team_tot_g,
        team_tot_sh,
        team_tot_s,
        team_tot_a,
    ]
    team_max_val = max(team_radar_vals) if max(team_radar_vals) > 0 else 10
    team_radar_texts = [str(v) for v in team_radar_vals]
    text_positions = [
        "top center",
        "middle right",
        "bottom center",
        "middle left",
        "top center",
    ]

    fig_team_radar = go.Figure()

    # FIX: Combined fill, lines, markers, and text into a single cohesive trace
    fig_team_radar.add_trace(
        go.Scatterpolar(
            r=team_radar_vals,
            theta=radar_cats,
            text=team_radar_texts,
            mode="lines+markers+text",
            fill="toself",
            fillcolor=hex_to_rgba(team_color, 0.25),
            textposition=text_positions,
            textfont=dict(color="#FFFFFF", size=12, weight="bold"),
            name="Squad Total",
            line=dict(color=team_color, width=3),
            marker=dict(size=8, color=team_color),
            cliponaxis=False,
            hoverinfo="theta+text",
        )
    )

    fig_team_radar.update_layout(
        title=None,
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            angularaxis=dict(
                direction="clockwise",
                rotation=90,
                tickfont=dict(color="#FFFFFF", size=12, weight="bold"),
                gridcolor="rgba(128,128,128,0.2)",
            ),
            radialaxis=dict(
                visible=True,
                range=[0, team_max_val * 1.15],
                tickfont=dict(color="#94a3b8", size=9),
                showticklabels=False,
                gridcolor="rgba(128,128,128,0.2)",
            ),
        ),
        showlegend=False,
        template="plotly_dark",
        height=520,
        margin=dict(l=60, r=60, t=50, b=50),
    )
    fig_team_radar = apply_balanced_chart_theme(fig_team_radar)

    col_t1, col_t2, col_t3 = st.columns([1, 10, 1])
    with col_t2:
        st.plotly_chart(
            fig_team_radar,
            use_container_width=True,
            config={"displayModeBar": False},
        )

# TAB 7: RAW DATA
with tab_raw:
    st.markdown("### Raw Session Dataset")
    st.dataframe(filtered_df, use_container_width=True)