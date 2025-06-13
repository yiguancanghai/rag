"""
Streamlit UI - Document Q&A RAG system frontend
"""

import streamlit as st
import os
import sys
from typing import List, Dict, Any
import logging
import time
from pathlib import Path

# Add app root directory to path
sys.path.append(str(Path(__file__).parent))

from loader import DocumentLoader
from vectordb import VectorDatabase
from qa_chain import QAChain
from utils import (
    Timer, load_config, validate_config, format_file_size, 
    safe_filename, setup_logging, log_user_interaction
)

# Setup logging
setup_logging(level="INFO")
logger = logging.getLogger(__name__)


def initialize_session_state():
    """Initialize session state"""
    if 'config' not in st.session_state:
        st.session_state.config = load_config()
    
    if 'vector_db' not in st.session_state:
        st.session_state.vector_db = None
    
    if 'qa_chain' not in st.session_state:
        st.session_state.qa_chain = None
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'uploaded_files_info' not in st.session_state:
        st.session_state.uploaded_files_info = []
    
    if 'processing_status' not in st.session_state:
        st.session_state.processing_status = ""


def setup_page_config():
    """Setup page configuration"""
    config = st.session_state.config
    
    st.set_page_config(
        page_title=config.get('page_title', 'Document Q&A RAG Demo'),
        page_icon=config.get('page_icon', '📄🔍'),
        layout="wide",
        initial_sidebar_state="expanded"
    )


def display_sidebar():
    """Display sidebar"""
    with st.sidebar:
        st.title("📁 Document Upload")
        
        # Configuration check
        config_errors = validate_config(st.session_state.config)
        if config_errors:
            st.error("⚠️ Configuration Errors:")
            for error in config_errors:
                st.error(f"• {error}")
            return False
        
        # File upload
        uploaded_files = st.file_uploader(
            "Choose document files",
            type=['pdf', 'docx', 'txt'],
            accept_multiple_files=True,
            help="Support PDF, DOCX, TXT formats"
        )
        
        # Display uploaded file info
        if uploaded_files:
            st.subheader("📋 Uploaded Files")
            total_size = 0
            
            for file in uploaded_files:
                file_size = len(file.read())
                file.seek(0)  # Reset file pointer
                total_size += file_size
                
                st.write(f"• **{file.name}** ({format_file_size(file_size)})")
            
            st.info(f"Total Size: {format_file_size(total_size)}")
            
            # Rebuild vector database button
            if st.button("🔄 Rebuild Vector DB", type="primary"):
                return rebuild_vector_database(uploaded_files)
        
        # Database status
        st.subheader("💾 Database Status")
        if st.session_state.vector_db:
            stats = st.session_state.vector_db.get_stats()
            st.success("✅ Database Ready")
            st.json(stats)
        else:
            st.warning("⚠️ Database Not Initialized")
        
        # Settings panel
        st.subheader("⚙️ Settings")
        
        # Strict mode toggle
        strict_mode = st.checkbox(
            "Strict Mode",
            value=st.session_state.config.get('strict_mode', True),
            help="Strict mode only answers based on retrieved context"
        )
        
        # Number of retrieval results
        top_k = st.slider(
            "Top K Results",
            min_value=1,
            max_value=10,
            value=st.session_state.config.get('top_k_results', 5),
            help="Number of documents to retrieve from vector database"
        )
        
        # Update configuration
        if strict_mode != st.session_state.config.get('strict_mode') or \
           top_k != st.session_state.config.get('top_k_results'):
            st.session_state.config['strict_mode'] = strict_mode
            st.session_state.config['top_k_results'] = top_k
            
            # Reinitialize QA chain
            if st.session_state.vector_db:
                initialize_qa_chain()
        
        # Clear database button
        if st.button("🗑️ Clear Database"):
            clear_database()
        
        return True


