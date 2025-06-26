import streamlit as st
from typing import Optional
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from core.rag_engine import RAGEngine
from core.chat_manager import ChatManager


def render_sidebar(rag_engine: RAGEngine, chat_manager: ChatManager) -> dict:
    """Render sidebar with navigation and controls"""
    
    with st.sidebar:
        st.title("🔧 IntelliDocs Pro")
        st.markdown("---")
        
        # Navigation
        page = st.selectbox(
            "Navigation",
            ["💬 Chat", "📄 Document Management", "⭐ Favorites", "📊 Analytics"],
            key="navigation"
        )
        
        st.markdown("---")
        
        # Document Statistics
        st.subheader("📊 Document Stats")
        collection_stats = rag_engine.get_collection_stats()
        st.metric("Total Documents", collection_stats.get("total_documents", 0))
        
        # Chat Statistics
        chat_stats = chat_manager.get_chat_statistics()
        st.metric("Total Questions", chat_stats.get("user_messages", 0))
        st.metric("Favorites", chat_stats.get("favorites_count", 0))
        
        st.markdown("---")
        
        # Quick Actions
        st.subheader("⚡ Quick Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear Chat", help="Clear chat history"):
                if chat_manager.clear_history():
                    st.success("Chat cleared!")
                    st.rerun()
        
        with col2:
            if st.button("🔄 Reset DB", help="Clear document database"):
                if rag_engine.clear_collection():
                    st.success("Database reset!")
                    st.rerun()
        
        st.markdown("---")
        
        # Settings
        st.subheader("⚙️ Settings")
        
        # Retrieval settings
        k_docs = st.slider(
            "Documents to Retrieve",
            min_value=1,
            max_value=10,
            value=4,
            help="Number of similar documents to retrieve for each query"
        )
        
        # Temperature setting
        temperature = st.slider(
            "Response Creativity",
            min_value=0.0,
            max_value=1.0,
            value=0.1,
            step=0.1,
            help="Higher values make responses more creative but less focused"
        )
        
        # Advanced settings expander
        with st.expander("🔧 Advanced Settings"):
            show_sources = st.checkbox("Show Source Documents", value=True)
            show_confidence = st.checkbox("Show Confidence Score", value=True)
            enable_streaming = st.checkbox("Enable Response Streaming", value=True)
        
        # Return settings
        return {
            "page": page,
            "k_docs": k_docs,
            "temperature": temperature,
            "show_sources": show_sources,
            "show_confidence": show_confidence,
            "enable_streaming": enable_streaming
        }


def render_document_stats_chart(rag_engine: RAGEngine):
    """Render document statistics chart"""
    try:
        stats = rag_engine.get_collection_stats()
        
        if stats.get("total_documents", 0) > 0:
            # Create a simple bar chart with better styling
            fig = go.Figure(data=[
                go.Bar(
                    x=["Documents"],
                    y=[stats["total_documents"]],
                    marker_color="#0066cc",
                    text=[stats["total_documents"]],
                    textposition="auto",
                    textfont=dict(color="white", size=14, family="Arial Black")
                )
            ])
            
            fig.update_layout(
                title={
                    'text': "Document Collection",
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 18, 'color': '#000000', 'family': 'Arial Black'}
                },
                height=280,
                showlegend=False,
                plot_bgcolor='#ffffff',
                paper_bgcolor='#ffffff',
                font=dict(color='#000000', family='Arial', size=12),
                xaxis=dict(
                    showgrid=False,
                    zeroline=False,
                    showline=True,
                    linecolor='#000000',
                    linewidth=2,
                    tickfont=dict(color='#000000', size=12, family='Arial Black')
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='#cccccc',
                    gridwidth=1,
                    zeroline=False,
                    showline=True,
                    linecolor='#000000',
                    linewidth=2,
                    tickfont=dict(color='#000000', size=12, family='Arial Black')
                ),
                margin=dict(l=40, r=40, t=60, b=40)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📄 No documents uploaded yet")
            
    except Exception as e:
        st.error(f"Error loading document stats: {str(e)}")


