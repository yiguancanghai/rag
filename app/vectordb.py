"""
向量数据库模块 - FAISS向量存储管理
Vector Database Module - FAISS vector store management
"""

import os
import pickle
from typing import List, Optional, Dict, Any
import logging
from pathlib import Path

import faiss
import numpy as np
from langchain.schema import Document
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS as CommunityFAISS

logger = logging.getLogger(__name__)


class VectorDatabase:
    """FAISS向量数据库管理器 - FAISS vector database manager"""
    
    def __init__(self, db_path: str = "./vector_db", embedding_model: str = "text-embedding-ada-002"):
        """初始化向量数据库 - Initialize vector database
        
        Args:
            db_path: 数据库存储路径 - Database storage path
            embedding_model: 嵌入模型名称 - Embedding model name
        """
        self.db_path = Path(db_path)
        self.db_path.mkdir(exist_ok=True)
        
        self.embedding_model = embedding_model
        self.embeddings = OpenAIEmbeddings(model=embedding_model)
        self.vectorstore = None
        
        # 元数据文件路径 - Metadata file path
        self.metadata_path = self.db_path / "metadata.pkl"
        self.faiss_index_path = self.db_path / "index.faiss"
        self.faiss_pkl_path = self.db_path / "index.pkl"
        
        # 加载现有数据库 - Load existing database
        self._load_existing_db()
    
    def _load_existing_db(self) -> bool:
        """加载现有数据库 - Load existing database"""
        try:
            if self.faiss_index_path.exists() and self.faiss_pkl_path.exists():
                logger.info("加载现有FAISS数据库 - Loading existing FAISS database")
                self.vectorstore = FAISS.load_local(
                    str(self.db_path), 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                return True
            else:
                logger.info("未找到现有数据库 - No existing database found")
                return False
        except Exception as e:
            logger.error(f"加载数据库失败 - Failed to load database: {e}")
            return False
    
    def add_documents(self, documents: List[Document]) -> bool:
        """添加文档到向量数据库 - Add documents to vector database
        
        Args:
            documents: 要添加的文档列表 - List of documents to add
            
        Returns:
            bool: 是否成功添加 - Whether successfully added
        """
        try:
            if not documents:
                logger.warning("没有文档需要添加 - No documents to add")
                return False
            
            logger.info(f"开始向量化 {len(documents)} 个文档 - Starting vectorization of {len(documents)} documents")
            
            if self.vectorstore is None:
                # 创建新的向量存储 - Create new vector store
                self.vectorstore = FAISS.from_documents(documents, self.embeddings)
                logger.info("创建新的FAISS向量库 - Created new FAISS vector store")
            else:
                # 添加到现有向量存储 - Add to existing vector store
                new_vectorstore = FAISS.from_documents(documents, self.embeddings)
                self.vectorstore.merge_from(new_vectorstore)
                logger.info("合并到现有FAISS向量库 - Merged to existing FAISS vector store")
            
            return True
            
        except Exception as e:
            logger.error(f"添加文档失败 - Failed to add documents: {e}")
            return False
    
    def save_database(self) -> bool:
        """保存数据库到磁盘 - Save database to disk"""
        try:
            if self.vectorstore is None:
                logger.warning("没有向量库需要保存 - No vector store to save")
                return False
            
            # 保存FAISS向量库 - Save FAISS vector store
            self.vectorstore.save_local(str(self.db_path))
            
            # 保存额外的元数据 - Save additional metadata
            metadata = {
                'embedding_model': self.embedding_model,
                'document_count': len(self.vectorstore.docstore._dict),
                'created_at': str(Path.ctime(self.db_path))
            }
            
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(metadata, f)
            
            logger.info("数据库保存成功 - Database saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"保存数据库失败 - Failed to save database: {e}")
            return False
    
    def search_similar(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """搜索相似文档 - Search for similar documents
        
        Args:
            query: 查询文本 - Query text
            k: 返回结果数量 - Number of results to return
            
        Returns:
            List of documents with similarity scores and metadata
        """
        try:
            if self.vectorstore is None:
                logger.warning("向量库未初始化 - Vector store not initialized")
                return []
            
            # 执行相似性搜索 - Perform similarity search
            docs_with_scores = self.vectorstore.similarity_search_with_score(query, k=k)
            
            results = []
            for doc, score in docs_with_scores:
                result = {
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'similarity_score': float(score),
                    'source': f"{doc.metadata.get('file_name', 'Unknown')} (Page {doc.metadata.get('page_num', 'N/A')})"
                }
                results.append(result)
            
            logger.info(f"找到 {len(results)} 个相关文档 - Found {len(results)} relevant documents")
            return results
            
        except Exception as e:
            logger.error(f"搜索失败 - Search failed: {e}")
            return []
    
    def get_retriever(self, k: int = 5):
        """获取检索器 - Get retriever"""
        if self.vectorstore is None:
            logger.error("向量库未初始化 - Vector store not initialized")
            return None
        
        return self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k}
        )
    
    def clear_database(self) -> bool:
        """清空数据库 - Clear database"""
        try:
            # 删除所有数据库文件 - Delete all database files
            for file_path in self.db_path.glob("*"):
                if file_path.is_file():
                    file_path.unlink()
            
            # 重置向量存储 - Reset vector store
            self.vectorstore = None
            
            logger.info("数据库已清空 - Database cleared")
            return True
            
        except Exception as e:
            logger.error(f"清空数据库失败 - Failed to clear database: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """获取数据库统计信息 - Get database statistics"""
        try:
            if self.vectorstore is None:
                return {
                    'document_count': 0,
                    'embedding_model': self.embedding_model,
                    'status': 'Empty'
                }
            
            # 加载元数据 - Load metadata
            metadata = {}
            if self.metadata_path.exists():
                with open(self.metadata_path, 'rb') as f:
                    metadata = pickle.load(f)
            
            stats = {
                'document_count': len(self.vectorstore.docstore._dict),
                'embedding_model': self.embedding_model,
                'status': 'Ready',
                **metadata
            }
            
            # 计算文件统计 - Calculate file statistics
            if hasattr(self.vectorstore, 'docstore'):
                files = set()
                file_types = set()
                
                for doc_id, doc in self.vectorstore.docstore._dict.items():
                    metadata = doc.metadata
                    files.add(metadata.get('file_name', 'Unknown'))
                    file_types.add(metadata.get('file_type', 'Unknown'))
                
                stats.update({
                    'unique_files': len(files),
                    'file_types': list(file_types),
                    'files': list(files)
                })
            
            return stats
            
        except Exception as e:
            logger.error(f"获取统计信息失败 - Failed to get stats: {e}")
            return {'error': str(e)}
    
    def rebuild_from_documents(self, documents: List[Document]) -> bool:
        """从文档重建数据库 - Rebuild database from documents"""
        try:
            # 清空现有数据库 - Clear existing database
            self.clear_database()
            
            # 添加新文档 - Add new documents
            success = self.add_documents(documents)
            
            if success:
                # 保存新数据库 - Save new database
                self.save_database()
                logger.info("数据库重建完成 - Database rebuild completed")
            
            return success
            
        except Exception as e:
            logger.error(f"重建数据库失败 - Failed to rebuild database: {e}")
            return False 