def rebuild_vector_database(uploaded_files):
    """Rebuild vector database"""
    if not uploaded_files:
        st.error("Please upload files first")
        return False
    
    try:
        with st.spinner("🔄 Processing documents..."):
            log_user_interaction("rebuild_database", {
                'file_count': len(uploaded_files),
                'files': [f.name for f in uploaded_files]
            })
            config = st.session_state.config
            loader = DocumentLoader(
                chunk_size=config.get('chunk_size', 1000),
                chunk_overlap=config.get('chunk_overlap', 200)
            )
            file_list = []
            for file in uploaded_files:
                file_bytes = file.read()
                file_list.append((file_bytes, file.name))
            with Timer() as timer:
                documents = loader.load_multiple_files(file_list)
            
            if not documents:
                st.error("❌ Could not extract content from uploaded files")
                return False
            
            st.success(f"✅ Successfully loaded {len(documents)} document chunks")
            st.info(f"⏱️ Document processing time: {timer.format_time()}")
            
            vector_db = VectorDatabase(
                db_path=config.get('vector_db_path', './vector_db')
            )
            
            with Timer() as timer:
                success = vector_db.rebuild_from_documents(documents)
            
            if success:
                st.session_state.vector_db = vector_db
                st.success(f"✅ Vector database rebuilt successfully")
                st.info(f"⏱️ Vectorization time: {timer.format_time()}")
                
                initialize_qa_chain()
                
                st.session_state.uploaded_files_info = [
                    {'name': f.name, 'size': len(f.read())} for f in uploaded_files
                ]
                
                return True
            else:
                st.error("❌ Vector database rebuild failed")
                return False
                
    except Exception as e:
        logger.error(f"Error rebuilding database: {e}")
        st.error(f"❌ Error during processing: {str(e)}")
        return False


def initialize_qa_chain():
    """Initialize QA chain"""
    if not st.session_state.vector_db:
        st.error("Vector database not initialized")
        return False
    
    try:
        config = st.session_state.config
        
        qa_chain = QAChain(
            model_name=config.get('model_name', 'gpt-4o'),
            temperature=config.get('temperature', 0),
            max_tokens=config.get('max_tokens', 2000),
            strict_mode=config.get('strict_mode', True)
        )
        
        retriever = st.session_state.vector_db.get_retriever(
            k=config.get('top_k_results', 5)
        )
        
        success = qa_chain.setup_chain(retriever)
        
        if success:
            st.session_state.qa_chain = qa_chain
            logger.info("QA chain initialized successfully")
            return True
        else:
            st.error("❌ QA chain initialization failed")
            return False
            
    except Exception as e:
        logger.error(f"Error initializing QA chain: {e}")
        st.error(f"❌ QA chain initialization error: {str(e)}")
        return False


def clear_database():
    """Clear database"""
    if st.session_state.vector_db:
        success = st.session_state.vector_db.clear_database()
        if success:
            st.session_state.vector_db = None
            st.session_state.qa_chain = None
            st.session_state.chat_history = []
            st.session_state.uploaded_files_info = []
            st.success("✅ Database cleared")
        else:
            st.error("❌ Failed to clear database")
    else:
        st.warning("⚠️ Database not initialized")


def display_chat_interface():
    """Display chat interface"""
    st.title("💬 Intelligent Document Q&A")
    
    # Check system status
    if not st.session_state.vector_db or not st.session_state.qa_chain:
        st.warning("⚠️ Please upload documents and rebuild vector database first")
        return
    
    # Display chat history
    chat_container = st.container()
    
    with chat_container:
        for i, chat in enumerate(st.session_state.chat_history):
            # User question
            with st.chat_message("user"):
                st.write(chat['question'])
            
            # Assistant answer
            with st.chat_message("assistant"):
                st.write(chat['answer'])
                
                # Display metadata
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.caption(f"⏱️ {chat.get('response_time', 0)}s")
                with col2:
                    token_usage = chat.get('token_usage', {})
                    st.caption(f"🔢 {token_usage.get('total_tokens', 0)} tokens")
                with col3:
                    st.caption(f"📊 {len(chat.get('source_documents', []))} sources")
                
                # Source documents expandable panel
                if chat.get('source_documents'):
                    with st.expander("📚 View Sources", expanded=False):
                        display_sources(chat['source_documents'])
    
    # Question input
    question = st.chat_input("Enter your question...")
    
    if question:
        process_question(question)