def render_chat_analytics(chat_manager: ChatManager):
    """Render chat analytics charts"""
    try:
        chat_history = chat_manager.get_chat_history()
        
        if not chat_history:
            st.info("💬 No chat history available")
            return
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame(chat_history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['date'] = df['timestamp'].dt.date
        
        # Messages per day
        daily_messages = df.groupby(['date', 'role']).size().unstack(fill_value=0)
        
        if not daily_messages.empty:
            # Create better styled bar chart with increased size
            fig = px.bar(
                daily_messages.reset_index(),
                x='date',
                y=daily_messages.columns.tolist(),
                title="Messages per Day",
                labels={'value': 'Message Count', 'date': 'Date'},
                color_discrete_sequence=['#0066cc', '#ff6b6b']
            )
            
            fig.update_layout(
                title={
                    'text': "Messages per Day",
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 20, 'color': '#000000', 'family': 'Arial Black'}
                },
                height=450,  # Increased height for better visibility
                width=None,  # Use full container width
                plot_bgcolor='#ffffff',
                paper_bgcolor='#ffffff',
                font=dict(color='#000000', family='Arial', size=14),
                legend=dict(
                    font=dict(color='#000000', size=14, family='Arial Black'),
                    bgcolor='#ffffff',
                    bordercolor='#000000',
                    borderwidth=2,
                    orientation="h",  # Horizontal legend for more space
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                xaxis=dict(
                    showgrid=False,
                    zeroline=False,
                    showline=True,
                    linecolor='#000000',
                    linewidth=2,
                    tickfont=dict(color='#000000', size=14, family='Arial Black'),
                    title_font=dict(color='#000000', size=16, family='Arial Black'),
                    tickangle=45  # Angled dates for better readability
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='#cccccc',
                    gridwidth=1,
                    zeroline=False,
                    showline=True,
                    linecolor='#000000',
                    linewidth=2,
                    tickfont=dict(color='#000000', size=14, family='Arial Black'),
                    title_font=dict(color='#000000', size=16, family='Arial Black')
                ),
                margin=dict(l=70, r=20, t=80, b=80)  # Adjusted margins for better spacing
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Role distribution pie chart
        role_counts = df['role'].value_counts()
        
        if not role_counts.empty:
            fig = px.pie(
                values=role_counts.values,
                names=role_counts.index,
                title="Message Distribution",
                color_discrete_sequence=['#0066cc', '#ff6b6b', '#28a745', '#ffc107']
            )
            
            fig.update_layout(
                title={
                    'text': "Message Distribution",
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 20, 'color': '#000000', 'family': 'Arial Black'}
                },
                height=400,  # Increased height for better visibility
                width=None,  # Use full container width
                plot_bgcolor='#ffffff',
                paper_bgcolor='#ffffff',
                font=dict(color='#000000', family='Arial', size=14),
                legend=dict(
                    font=dict(color='#000000', size=14, family='Arial Black'),
                    bgcolor='#ffffff',
                    bordercolor='#000000',
                    borderwidth=2,
                    orientation="v",  # Vertical legend
                    yanchor="middle",
                    y=0.5,
                    xanchor="left",
                    x=1.05
                ),
                margin=dict(l=40, r=100, t=60, b=40)  # More right margin for legend
            )
            
            fig.update_traces(
                textfont=dict(color='#000000', size=16, family='Arial Black'),
                textinfo='label+percent',
                textposition='inside',
                pull=[0.1 if i == role_counts.idxmax() else 0 for i in range(len(role_counts))]  # Highlight largest segment
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
    except Exception as e:
        st.error(f"Error loading chat analytics: {str(e)}")


def render_favorites_section(chat_manager: ChatManager):
    """Render favorites management section"""
    st.subheader("⭐ Favorite Q&A Pairs")
    
    favorites = chat_manager.get_favorites()
    
    if not favorites:
        st.info("🌟 No favorites yet. Add some by clicking the star icon next to answers!")
        return
    
    for favorite in favorites:
        with st.expander(f"⭐ {favorite.get('title', 'Untitled')}"):
            if favorite.get('question'):
                st.markdown(f"**Question:** {favorite['question']}")
            
            st.markdown(f"**Answer:** {favorite['answer']}")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.caption(f"Added: {favorite.get('added_to_favorites', 'Unknown')}")
            
            with col2:
                if st.button(f"🗑️ Remove", key=f"remove_{favorite['id']}"):
                    if chat_manager.remove_from_favorites(favorite['id']):
                        st.success("Removed from favorites!")
                        st.rerun()
                    else:
                        st.error("Failed to remove from favorites")