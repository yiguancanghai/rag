#!/usr/bin/env python3
"""
Environment Check Script for IntelliDocs Pro
Verify that all required environment variables are properly set
"""

import os
import sys
from pathlib import Path

def check_environment():
    """Check environment configuration"""
    print("🔍 Checking IntelliDocs Pro Environment Configuration\n")
    
    # Check Python version
    print(f"Python Version: {sys.version}")
    print(f"Python Path: {sys.executable}\n")
    
    # Check API key in environment variables
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if api_key:
        if api_key.startswith("sk-"):
            print("✅ OPENAI_API_KEY found in environment variables")
            print(f"   Key starts with: {api_key[:7]}...")
            print(f"   Key length: {len(api_key)} characters")
        else:
            print("❌ OPENAI_API_KEY found but doesn't look like a valid OpenAI key")
            print("   OpenAI keys should start with 'sk-'")
    else:
        print("❌ OPENAI_API_KEY not found in environment variables")
    
    print()
    
    # Check .env file
    env_file = Path("config/.env")
    if env_file.exists():
        print("📄 Found config/.env file")
        try:
            content = env_file.read_text()
            if "OPENAI_API_KEY=" in content:
                print("   Contains OPENAI_API_KEY configuration")
            else:
                print("   Does not contain OPENAI_API_KEY")
        except Exception as e:
            print(f"   Error reading file: {e}")
    else:
        print("📄 No config/.env file found")
    
    print()
    
    # Check directories
    required_dirs = ["data", "data/documents", "data/vector_db", "logs"]
    
    print("📁 Checking directories:")
    for directory in required_dirs:
        dir_path = Path(directory)
        if dir_path.exists():
            print(f"   ✅ {directory}")
        else:
            print(f"   ❌ {directory} (will be created when needed)")
    
    print()
    
    # Check if we can import required packages
    print("📦 Checking required packages:")
    required_packages = [
        ('streamlit', 'streamlit'),
        ('langchain', 'langchain'),
        ('openai', 'openai'),
        ('chromadb', 'chromadb'),
        ('dotenv', 'python-dotenv')
    ]
    
    missing_packages = []
    for import_name, package_name in required_packages:
        try:
            __import__(import_name)
            print(f"   ✅ {package_name}")
        except ImportError:
            print(f"   ❌ {package_name}")
            missing_packages.append(package_name)
    
    print()
    
    # Summary
    if api_key and api_key.startswith("sk-") and not missing_packages:
        print("🎉 Environment is ready!")
        print("   You can run: python run_local.py")
    else:
        print("⚠️  Environment needs setup:")
        
        if not (api_key and api_key.startswith("sk-")):
            print("   - Set OPENAI_API_KEY environment variable")
            print("     Add to your ~/.zshrc: export OPENAI_API_KEY='your-key-here'")
            print("     Then run: source ~/.zshrc")
        
        if missing_packages:
            print("   - Install missing packages:")
            print("     pip install -r requirements.txt")
    
    print()

if __name__ == "__main__":
    check_environment()