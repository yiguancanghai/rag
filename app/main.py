import streamlit as st
import os
from pathlib import Path

# Add the app directory to Python path
import sys
sys.path.append(str(Path(__file__).parent))

from core.document_processor import DocumentProcessor
from core.rag_engine import RAGEngine
from core.chat_manager import ChatManager
from ui.components.sidebar import render_sidebar, render_document_stats_chart, render_chat_analytics, render_favorites_section
from ui.components.chat_interface import render_chat_interface, render_example_questions, render_search_interface
from ui.components.document_manager import render_document_manager
from utils.config import Config, get_custom_css
from utils.logger import logger


def initialize_session_state():
    """Initialize Streamlit session state"""
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
        st.session_state.rag_engine = None
        st.session_state.doc_processor = None
        st.session_state.chat_manager = None


def initialize_components():
    """Initialize core components"""
    try:
        # Validate configuration
        Config.validate_config()
        
        # Initialize components
        if st.session_state.rag_engine is None:
            st.session_state.rag_engine = RAGEngine()
        
        if st.session_state.doc_processor is None:
            st.session_state.doc_processor = DocumentProcessor()
        
        if st.session_state.chat_manager is None:
            st.session_state.chat_manager = ChatManager()
        
        return True
        
    except Exception as e:
        st.error(f"❌ Initialization Error: {str(e)}")
        
        if "OPENAI_API_KEY" in str(e):
            st.info("💡 Please set your OpenAI API key in the .env file or as an environment variable.")
            
            with st.expander("🔧 Setup Instructions"):
                st.markdown("""
                ### Setting up your API Key:
                
                1. **Option 1: Environment Variable**
                   ```bash
                   export OPENAI_API_KEY="your-api-key-here"
                   ```
                
                2. **Option 2: .env File**
                   - Copy `config/.env.example` to `config/.env`
                   - Add your API key: `OPENAI_API_KEY=your-api-key-here`
                
                3. **Get an API Key:**
                   - Visit [OpenAI Platform](https://platform.openai.com/api-keys)
                   - Create a new API key
                   - Copy it to your configuration
                """)
        
        return False


def render_main_content(page: str, settings: dict):
    """Render main content based on selected page"""
    
    rag_engine = st.session_state.rag_engine
    doc_processor = st.session_state.doc_processor
    chat_manager = st.session_state.chat_manager
    
    if page == "💬 Chat":
        render_chat_page(rag_engine, chat_manager, settings)
    
    elif page == "📄 Document Management":
        render_document_manager(doc_processor, rag_engine)
    
    elif page == "⭐ Favorites":
        render_favorites_section(chat_manager)
    
    elif page == "📊 Analytics":
        render_analytics_page(rag_engine, chat_manager)


def render_chat_page(rag_engine: RAGEngine, chat_manager: ChatManager, settings: dict):
    """Render the chat page"""
    
    # Main chat interface
    render_chat_interface(rag_engine, chat_manager, settings)
    
    # Additional sections
    col1, col2 = st.columns([2, 1])
    
    with col1:
        render_search_interface(chat_manager)
    
    with col2:
        render_example_questions()


def render_analytics_page(rag_engine: RAGEngine, chat_manager: ChatManager):
    """Render analytics and statistics page"""
    
    st.header("📊 Analytics Dashboard")
    
    # Document statistics
    st.subheader("📄 Document Statistics")
    render_document_stats_chart(rag_engine)
    
    st.markdown("---")
    
    # Chat analytics
    st.subheader("💬 Chat Analytics")
    render_chat_analytics(chat_manager)
    
    st.markdown("---")
    
    # System information
    render_system_info()


def render_system_info():
    """Render system information"""
    
    st.subheader("⚙️ System Information")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Python Version", f"{sys.version_info.major}.{sys.version_info.minor}")
    
    with col2:
        st.metric("Streamlit Version", st.__version__)
    
    with col3:
        st.metric("Vector DB", "ChromaDB")
    
    # Configuration info
    with st.expander("🔧 Configuration"):
        config_info = {
            "Chunk Size": Config.CHUNK_SIZE,
            "Chunk Overlap": Config.CHUNK_OVERLAP,
            "Temperature": Config.TEMPERATURE,
            "Max Tokens": Config.MAX_TOKENS,
            "Max Upload Size (MB)": Config.MAX_UPLOAD_SIZE_MB
        }
        
        for key, value in config_info.items():
            st.text(f"{key}: {value}")


def main():
    """Main application entry point"""
    
    # Page configuration
    st.set_page_config(
        page_title="IntelliDocs Pro",
        page_icon="🔧",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply custom CSS styles to fix font display issues
    st.markdown(get_custom_css(), unsafe_allow_html=True)
    
    # Initialize session state
    initialize_session_state()
    
    # Initialize components
    if not initialize_components():
        st.stop()
    
    # Render sidebar and get settings
    settings = render_sidebar(
        st.session_state.rag_engine,
        st.session_state.chat_manager
    )
    
    # Render main content
    render_main_content(settings["page"], settings)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "🔧 **IntelliDocs Pro** - Enterprise Document Q&A System | "
        "Built with Streamlit, LangChain, and OpenAI"
    )


if __name__ == "__main__":
    main()