def display_sources(source_documents: List[Dict[str, Any]]):
    """Display source documents"""
    for i, source in enumerate(source_documents):
        st.markdown(f"**📄 Source {i+1}:**")
        
        # File info
        col1, col2 = st.columns(2)
        with col1:
            st.caption(f"📁 File: {source.get('file_name', 'Unknown')}")
        with col2:
            st.caption(f"📖 Page: {source.get('page_num', 'N/A')}")
        
        # Document content
        content = source.get('content', '')
        if len(content) > 500:
            content = content[:500] + "..."
        
        st.markdown(f"```\n{content}\n```")
        
        # Similarity score (if available)
        if 'similarity_score' in source:
            st.caption(f"🎯 Similarity: {source['similarity_score']:.3f}")
        
        if i < len(source_documents) - 1:
            st.divider()


def process_question(question: str):
    """Process question"""
    if not question.strip():
        return
    
    # Log user interaction
    log_user_interaction("ask_question", {'question': question})
    
    # Display user question
    with st.chat_message("user"):
        st.write(question)
    
    # Process and display answer
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            with Timer() as timer:
                result = st.session_state.qa_chain.ask_question(question)
        
        # Display answer
        answer = result.get('answer', 'Could not get answer')
        st.write(answer)
        
        # Display metadata
        col1, col2, col3 = st.columns(3)
        with col1:
            st.caption(f"⏱️ {result.get('response_time', 0)}s")
        with col2:
            token_usage = result.get('token_usage', {})
            st.caption(f"🔢 {token_usage.get('total_tokens', 0)} tokens")
        with col3:
            source_count = len(result.get('source_documents', []))
            st.caption(f"📊 {source_count} sources")
        
        # Source documents
        if result.get('source_documents'):
            with st.expander("📚 View Sources", expanded=False):
                display_sources(result['source_documents'])
        
        # Save to chat history
        chat_entry = {
            'question': question,
            'answer': answer,
            'response_time': result.get('response_time', 0),
            'token_usage': result.get('token_usage', {}),
            'source_documents': result.get('source_documents', []),
            'timestamp': time.time()
        }
        
        st.session_state.chat_history.append(chat_entry)


def display_statistics():
    """Display statistics"""
    if len(st.session_state.chat_history) > 0:
        st.subheader("📊 Session Statistics")
        
        total_questions = len(st.session_state.chat_history)
        total_tokens = sum(
            chat.get('token_usage', {}).get('total_tokens', 0) 
            for chat in st.session_state.chat_history
        )
        avg_response_time = sum(
            chat.get('response_time', 0) 
            for chat in st.session_state.chat_history
        ) / total_questions
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Questions", total_questions)
        with col2:
            st.metric("Total Tokens", total_tokens)
        with col3:
            st.metric("Avg Response Time", f"{avg_response_time:.1f}s")


def main():
    """Main function"""
    # Initialize
    initialize_session_state()
    setup_page_config()
    
    # Check OpenAI API key
    if not st.session_state.config.get('openai_api_key'):
        st.error("""
        ⚠️ **OpenAI API Key Not Set**
        
        Please create a `.env` file and add your API key:
        ```
        OPENAI_API_KEY=your_api_key_here
        ```
        """)
        return
    
    # Set OpenAI API key
    os.environ['OPENAI_API_KEY'] = st.session_state.config['openai_api_key']
    
    # Display sidebar
    sidebar_ok = display_sidebar()
    
    if sidebar_ok:
        # Main content area
        display_chat_interface()
        
        # Statistics
        with st.expander("📊 Statistics", expanded=False):
            display_statistics()
        
        # Footer
        st.markdown("---")
        st.markdown(
            "🚀 **Document Q&A RAG Demo** | "
            "Powered by LangChain, OpenAI GPT-4o, FAISS & Streamlit"
        )


if __name__ == "__main__":
    main() 