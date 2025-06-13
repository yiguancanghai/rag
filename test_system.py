#!/usr/bin/env python3
"""
RAG系统测试脚本 - RAG System Test Script
Comprehensive testing for the Document Q&A RAG system
"""

import os
import sys
import tempfile
import logging
from pathlib import Path
from typing import List, Dict, Any

# 添加应用路径 - Add app path
sys.path.append(str(Path(__file__).parent / 'app'))

def setup_logging():
    """设置测试日志 - Setup test logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def create_test_documents() -> List[tuple]:
    """创建测试文档 - Create test documents"""
    # 测试文档内容 - Test document content
    test_docs = [
        ("test_document.txt", """
Document Q&A RAG System Test Document

This is a comprehensive test document for the RAG system.

Section 1: Introduction
The RAG (Retrieval-Augmented Generation) system combines the power of 
vector search with large language models to provide accurate answers 
based on document content.

Key features include:
- Multi-file upload support
- Intelligent document chunking
- FAISS vector storage
- Source citation tracking
- Real-time processing metrics

Section 2: Technical Architecture
The system uses the following components:
1. DocumentLoader: Processes PDF, DOCX, and TXT files
2. VectorDatabase: FAISS-based similarity search
3. QAChain: LangChain integration with OpenAI GPT-4o
4. Streamlit UI: Interactive web interface

Section 3: Performance Metrics
Expected performance characteristics:
- Document processing: <30 seconds for typical documents
- Query response time: <5 seconds
- Accuracy: High precision with source citations
- Scalability: Handles multiple large documents efficiently

Section 4: Use Cases
Common applications include:
- Enterprise document search
- Research paper analysis
- Legal document review
- Technical documentation Q&A
- Knowledge base queries
        """),
        
        ("technical_specs.txt", """
Technical Specifications - RAG System

Hardware Requirements:
- CPU: 4+ cores recommended
- RAM: 8GB minimum, 16GB recommended
- Storage: 10GB free space for vector database
- Network: Internet connection for OpenAI API

Software Dependencies:
- Python 3.11+
- LangChain framework
- OpenAI Python library
- FAISS vector search
- Streamlit web framework
- PyMuPDF for PDF processing

Configuration Parameters:
- Chunk Size: 1000 characters (configurable)
- Chunk Overlap: 200 characters
- Vector Dimensions: 1536 (OpenAI embeddings)
- Top-K Retrieval: 5 documents
- Temperature: 0 (deterministic responses)

