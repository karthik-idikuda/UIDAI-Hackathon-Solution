"""
Custom CSS Styles for UIDAI Data Hackathon 2026 Application
Professional dark theme with government-standard aesthetics.
No gradients, clean and futuristic design.
"""

# Color Palette
COLORS = {
    "bg_primary": "#0A0E14",
    "bg_secondary": "#12171E",
    "surface": "#1A1F26",
    "border": "#2A3142",
    "text_primary": "#FFFFFF",
    "text_secondary": "#A0A8B8",
    "accent_primary": "#3B82F6",
    "accent_secondary": "#06B6D4",
    "success": "#10B981",
    "warning": "#F59E0B",
    "error": "#EF4444",
}

def get_main_styles():
    """Return the main CSS styles for the application."""
    return f"""
    <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
        
        /* Global Styles */
        .stApp {{
            background-color: {COLORS["bg_primary"]};
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        
        /* Hide Streamlit branding and default pages but keep sidebar controls */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        [data-testid="stSidebarNav"] {{display: none !important;}}
        
        /* Main container */
        .main .block-container {{
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            max-width: 100%;
        }}
        
        /* Sidebar styles - compact */
        [data-testid="stSidebar"] {{
            background-color: {COLORS["bg_secondary"]};
            border-right: 1px solid {COLORS["border"]};
        }}
        
        [data-testid="stSidebar"] > div:first-child {{
            padding-top: 0.5rem;
            padding-bottom: 0.5rem;
        }}
        
        [data-testid="stSidebar"] .block-container {{
            padding: 0.5rem 0.75rem;
        }}
        
        /* Sidebar text */
        [data-testid="stSidebar"] .stMarkdown {{
            color: {COLORS["text_primary"]};
        }}
        
        [data-testid="stSidebar"] .stMarkdown p {{
            margin-bottom: 0.25rem;
        }}
        
        /* Radio buttons in sidebar - compact */
        [data-testid="stSidebar"] .stRadio > label {{
            color: {COLORS["text_primary"]} !important;
            font-weight: 500;
            font-size: 0.8rem;
            margin-bottom: 0.25rem;
        }}
        
        [data-testid="stSidebar"] .stRadio > div {{
            gap: 0.125rem;
        }}
        
        [data-testid="stSidebar"] .stRadio > div > label {{
            background-color: transparent;
            border: none;
            padding: 0.5rem 0.75rem;
            border-radius: 6px;
            margin: 0.0625rem 0;
            transition: all 0.2s ease;
            color: {COLORS["text_secondary"]} !important;
            font-size: 0.85rem;
        }}
        
        [data-testid="stSidebar"] .stRadio > div > label:hover {{
            background-color: {COLORS["surface"]};
            color: {COLORS["text_primary"]} !important;
        }}
        
        [data-testid="stSidebar"] .stRadio > div > label[data-checked="true"] {{
            background-color: {COLORS["accent_primary"]};
            color: {COLORS["text_primary"]} !important;
        }}
        
        /* Sidebar divider */
        [data-testid="stSidebar"] hr {{
            margin: 0.5rem 0;
            border-color: {COLORS["border"]};
        }}
        
        /* Headings */
        h1, h2, h3, h4, h5, h6 {{
            color: {COLORS["text_primary"]} !important;
            font-family: 'Inter', sans-serif;
            font-weight: 600;
        }}
        
        h1 {{
            font-size: 1.75rem !important;
            margin-bottom: 1rem !important;
        }}
        
        h2 {{
            font-size: 1.35rem !important;
            margin-bottom: 0.75rem !important;
        }}
        
        h3 {{
            font-size: 1.1rem !important;
            margin-bottom: 0.5rem !important;
        }}
        
        /* Paragraphs and text */
        p, span, div {{
            color: {COLORS["text_secondary"]};
        }}
        
        /* Labels - WHITE color */
        label, .stSelectbox label, .stMultiSelect label, .stDateInput label {{
            color: {COLORS["text_primary"]} !important;
            font-weight: 500 !important;
        }}
        
        [data-testid="stWidgetLabel"] {{
            color: {COLORS["text_primary"]} !important;
        }}
        
        [data-testid="stWidgetLabel"] p {{
            color: {COLORS["text_primary"]} !important;
        }}
        
        /* Metric cards */
        [data-testid="stMetric"] {{
            background-color: {COLORS["surface"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 10px;
            padding: 1rem;
        }}
        
        [data-testid="stMetric"] label {{
            color: {COLORS["text_primary"]} !important;
            font-size: 0.8rem;
            font-weight: 500;
        }}
        
        [data-testid="stMetric"] [data-testid="stMetricValue"] {{
            color: {COLORS["text_primary"]} !important;
            font-size: 1.5rem;
            font-weight: 700;
        }}
        
        [data-testid="stMetric"] [data-testid="stMetricDelta"] {{
            font-size: 0.75rem;
        }}
        
        /* Selectbox and multiselect */
        .stSelectbox > div > div,
        .stMultiSelect > div > div {{
            background-color: {COLORS["surface"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 6px;
            color: {COLORS["text_primary"]};
        }}
        
        .stSelectbox > div > div:hover,
        .stMultiSelect > div > div:hover {{
            border-color: {COLORS["accent_primary"]};
        }}
        
        /* Multiselect tags */
        .stMultiSelect [data-baseweb="tag"] {{
            background-color: {COLORS["accent_primary"]};
            color: {COLORS["text_primary"]};
        }}
        
        /* Date input */
        .stDateInput > div > div {{
            background-color: {COLORS["surface"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 6px;
        }}
        
        .stDateInput input {{
            color: {COLORS["text_primary"]} !important;
        }}
        
        /* Expanders */
        .streamlit-expanderHeader {{
            background-color: {COLORS["surface"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 6px;
            color: {COLORS["text_primary"]} !important;
        }}
        
        .streamlit-expanderContent {{
            background-color: {COLORS["surface"]};
            border: 1px solid {COLORS["border"]};
            border-top: none;
            border-radius: 0 0 6px 6px;
        }}
        
        /* Dataframe */
        .stDataFrame {{
            background-color: {COLORS["surface"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 6px;
        }}
        
        [data-testid="stDataFrame"] {{
            background-color: {COLORS["surface"]};
        }}
        
        /* Buttons */
        .stButton > button {{
            background-color: {COLORS["accent_primary"]};
            color: {COLORS["text_primary"]};
            border: none;
            border-radius: 6px;
            padding: 0.4rem 1.25rem;
            font-weight: 500;
            transition: all 0.2s ease;
        }}
        
        .stButton > button:hover {{
            background-color: #2563EB;
            transform: translateY(-1px);
        }}
        
        /* Download button */
        .stDownloadButton > button {{
            background-color: {COLORS["surface"]};
            color: {COLORS["text_primary"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 6px;
            padding: 0.4rem 1rem;
            font-weight: 500;
            transition: all 0.2s ease;
        }}
        
        .stDownloadButton > button:hover {{
            background-color: {COLORS["accent_primary"]};
            border-color: {COLORS["accent_primary"]};
        }}
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            background-color: {COLORS["surface"]};
            border-radius: 6px;
            padding: 0.2rem;
            gap: 0.2rem;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background-color: transparent;
            color: {COLORS["text_secondary"]};
            border-radius: 4px;
            padding: 0.4rem 0.8rem;
            font-weight: 500;
        }}
        
        .stTabs [aria-selected="true"] {{
            background-color: {COLORS["accent_primary"]} !important;
            color: {COLORS["text_primary"]} !important;
        }}
        
        /* Divider */
        hr {{
            border-color: {COLORS["border"]};
            margin: 1rem 0;
        }}
        
        /* Spinner */
        .stSpinner > div {{
            border-top-color: {COLORS["accent_primary"]} !important;
        }}
        
        /* Slider */
        .stSlider > div > div > div {{
            background-color: {COLORS["accent_primary"]};
        }}
        
        .stSlider label {{
            color: {COLORS["text_primary"]} !important;
        }}
        
        /* Plotly charts */
        .js-plotly-plot .plotly {{
            background-color: transparent !important;
        }}
        
        /* Scrollbar */
        ::-webkit-scrollbar {{
            width: 6px;
            height: 6px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: {COLORS["bg_secondary"]};
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: {COLORS["border"]};
            border-radius: 3px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: {COLORS["text_secondary"]};
        }}
        
        /* Columns spacing */
        [data-testid="column"] {{
            padding: 0 0.5rem;
        }}
    </style>
    """


