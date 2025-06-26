import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration settings"""
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    
    # Vector Database
    CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", "./data/vector_db")
    
    # Document Processing
    MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "100"))
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
    
    # LLM Settings
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.1"))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2000"))
    
    # Streamlit Settings
    STREAMLIT_SERVER_PORT = int(os.getenv("STREAMLIT_SERVER_PORT", "8501"))
    STREAMLIT_SERVER_ADDRESS = os.getenv("STREAMLIT_SERVER_ADDRESS", "localhost")
    
    # Supported file types
    SUPPORTED_FILE_TYPES = [
        "pdf", "docx", "doc", "txt", "md", 
        "pptx", "ppt", "xlsx", "xls"
    ]
    
    # Paths
    DOCUMENTS_DIR = Path("./data/documents")
    VECTOR_DB_DIR = Path(CHROMA_PERSIST_DIRECTORY)
    
    @classmethod
    def validate_config(cls):
        """Validate required configuration"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")
        
        # Create directories if they don't exist
        cls.DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
        cls.VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)
        
        return True

def get_custom_css():
    """Get custom CSS styles to fix font color display issues"""
    return """
    <style>
    /* Main container styles */
    .main > div {
        padding-top: 2rem;
    }
    
    /* Fix font color issues - ensure text visibility */
    .stMarkdown, .stMarkdown p, .stMarkdown div {
        color: #262730 !important;
    }
    
    /* Text color for dark theme */
    @media (prefers-color-scheme: dark) {
        .stMarkdown, .stMarkdown p, .stMarkdown div {
            color: #fafafa !important;
        }
    }
    
    /* Chat message styles */
    .stChatMessage {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
        border: 1px solid #e1e5e9;
        background-color: #ffffff;
    }
    
    .stChatMessage [data-testid="stChatMessageContent"] {
        color: #262730 !important;
    }
    
    @media (prefers-color-scheme: dark) {
        .stChatMessage {
            border-color: #30363d;
            background-color: #21262d;
        }
        .stChatMessage [data-testid="stChatMessageContent"] {
            color: #fafafa !important;
        }
    }
    
    /* User message styles */
    .stChatMessage[data-testid="user-message"] {
        background-color: #e3f2fd;
    }
    
    @media (prefers-color-scheme: dark) {
        .stChatMessage[data-testid="user-message"] {
            background-color: #1565c0;
        }
    }
    
    /* AI message styles */
    .stChatMessage[data-testid="assistant-message"] {
        background-color: #f3e5f5;
    }
    
    @media (prefers-color-scheme: dark) {
        .stChatMessage[data-testid="assistant-message"] {
            background-color: #4a148c;
        }
    }
    
    /* Metric card styles */
    .stMetric {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e1e5e9;
        color: #262730 !important;
    }
    
    .stMetric label {
        color: #6c757d !important;
        font-weight: 500;
    }
    
    .stMetric [data-testid="metric-value"] {
        color: #262730 !important;
        font-weight: 600;
    }
    
    @media (prefers-color-scheme: dark) {
        .stMetric {
            background-color: #21262d;
            border-color: #30363d;
            color: #fafafa !important;
        }
        .stMetric label {
            color: #8b949e !important;
        }
        .stMetric [data-testid="metric-value"] {
            color: #fafafa !important;
        }
    }
    
    /* Enhanced sidebar styles */
    .css-1d391kg {
        background-color: #f8f9fa;
        border-right: 1px solid #e1e5e9;
    }
    
    @media (prefers-color-scheme: dark) {
        .css-1d391kg {
            background-color: #21262d;
            border-right-color: #30363d;
        }
    }
    
    /* Optimized button styles */
    .stButton button {
        color: #ffffff !important;
        background-color: #0066cc !important;
        border-color: #0066cc !important;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stButton button:hover {
        background-color: #0052a3 !important;
        border-color: #0052a3 !important;
        transform: translateY(-1px);
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Optimized input styles */
    .stTextInput input, .stTextArea textarea {
        color: #262730 !important;
        background-color: #ffffff !important;
        border: 2px solid #e1e5e9 !important;
        border-radius: 0.375rem;
        transition: border-color 0.2s ease;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #0066cc !important;
        box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1);
    }
    
    @media (prefers-color-scheme: dark) {
        .stTextInput input, .stTextArea textarea {
            color: #fafafa !important;
            background-color: #21262d !important;
            border-color: #30363d !important;
        }
        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: #58a6ff !important;
            box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.1);
        }
    }
    
    /* Improve alert and info box readability */
    .stAlert {
        border-radius: 0.5rem;
        border-left: 4px solid;
        font-weight: 500;
    }
    
    .stAlert[data-baseweb="notification"] {
        color: #262730 !important;
    }
    
    @media (prefers-color-scheme: dark) {
        .stAlert[data-baseweb="notification"] {
            color: #fafafa !important;
        }
    }
    
    /* Success message styles */
    .stSuccess {
        background-color: #d1f2eb !important;
        border-left-color: #28a745;
        color: #0d7956 !important;
    }
    
    /* Error message styles */
    .stError {
        background-color: #f8d7da !important;
        border-left-color: #dc3545;
        color: #721c24 !important;
    }
    
    /* Warning message styles */
    .stWarning {
        background-color: #fff3cd !important;
        border-left-color: #ffc107;
        color: #856404 !important;
    }
    
    /* Info message styles */
    .stInfo {
        background-color: #d1ecf1 !important;
        border-left-color: #17a2b8;
        color: #0c5460 !important;
    }
    
    @media (prefers-color-scheme: dark) {
        .stSuccess {
            background-color: #1a4c34 !important;
            color: #7ddfc3 !important;
        }
        .stError {
            background-color: #4a1a1f !important;
            color: #f5b7c1 !important;
        }
        .stWarning {
            background-color: #4a3a1f !important;
            color: #ffd966 !important;
        }
        .stInfo {
            background-color: #1f3a4a !important;
            color: #7dd3fc !important;
        }
    }
    
    /* Optimized code block styles */
    .stCode {
        background-color: #f8f9fa !important;
        color: #262730 !important;
        border: 1px solid #e1e5e9 !important;
        border-radius: 0.375rem;
        font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    }
    
    @media (prefers-color-scheme: dark) {
        .stCode {
            background-color: #21262d !important;
            color: #fafafa !important;
            border-color: #30363d !important;
        }
    }
    
    /* Progress bar styles */
    .stProgress > div > div > div {
        background-color: #0066cc !important;
    }
    
    /* Slider styles */
    .stSlider > div > div > div > div {
        color: #0066cc !important;
    }
    
    /* Ensure table content visibility */
    .stDataFrame, .stDataFrame table, .stDataFrame tbody, .stDataFrame thead {
        color: #262730 !important;
    }
    
    @media (prefers-color-scheme: dark) {
        .stDataFrame, .stDataFrame table, .stDataFrame tbody, .stDataFrame thead {
            color: #fafafa !important;
        }
    }
    
    /* Enhanced title styles */
    h1, h2, h3 {
        color: #262730 !important;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    @media (prefers-color-scheme: dark) {
        h1, h2, h3 {
            color: #fafafa !important;
        }
    }
    
    /* Chart container styles - Enhanced for Analytics Dashboard */
    .js-plotly-plot {
        border-radius: 0.5rem;
        border: 1px solid #e1e5e9;
        background-color: #ffffff !important;
    }
    
    @media (prefers-color-scheme: dark) {
        .js-plotly-plot {
            border-color: #30363d;
            background-color: #ffffff !important;
        }
    }
    
    /* ENHANCED Plotly chart text and styling fixes */
    .js-plotly-plot .plotly {
        background-color: #ffffff !important;
    }
    
    /* STRONGER Fix for Plotly chart titles and labels */
    .js-plotly-plot .gtitle, 
    .js-plotly-plot .xtitle, 
    .js-plotly-plot .ytitle,
    .js-plotly-plot .legend,
    .js-plotly-plot .axis text,
    .js-plotly-plot text,
    .js-plotly-plot .trace text,
    .js-plotly-plot tspan {
        fill: #000000 !important;
        color: #000000 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }
    
    /* Force white background for all Plotly charts */
    .js-plotly-plot .bg,
    .js-plotly-plot .plot-container,
    .js-plotly-plot .svg-container {
        fill: #ffffff !important;
        background-color: #ffffff !important;
    }
    
    /* Fix Plotly chart background and grid - Force white background */
    .js-plotly-plot .gridlayer .crisp {
        stroke: #cccccc !important;
        stroke-width: 1 !important;
    }
    
    /* Fix Plotly axis lines - make them dark and visible */
    .js-plotly-plot .xlines-above, 
    .js-plotly-plot .ylines-above,
    .js-plotly-plot .xlines-below, 
    .js-plotly-plot .ylines-below,
    .js-plotly-plot .zero-line {
        stroke: #000000 !important;
        stroke-width: 2 !important;
    }
    
    /* Fix Plotly legend text - force black text */
    .js-plotly-plot .legend .traces .legendtext,
    .js-plotly-plot .legend text {
        fill: #000000 !important;
        font-weight: 600 !important;
        font-size: 12px !important;
    }
    
    /* Fix Plotly hover labels - force dark text on light background */
    .js-plotly-plot .hoverlayer .hovertext {
        fill: #000000 !important;
        stroke: #000000 !important;
        background-color: #ffffff !important;
        border: 2px solid #000000 !important;
        font-weight: 600 !important;
    }
    
    /* Force all text elements to be black and bold */
    .js-plotly-plot * {
        color: #000000 !important;
    }
    
    /* Fix tick labels specifically */
    .js-plotly-plot .xtick text,
    .js-plotly-plot .ytick text,
    .js-plotly-plot .tick text {
        fill: #000000 !important;
        font-weight: 600 !important;
        font-size: 12px !important;
    }
    
    /* Fix axis titles specifically */
    .js-plotly-plot .xtitle text,
    .js-plotly-plot .ytitle text {
        fill: #000000 !important;
        font-weight: 700 !important;
        font-size: 14px !important;
    }
    
    /* Fix chart title specifically */
    .js-plotly-plot .gtitle text {
        fill: #000000 !important;
        font-weight: 700 !important;
        font-size: 16px !important;
    }
    
    /* Selectbox and dropdown styling */
    .stSelectbox > div > div {
        background-color: #ffffff !important;
        color: #262730 !important;
        border-color: #e1e5e9 !important;
    }
    
    @media (prefers-color-scheme: dark) {
        .stSelectbox > div > div {
            background-color: #21262d !important;
            color: #fafafa !important;
            border-color: #30363d !important;
        }
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        color: #262730 !important;
        background-color: #f8f9fa !important;
    }
    
    @media (prefers-color-scheme: dark) {
        .streamlit-expanderHeader {
            color: #fafafa !important;
            background-color: #21262d !important;
        }
    }
    </style>
    """