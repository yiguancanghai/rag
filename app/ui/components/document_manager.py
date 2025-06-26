import streamlit as st
from typing import List, Dict
import pandas as pd
from pathlib import Path

from core.document_processor import DocumentProcessor
from core.rag_engine import RAGEngine


def render_document_manager(doc_processor: DocumentProcessor, rag_engine: RAGEngine):
    """Render document management interface"""
    
    st.header("📄 Document Management")
    
    # Upload section
    render_upload_section(doc_processor, rag_engine)
    
    st.markdown("---")
    
    # Document statistics
    render_document_statistics(rag_engine)
    
    st.markdown("---")
    
    # Document preview and management
    render_document_list()


def render_upload_section(doc_processor: DocumentProcessor, rag_engine: RAGEngine):
    """Render document upload interface"""
    
    st.subheader("📤 Upload Documents")
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Choose documents to upload",
        type=doc_processor.config.SUPPORTED_FILE_TYPES,
        accept_multiple_files=True,
        help=f"Supported formats: {', '.join(doc_processor.config.SUPPORTED_FILE_TYPES)}"
    )
    
    # Upload settings
    col1, col2 = st.columns(2)
    
    with col1:
        chunk_size = st.slider(
            "Chunk Size",
            min_value=500,
            max_value=2000,
            value=doc_processor.config.CHUNK_SIZE,
            help="Size of text chunks for processing"
        )
    
    with col2:
        chunk_overlap = st.slider(
            "Chunk Overlap",
            min_value=50,
            max_value=500,
            value=doc_processor.config.CHUNK_OVERLAP,
            help="Overlap between consecutive chunks"
        )
    
    # Process uploaded files
    if uploaded_files:
        if st.button("🚀 Process Documents", type="primary"):
            process_uploaded_documents(uploaded_files, doc_processor, rag_engine, chunk_size, chunk_overlap)


def process_uploaded_documents(uploaded_files, doc_processor: DocumentProcessor, 
                             rag_engine: RAGEngine, chunk_size: int, chunk_overlap: int):
    """Process and add uploaded documents to the system"""
    
    # Update text splitter settings
    doc_processor.text_splitter = doc_processor.text_splitter.__class__(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_files = len(uploaded_files)
    
    try:
        # Process documents
        status_text.text("Processing documents...")
        documents, processing_status = doc_processor.process_uploaded_files(uploaded_files)
        
        progress_bar.progress(0.5)
        
        if documents:
            # Add to vector store
            status_text.text("Adding documents to knowledge base...")
            success = rag_engine.add_documents(documents)
            
            progress_bar.progress(1.0)
            
            if success:
                st.success(f"✅ Successfully processed {len(documents)} document chunks!")
                
                # Display processing results
                st.subheader("📊 Processing Results")
                
                results_df = pd.DataFrame([
                    {"File": filename, "Status": status}
                    for filename, status in processing_status.items()
                ])
                
                st.dataframe(results_df, use_container_width=True)
                
                # Document metadata
                metadata = doc_processor.get_document_metadata(documents)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Chunks", metadata.get('total_chunks', 0))
                
                with col2:
                    st.metric("Total Characters", f"{metadata.get('total_characters', 0):,}")
                
                with col3:
                    st.metric("Source Files", len(metadata.get('source_files', [])))
                
            else:
                st.error("❌ Failed to add documents to knowledge base")
        else:
            st.error("❌ No documents were successfully processed")
            
            # Show processing errors
            st.subheader("❌ Processing Errors")
            for filename, status in processing_status.items():
                st.error(f"**{filename}:** {status}")
    
    except Exception as e:
        st.error(f"❌ Error processing documents: {str(e)}")
    
    finally:
        progress_bar.empty()
        status_text.empty()


def render_document_statistics(rag_engine: RAGEngine):
    """Render document collection statistics"""
    
    st.subheader("📊 Collection Statistics")
    
    try:
        stats = rag_engine.get_collection_stats()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Documents in Database",
                stats.get("total_documents", 0),
                help="Total number of document chunks in the vector database"
            )
        
        with col2:
            st.metric(
                "Collection Name",
                stats.get("collection_name", "Unknown"),
                help="Name of the active document collection"
            )
        
        # Additional statistics if available
        if stats.get("total_documents", 0) > 0:
            st.info("💡 Documents are ready for querying!")
        else:
            st.warning("⚠️ No documents in the database. Upload some documents to get started.")
    
    except Exception as e:
        st.error(f"Error loading statistics: {str(e)}")


