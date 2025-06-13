#!/bin/bash

# 📄🔍 Document Q&A RAG System - Quick Start Script
# 快速启动脚本 - Quick start script for RAG system

set -e  # Exit on any error

echo "📄🔍 Document Q&A RAG System - Quick Start"
echo "=========================================="

# 检查Python版本 - Check Python version
echo "🔍 Checking Python version..."
if ! python3 --version | grep -E "3\.(11|12|13)" > /dev/null; then
    echo "❌ Python 3.11+ required. Please install Python 3.11 or higher."
    exit 1
fi
echo "✅ Python version OK"

# 检查是否在虚拟环境中 - Check if in virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment active: $VIRTUAL_ENV"
else
    echo "⚠️  No virtual environment detected"
    echo "💡 Recommended: Create a virtual environment first"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate  # On macOS/Linux"
    echo "   venv\\Scripts\\activate     # On Windows"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 安装依赖 - Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# 检查环境配置 - Check environment configuration
echo "⚙️  Checking environment configuration..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "📝 Creating .env file from template..."
        cp .env.example .env
        echo "⚠️  Please edit .env file with your OpenAI API key:"
        echo "   OPENAI_API_KEY=your_api_key_here"
        echo ""
        read -p "Press Enter after setting your API key..."
    else
        echo "❌ No .env.example file found"
        exit 1
    fi
fi

# 验证API密钥 - Validate API key
source .env 2>/dev/null || true
if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your_openai_api_key_here" ]; then
    echo "❌ Please set your OPENAI_API_KEY in .env file"
    exit 1
fi
echo "✅ OpenAI API key configured"

# 创建必要目录 - Create necessary directories
echo "📁 Creating directories..."
mkdir -p vector_db logs .streamlit

# 运行系统测试 - Run system tests
echo "🧪 Running system tests..."
if python3 test_system.py; then
    echo "✅ All tests passed!"
else
    echo "⚠️  Some tests failed, but system may still work"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 启动系统 - Start system
echo ""
echo "🚀 Starting Document Q&A RAG System..."
echo "🌐 Opening browser at http://localhost:8501"
echo "🛑 Press Ctrl+C to stop the server"
echo "=========================================="
echo ""

# 启动Streamlit - Start Streamlit
python3 run.py 