def get_plotly_theme():
    """Return Plotly theme configuration for dark mode."""
    return {
        "template": "plotly_dark",
        "paper_bgcolor": COLORS["surface"],
        "plot_bgcolor": COLORS["surface"],
        "font": {
            "family": "Inter, sans-serif",
            "color": COLORS["text_secondary"]
        },
        "colorway": [
            COLORS["accent_primary"],
            COLORS["accent_secondary"],
            COLORS["success"],
            COLORS["warning"],
            COLORS["error"],
            "#8B5CF6",
            "#EC4899",
            "#F97316",
        ],
        "xaxis": {
            "gridcolor": COLORS["border"],
            "linecolor": COLORS["border"],
            "tickcolor": COLORS["text_secondary"],
        },
        "yaxis": {
            "gridcolor": COLORS["border"],
            "linecolor": COLORS["border"],
            "tickcolor": COLORS["text_secondary"],
        },
    }


def apply_plotly_theme(fig):
    """Apply dark theme to a Plotly figure."""
    theme = get_plotly_theme()
    fig.update_layout(
        paper_bgcolor=theme["paper_bgcolor"],
        plot_bgcolor=theme["plot_bgcolor"],
        font=theme["font"],
        xaxis=dict(
            gridcolor=theme["xaxis"]["gridcolor"],
            linecolor=theme["xaxis"]["linecolor"],
            tickfont=dict(color=COLORS["text_secondary"]),
        ),
        yaxis=dict(
            gridcolor=theme["yaxis"]["gridcolor"],
            linecolor=theme["yaxis"]["linecolor"],
            tickfont=dict(color=COLORS["text_secondary"]),
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=COLORS["text_secondary"]),
        ),
        margin=dict(l=20, r=20, t=40, b=20),
    )
    return fig
