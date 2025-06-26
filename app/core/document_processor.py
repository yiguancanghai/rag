import os
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime

import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
    UnstructuredPowerPointLoader,
    UnstructuredExcelLoader
)

from utils.logger import logger
from utils.config import Config


class DocumentProcessor:
    """Handle document uploading, processing, and text extraction"""
    
    def __init__(self):
        self.config = Config()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.CHUNK_SIZE,
            chunk_overlap=self.config.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
    def get_file_hash(self, file_content: bytes) -> str:
        """Generate hash for file content to avoid duplicates"""
        return hashlib.md5(file_content).hexdigest()
    
    def save_uploaded_file(self, uploaded_file) -> Optional[Path]:
        """Save uploaded file to documents directory"""
        try:
            # Create file hash to avoid duplicates
            file_content = uploaded_file.read()
            file_hash = self.get_file_hash(file_content)
            uploaded_file.seek(0)  # Reset file pointer
            
            # Create filename with hash
            file_extension = Path(uploaded_file.name).suffix
            safe_filename = f"{file_hash}_{uploaded_file.name}"
            file_path = self.config.DOCUMENTS_DIR / safe_filename
            
            # Check if file already exists
            if file_path.exists():
                logger.info(f"File already exists: {safe_filename}")
                return file_path
            
            # Save file
            with open(file_path, "wb") as f:
                f.write(file_content)
            
            logger.info(f"File saved: {safe_filename}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving file {uploaded_file.name}: {str(e)}")
            return None
    
    def load_document(self, file_path: Path) -> List[Document]:
        """Load and parse document based on file type"""
        try:
            file_extension = file_path.suffix.lower()
            
            # Select appropriate loader based on file type
            if file_extension == '.pdf':
                loader = PyPDFLoader(str(file_path))
            elif file_extension in ['.docx', '.doc']:
                loader = Docx2txtLoader(str(file_path))
            elif file_extension == '.txt':
                loader = TextLoader(str(file_path), encoding='utf-8')
            elif file_extension == '.md':
                loader = UnstructuredMarkdownLoader(str(file_path))
            elif file_extension in ['.pptx', '.ppt']:
                loader = UnstructuredPowerPointLoader(str(file_path))
            elif file_extension in ['.xlsx', '.xls']:
                loader = UnstructuredExcelLoader(str(file_path))
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
            
            # Load documents
            documents = loader.load()
            
            # Add metadata
            for doc in documents:
                doc.metadata.update({
                    'source_file': file_path.name,
                    'file_type': file_extension,
                    'upload_date': datetime.now().isoformat(),
                    'file_size': file_path.stat().st_size
                })
            
            logger.info(f"Loaded {len(documents)} document chunks from {file_path.name}")
            return documents
            
        except Exception as e:
            logger.error(f"Error loading document {file_path}: {str(e)}")
            return []
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into smaller chunks"""
        try:
            split_docs = self.text_splitter.split_documents(documents)
            logger.info(f"Split {len(documents)} documents into {len(split_docs)} chunks")
            return split_docs
        except Exception as e:
            logger.error(f"Error splitting documents: {str(e)}")
            return documents
    
    def process_uploaded_files(self, uploaded_files) -> Tuple[List[Document], Dict[str, str]]:
        """Process multiple uploaded files and return documents and status"""
        all_documents = []
        processing_status = {}
        
        for uploaded_file in uploaded_files:
            try:
                # Validate file size
                file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
                if file_size_mb > self.config.MAX_UPLOAD_SIZE_MB:
                    processing_status[uploaded_file.name] = f"File too large: {file_size_mb:.2f}MB"
                    continue
                
                # Validate file type
                file_extension = Path(uploaded_file.name).suffix.lower().replace('.', '')
                if file_extension not in self.config.SUPPORTED_FILE_TYPES:
                    processing_status[uploaded_file.name] = f"Unsupported file type: {file_extension}"
                    continue
                
                # Save and process file
                file_path = self.save_uploaded_file(uploaded_file)
                if not file_path:
                    processing_status[uploaded_file.name] = "Failed to save file"
                    continue
                
                # Load and split document
                documents = self.load_document(file_path)
                if not documents:
                    processing_status[uploaded_file.name] = "Failed to load document"
                    continue
                
                split_documents = self.split_documents(documents)
                all_documents.extend(split_documents)
                
                processing_status[uploaded_file.name] = f"Successfully processed ({len(split_documents)} chunks)"
                
            except Exception as e:
                processing_status[uploaded_file.name] = f"Error: {str(e)}"
                logger.error(f"Error processing {uploaded_file.name}: {str(e)}")
        
        return all_documents, processing_status
    
    def get_document_metadata(self, documents: List[Document]) -> Dict:
        """Extract metadata summary from processed documents"""
        if not documents:
            return {}
        
        metadata = {
            'total_chunks': len(documents),
            'total_characters': sum(len(doc.page_content) for doc in documents),
            'source_files': list(set(doc.metadata.get('source_file', 'Unknown') for doc in documents)),
            'file_types': list(set(doc.metadata.get('file_type', 'Unknown') for doc in documents)),
            'processing_date': datetime.now().isoformat()
        }
        
        return metadata