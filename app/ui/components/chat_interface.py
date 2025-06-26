import streamlit as st
from typing import Dict, List
import time

from core.rag_engine import RAGEngine
from core.chat_manager import ChatManager


def render_chat_interface(rag_engine: RAGEngine, chat_manager: ChatManager, settings: Dict):
    """Render the main chat interface"""
    
    st.header("💬 Document Q&A Chat")
    
    # Check if documents are available
    collection_stats = rag_engine.get_collection_stats()
    if collection_stats.get("total_documents", 0) == 0:
        st.warning("⚠️ No documents uploaded yet. Please upload documents first in the Document Management section.")
        return
    
    # Display chat history
    render_chat_history(chat_manager, settings)
    
    # Chat input
    render_chat_input(rag_engine, chat_manager, settings)


def render_chat_history(chat_manager: ChatManager, settings: Dict):
    """Render chat history with messages"""
    
    chat_history = chat_manager.get_chat_history()
    
    if not chat_history:
        st.info("👋 Welcome! Ask me anything about your documents.")
        return
    
    # Create container for chat messages
    chat_container = st.container()
    
    with chat_container:
        for message in chat_history:
            render_message(message, chat_manager, settings)


def render_message(message: Dict, chat_manager: ChatManager, settings: Dict):
    """Render a single message"""
    
    if message["role"] == "user":
        render_user_message(message)
    else:
        render_assistant_message(message, chat_manager, settings)


def render_user_message(message: Dict):
    """Render user message"""
    with st.chat_message("user"):
        st.write(message["content"])
        st.caption(f"🕒 {message['timestamp'][:19].replace('T', ' ')}")


def render_assistant_message(message: Dict, chat_manager: ChatManager, settings: Dict):
    """Render assistant message with metadata"""
    
    with st.chat_message("assistant"):
        # Main answer
        st.write(message["content"])
        
        # Metadata
        metadata = message.get("metadata", {})
        
        # Confidence score
        if settings.get("show_confidence", True) and "confidence_score" in metadata:
            confidence = metadata["confidence_score"]
            confidence_color = get_confidence_color(confidence)
            st.markdown(f"**Confidence:** :color[{confidence_color}][{confidence:.1%}]")
        
        # Source documents
        if settings.get("show_sources", True) and "source_documents" in metadata:
            render_source_documents(metadata["source_documents"])
        
        # Action buttons
        render_message_actions(message, chat_manager)
        
        # Timestamp
        st.caption(f"🕒 {message['timestamp'][:19].replace('T', ' ')}")


def render_source_documents(source_docs: List[Dict]):
    """Render source documents section"""
    
    if not source_docs:
        return
    
    with st.expander(f"📚 Source Documents ({len(source_docs)})"):
        for i, doc in enumerate(source_docs, 1):
            st.markdown(f"**Source {i}:** {doc.get('source', 'Unknown')}")
            
            if doc.get('page') != 'N/A':
                st.markdown(f"**Page:** {doc.get('page')}")
            
            st.markdown(f"**Content Preview:**")
            st.text(doc.get('content', ''))
            
            if i < len(source_docs):
                st.markdown("---")


def render_message_actions(message: Dict, chat_manager: ChatManager):
    """Render action buttons for a message"""
    
    col1, col2, col3 = st.columns([1, 1, 4])
    
    with col1:
        if st.button("⭐", key=f"fav_{message['id']}", help="Add to favorites"):
            if chat_manager.add_to_favorites(message['id']):
                st.success("Added to favorites!")
                time.sleep(1)
                st.rerun()
    
    with col2:
        if st.button("📋", key=f"copy_{message['id']}", help="Copy to clipboard"):
            st.code(message['content'])
            st.success("Content displayed above!")


def render_chat_input(rag_engine: RAGEngine, chat_manager: ChatManager, settings: Dict):
    """Render chat input and handle user queries"""
    
    # Chat input
    user_question = st.chat_input("Ask a question about your documents...")
    
    if user_question:
        # Add user message to history
        chat_manager.add_message("user", user_question)
        
        # Display user message immediately
        with st.chat_message("user"):
            st.write(user_question)
        
        # Generate response
        with st.chat_message("assistant"):
            # Create placeholder for streaming response
            response_placeholder = st.empty()
            
            # Query the RAG system
            with st.spinner("🤔 Thinking..."):
                result = rag_engine.query(
                    question=user_question,
                    k=settings.get("k_docs", 4),
                    stream_container=response_placeholder if settings.get("enable_streaming", True) else None
                )
            
            # Display final response if not streaming
            if not settings.get("enable_streaming", True):
                response_placeholder.write(result["answer"])
            
            # Add response to chat history
            chat_manager.add_qa_pair(
                question=user_question,
                answer=result["answer"],
                source_docs=result["source_documents"],
                confidence_score=result["confidence_score"]
            )
        
        # Rerun to refresh the interface
        st.rerun()


def get_confidence_color(confidence: float) -> str:
    """Get color based on confidence score"""
    if confidence >= 0.8:
        return "green"
    elif confidence >= 0.6:
        return "orange"
    else:
        return "red"


def render_example_questions():
    """Render example questions for users"""
    
    st.subheader("💡 Example Questions")
    
    example_questions = [
        "What is the main topic of the uploaded documents?",
        "Can you summarize the key points?",
        "What are the conclusions or recommendations?",
        "Are there any specific dates or numbers mentioned?",
        "What problems does this document address?"
    ]
    
    for question in example_questions:
        if st.button(f"💬 {question}", key=f"example_{hash(question)}"):
            st.session_state.example_question = question
            st.rerun()


def render_search_interface(chat_manager: ChatManager):
    """Render search interface for chat history"""
    
    st.subheader("🔍 Search Chat History")
    
    search_query = st.text_input("Search previous conversations...")
    
    if search_query:
        results = chat_manager.search_history(search_query)
        
        if results:
            st.write(f"Found {len(results)} matching messages:")
            
            for message in results:
                with st.expander(f"{message['role'].title()}: {message['content'][:100]}..."):
                    st.write(message['content'])
                    st.caption(f"🕒 {message['timestamp'][:19].replace('T', ' ')}")
        else:
            st.info("No matching messages found.")
    else:
        st.info("Enter a search term to find previous conversations.")