API Limits:
- OpenAI API rate limits apply
- Recommended: Monitor token usage
- Cost optimization: Use efficient chunking
        """)
    ]
    
    # 创建临时文件 - Create temporary files
    temp_files = []
    for filename, content in test_docs:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_files.append((f.name.encode(), filename))
    
    return temp_files

def test_document_loader():
    """测试文档加载器 - Test document loader"""
    logging.info("🧪 Testing DocumentLoader...")
    
    try:
        from loader import DocumentLoader
        
        # 创建测试文档 - Create test documents
        test_files = create_test_documents()
        
        # 初始化加载器 - Initialize loader
        loader = DocumentLoader(chunk_size=500, chunk_overlap=100)
        
        # 加载文档 - Load documents
        documents = loader.load_multiple_files([
            (open(file_path, 'rb').read(), filename) 
            for file_path, filename in test_files
        ])
        
        # 验证结果 - Validate results
        assert len(documents) > 0, "No documents loaded"
        assert all(doc.page_content for doc in documents), "Empty document content"
        assert all('file_name' in doc.metadata for doc in documents), "Missing metadata"
        
        logging.info("✅ DocumentLoader test passed - %d chunks created", len(documents))
        
        # 清理临时文件 - Clean up temp files
        for file_path, _ in test_files:
            Path(file_path.decode()).unlink(missing_ok=True)
        
        return documents
        
    except Exception as e:
        logging.error("❌ DocumentLoader test failed: %s", e)
        return None

def test_vector_database(documents):
    """测试向量数据库 - Test vector database"""
    if not documents:
        logging.error("❌ No documents provided for VectorDatabase test")
        return None
    
    logging.info("🧪 Testing VectorDatabase...")
    
    try:
        from vectordb import VectorDatabase
        
        # 使用临时目录 - Use temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # 初始化向量数据库 - Initialize vector database
            vector_db = VectorDatabase(db_path=temp_dir)
            
            # 添加文档 - Add documents
            success = vector_db.add_documents(documents)
            assert success, "Failed to add documents"
            
            # 保存数据库 - Save database
            success = vector_db.save_database()
            assert success, "Failed to save database"
            
            # 测试搜索 - Test search
            results = vector_db.search_similar("RAG system architecture", k=3)
            assert len(results) > 0, "No search results found"
            assert all('content' in result for result in results), "Missing content in results"
            
            # 获取统计信息 - Get statistics
            stats = vector_db.get_stats()
            assert stats['document_count'] > 0, "Invalid document count"
            
            logging.info("✅ VectorDatabase test passed - %d documents indexed", 
                        stats['document_count'])
            
            return vector_db
    
    except Exception as e:
        logging.error("❌ VectorDatabase test failed: %s", e)
        return None

def test_qa_chain(vector_db):
    """测试问答链 - Test QA chain"""
    if not vector_db:
        logging.error("❌ No vector database provided for QAChain test")
        return False
    
    logging.info("🧪 Testing QAChain...")
    
    try:
        from qa_chain import QAChain
        
        # 检查API密钥 - Check API key
        if not os.getenv('OPENAI_API_KEY'):
            logging.warning("⚠️ No OpenAI API key found - skipping QAChain test")
            return True
        
        # 初始化QA链 - Initialize QA chain
        qa_chain = QAChain(
            model_name="gpt-4o",
            temperature=0,
            strict_mode=True
        )
        
        # 设置检索器 - Setup retriever
        retriever = vector_db.get_retriever(k=3)
        success = qa_chain.setup_chain(retriever)
        assert success, "Failed to setup QA chain"
        
        # 测试问答 - Test Q&A
        test_questions = [
            "What are the key features of the RAG system?",
            "What are the hardware requirements?",
            "How does the system process documents?"
        ]
        
        for question in test_questions:
            result = qa_chain.ask_question(question)
            assert not result.get('error'), f"QA failed for: {question}"
            assert result.get('answer'), f"No answer for: {question}"
            assert len(result.get('source_documents', [])) > 0, f"No sources for: {question}"
            
            logging.info("✅ Q&A test passed: %s -> %s", 
                        question[:50] + "...", 
                        result['answer'][:100] + "...")
        
        logging.info("✅ QAChain test passed - all questions answered")
        return True
        
    except Exception as e:
        logging.error("❌ QAChain test failed: %s", e)
        return False

def test_utils():
    """测试工具函数 - Test utility functions"""
    logging.info("🧪 Testing Utils...")
    
    try:
        from utils import (
            Timer, format_file_size, safe_filename, 
            load_config, validate_config, get_system_info
        )
        
        # 测试计时器 - Test timer
        with Timer() as timer:
            import time
            time.sleep(0.1)
        assert timer.elapsed >= 0.1, "Timer not working"
        
        # 测试文件大小格式化 - Test file size formatting
        assert format_file_size(1024) == "1.0KB", "File size formatting failed"
        assert format_file_size(1024*1024) == "1.0MB", "File size formatting failed"
        
        # 测试安全文件名 - Test safe filename
        assert safe_filename("test/file?.txt") == "test_file_.txt", "Safe filename failed"
        
        # 测试配置加载 - Test config loading
        config = load_config()
        assert isinstance(config, dict), "Config loading failed"
        
        # 测试配置验证 - Test config validation
        errors = validate_config(config)
        assert isinstance(errors, list), "Config validation failed"
        
        # 测试系统信息 - Test system info
        sys_info = get_system_info()
        assert 'platform' in sys_info, "System info missing platform"
        
        logging.info("✅ Utils test passed")
        return True
        
    except Exception as e:
        logging.error("❌ Utils test failed: %s", e)
        return False

def test_integration():
    """集成测试 - Integration test"""
    logging.info("🧪 Running integration test...")
    
    try:
        # 端到端测试流程 - End-to-end test flow
        logging.info("1️⃣ Testing document loading...")
        documents = test_document_loader()
        if not documents:
            return False
        
        logging.info("2️⃣ Testing vector database...")
        vector_db = test_vector_database(documents)
        if not vector_db:
            return False
        
        logging.info("3️⃣ Testing QA chain...")
        qa_success = test_qa_chain(vector_db)
        if not qa_success:
            return False
        
        logging.info("4️⃣ Testing utilities...")
        utils_success = test_utils()
        if not utils_success:
            return False
        
        logging.info("✅ Integration test passed - all components working")
        return True
        
    except Exception as e:
        logging.error("❌ Integration test failed: %s", e)
        return False

def run_performance_test():
    """性能测试 - Performance test"""
    logging.info("🧪 Running performance test...")
    
    try:
        from utils import Timer
        
        # 创建大量测试文档 - Create multiple test documents
        large_content = "Test content. " * 1000  # ~14KB content
        test_files = [(large_content.encode(), "large_test.txt")]
        
        # 测试文档处理性能 - Test document processing performance
        with Timer() as timer:
            from loader import DocumentLoader
            loader = DocumentLoader(chunk_size=1000, chunk_overlap=200)
            documents = loader.load_multiple_files(test_files)
        
        processing_time = timer.elapsed
        logging.info("📊 Document processing: %.2fs for %d chunks", 
                    processing_time, len(documents))
        
        # 测试向量化性能 - Test vectorization performance
        if os.getenv('OPENAI_API_KEY'):
            with Timer() as timer:
                from vectordb import VectorDatabase
                with tempfile.TemporaryDirectory() as temp_dir:
                    vector_db = VectorDatabase(db_path=temp_dir)
                    vector_db.add_documents(documents[:10])  # Limit for API costs
            
            vectorization_time = timer.elapsed
            logging.info("📊 Vectorization: %.2fs for %d chunks", 
                        vectorization_time, min(10, len(documents)))
        
        logging.info("✅ Performance test completed")
        return True
        
    except Exception as e:
        logging.error("❌ Performance test failed: %s", e)
        return False

def main():
    """主测试函数 - Main test function"""
    setup_logging()
    
    print("🧪 RAG System Comprehensive Test Suite")
    print("=" * 50)
    
    # 加载环境变量 - Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    test_results = []
    
    # 运行测试套件 - Run test suite
    tests = [
        ("工具函数测试", test_utils),
        ("集成测试", test_integration),
        ("性能测试", run_performance_test),
    ]
    
    for test_name, test_func in tests:
        logging.info("🔍 Running %s...", test_name)
        try:
            result = test_func()
            test_results.append((test_name, result))
            if result:
                logging.info("✅ %s passed", test_name)
            else:
                logging.error("❌ %s failed", test_name)
        except Exception as e:
            logging.error("❌ %s error: %s", test_name, e)
            test_results.append((test_name, False))
    
    # 测试结果总结 - Test results summary
    print("\n📊 Test Results Summary")
    print("=" * 30)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! RAG system is ready for use.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the logs above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 