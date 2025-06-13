#!/usr/bin/env python3
"""
RAG系统启动脚本 - RAG System Startup Script
Quick launcher for the Document Q&A RAG system
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

def setup_logging():
    """设置日志 - Setup logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def check_python_version():
    """检查Python版本 - Check Python version"""
    if sys.version_info < (3, 11):
        logging.error("❌ Python 3.11+ required. Current: %s", sys.version)
        return False
    logging.info("✅ Python version: %s", sys.version.split()[0])
    return True

def check_environment():
    """检查环境配置 - Check environment configuration"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        if env_example.exists():
            logging.warning("⚠️  .env file not found. Copying from .env.example")
            import shutil
            shutil.copy(env_example, env_file)
            logging.info("📝 Please edit .env file with your OpenAI API key")
        else:
            logging.error("❌ No .env or .env.example file found")
            return False
    
    # 检查API密钥 - Check API key
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'your_openai_api_key_here':
        logging.error("❌ Please set your OPENAI_API_KEY in .env file")
        return False
    
    logging.info("✅ Environment configuration found")
    return True

def check_dependencies():
    """检查依赖包 - Check dependencies"""
    try:
        import streamlit
        import langchain
        import openai
        import faiss
        import fitz  # PyMuPDF
        from docx import Document
        logging.info("✅ All required packages installed")
        return True
    except ImportError as e:
        logging.error("❌ Missing required package: %s", e.name)
        logging.info("💡 Run: pip install -r requirements.txt")
        return False

def create_directories():
    """创建必要目录 - Create necessary directories"""
    directories = ['vector_db', 'logs', '.streamlit']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    logging.info("✅ Directory structure created")

def create_streamlit_config():
    """创建Streamlit配置 - Create Streamlit configuration"""
    config_dir = Path('.streamlit')
    config_file = config_dir / 'config.toml'
    
    if not config_file.exists():
        config_content = '''[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"

[server]
maxUploadSize = 200
maxMessageSize = 200

[client]
showErrorDetails = false
'''
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        logging.info("✅ Streamlit configuration created")

def run_system_check():
    """运行系统检查 - Run system check"""
    logging.info("🔍 Running system diagnostics...")
    
    try:
        # 导入并测试核心模块 - Import and test core modules
        sys.path.append(str(Path(__file__).parent / 'app'))
        
        from utils import get_system_info, load_config
        from loader import DocumentLoader
        from vectordb import VectorDatabase
        
        # 系统信息 - System info
        system_info = get_system_info()
        logging.info("💻 System: %s", system_info.get('platform', 'Unknown'))
        logging.info("🐍 Python: %s", system_info.get('python_version', 'Unknown'))
        logging.info("💾 Memory: %.1f GB available", 
                    system_info.get('memory_available', 0) / (1024**3))
        
        # 配置检查 - Configuration check
        config = load_config()
        logging.info("⚙️  Model: %s", config.get('model_name', 'Unknown'))
        logging.info("📊 Chunk size: %s", config.get('chunk_size', 'Unknown'))
        
        logging.info("✅ System check completed successfully")
        return True
        
    except Exception as e:
        logging.error("❌ System check failed: %s", e)
        return False

def start_streamlit():
    """启动Streamlit应用 - Start Streamlit application"""
    logging.info("🚀 Starting Document Q&A RAG system...")
    
    try:
        # 启动Streamlit - Start Streamlit
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            "app/ui.py",
            "--server.address", "localhost",
            "--server.port", "8501",
            "--server.headless", "false",
            "--browser.gatherUsageStats", "false"
        ]
        
        logging.info("🌐 Starting server at http://localhost:8501")
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        logging.info("👋 RAG system stopped by user")
    except subprocess.CalledProcessError as e:
        logging.error("❌ Failed to start Streamlit: %s", e)
        return False
    except Exception as e:
        logging.error("❌ Unexpected error: %s", e)
        return False

def main():
    """主函数 - Main function"""
    setup_logging()
    
    print("📄🔍 Document Q&A RAG System Launcher")
    print("=" * 50)
    
    # 系统检查步骤 - System check steps
    checks = [
        ("Python版本检查", check_python_version),
        ("环境配置检查", check_environment),
        ("依赖包检查", check_dependencies),
        ("目录结构创建", lambda: (create_directories(), True)[1]),
        ("Streamlit配置", lambda: (create_streamlit_config(), True)[1]),
        ("系统诊断", run_system_check),
    ]
    
    # 执行检查 - Execute checks
    for check_name, check_func in checks:
        logging.info("🔍 %s...", check_name)
        if not check_func():
            logging.error("❌ %s失败", check_name)
            sys.exit(1)
    
    print("\n✅ All system checks passed!")
    print("🚀 Starting RAG system...")
    print("\n📝 Instructions:")
    print("1. Upload PDF, DOCX, or TXT files using the sidebar")
    print("2. Click 'Rebuild Vector DB' to process documents")
    print("3. Ask questions in the chat interface")
    print("4. View source citations for each answer")
    print("\n🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # 启动应用 - Start application
    start_streamlit()

if __name__ == "__main__":
    main() 