def render_document_list():
    """Render list of uploaded documents"""
    
    st.subheader("📋 Uploaded Documents")
    
    try:
        # Get list of files in documents directory
        docs_dir = Path("./data/documents")
        
        if not docs_dir.exists():
            st.info("📁 No documents directory found")
            return
        
        document_files = list(docs_dir.glob("*"))
        document_files = [f for f in document_files if f.is_file()]
        
        if not document_files:
            st.info("📄 No documents uploaded yet")
            return
        
        # Create DataFrame for display
        file_data = []
        for file_path in document_files:
            try:
                stat = file_path.stat()
                file_data.append({
                    "Filename": file_path.name,
                    "Size (KB)": round(stat.st_size / 1024, 2),
                    "Modified": pd.to_datetime(stat.st_mtime, unit='s').strftime('%Y-%m-%d %H:%M'),
                    "Extension": file_path.suffix.lower()
                })
            except Exception as e:
                st.error(f"Error reading file {file_path.name}: {str(e)}")
        
        if file_data:
            df = pd.DataFrame(file_data)
            
            # Display table
            st.dataframe(df, use_container_width=True)
            
            # File type distribution
            if len(df) > 1:
                st.subheader("📈 File Type Distribution")
                
                type_counts = df['Extension'].value_counts()
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.bar_chart(type_counts)
                
                with col2:
                    for ext, count in type_counts.items():
                        st.metric(f"{ext.upper()} files", count)
        
    except Exception as e:
        st.error(f"Error loading document list: {str(e)}")


def render_document_preview(filename: str):
    """Render document preview"""
    
    st.subheader(f"👀 Preview: {filename}")
    
    try:
        file_path = Path("./data/documents") / filename
        
        if not file_path.exists():
            st.error("File not found")
            return
        
        file_extension = file_path.suffix.lower()
        
        # Preview based on file type
        if file_extension == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                st.text_area("Content", content, height=300)
        
        elif file_extension == '.md':
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                st.markdown(content)
        
        else:
            st.info(f"Preview not available for {file_extension} files")
            
            # Show file info instead
            stat = file_path.stat()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("File Size", f"{stat.st_size / 1024:.2f} KB")
            
            with col2:
                st.metric("Last Modified", 
                         pd.to_datetime(stat.st_mtime, unit='s').strftime('%Y-%m-%d %H:%M'))
    
    except Exception as e:
        st.error(f"Error previewing file: {str(e)}")


def render_batch_operations():
    """Render batch operations for document management"""
    
    st.subheader("🔧 Batch Operations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Clear All Documents", help="Remove all documents from storage"):
            if st.session_state.get("confirm_clear_docs", False):
                # Actually clear documents
                try:
                    docs_dir = Path("./data/documents")
                    if docs_dir.exists():
                        for file_path in docs_dir.glob("*"):
                            if file_path.is_file():
                                file_path.unlink()
                    
                    st.success("All documents cleared!")
                    st.session_state["confirm_clear_docs"] = False
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error clearing documents: {str(e)}")
                    
            else:
                st.session_state["confirm_clear_docs"] = True
                st.rerun()
    
    with col2:
        if st.button("📊 Rebuild Index", help="Rebuild the vector database index"):
            st.info("Index rebuild functionality would be implemented here")
    
    # Confirmation dialog
    if st.session_state.get("confirm_clear_docs", False):
        st.warning("⚠️ Are you sure you want to delete all documents? This action cannot be undone.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ Yes, Clear All"):
                # Trigger the actual clearing
                st.rerun()
        
        with col2:
            if st.button("❌ Cancel"):
                st.session_state["confirm_clear_docs"] = False
                st.rerun()