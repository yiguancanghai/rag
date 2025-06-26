#!/usr/bin/env python3
"""
IntelliDocs Pro - Local Runner Script
Quick setup and run script for local development
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def print_banner():
    """Print application banner"""
    banner = """
    ╔═══════════════════════════════════════╗
    ║        🔧 IntelliDocs Pro             ║
    ║    Enterprise Document Q&A System     ║
    ╚═══════════════════════════════════════╝
    """
    print(banner)


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")


def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'streamlit',
        'langchain',
        'openai',
        'chromadb',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        
        print("\n💡 Install missing packages with:")
        print("   pip install -r requirements.txt")
        return False
    
    print("✅ All required packages are installed")
    return True


def setup_environment():
    """Setup environment configuration"""
    # First check if API key is available in environment variables
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if api_key and api_key.startswith("sk-"):
        print("✅ OpenAI API key found in environment variables")
        return True
    
    # If not in env vars, check .env file
    env_file = Path("config/.env")
    env_example = Path("config/.env.example")
    
    if not env_file.exists():
        if env_example.exists():
            print("📋 Creating environment file from template...")
            env_file.write_text(env_example.read_text())
            print(f"✅ Created {env_file}")
        else:
            print("❌ Environment template not found")
            return False
    
    # Check if API key is configured in .env file
    env_content = env_file.read_text()
    if "your_openai_api_key_here" in env_content or "OPENAI_API_KEY=" not in env_content:
        print("⚠️  OpenAI API key not found")
        print("   Options:")
        print("   1. Use existing environment variable (already set in zsh)")
        print("   2. Edit config/.env file and add your API key")
        print(f"   Current OPENAI_API_KEY in env: {'✅ Set' if api_key else '❌ Not set'}")
        
        if not api_key:
            return False
    
    print("✅ Environment configuration ready")
    return True


def create_directories():
    """Create necessary directories"""
    directories = [
        "data/documents",
        "data/vector_db",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Created necessary directories")


def run_application():
    """Run the Streamlit application"""
    print("🚀 Starting IntelliDocs Pro...")
    print("   Access URL: http://localhost:8501")
    print("   Press Ctrl+C to stop\n")
    
    try:
        # Change to project root and run streamlit
        original_cwd = os.getcwd()
        project_root = Path(__file__).parent
        os.chdir(project_root)
        
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "app/main.py",
            "--server.port=8501",
            "--server.address=localhost"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 IntelliDocs Pro stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running application: {e}")
        sys.exit(1)
    finally:
        os.chdir(original_cwd)


def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="IntelliDocs Pro Local Runner")
    parser.add_argument("--install", action="store_true", help="Install dependencies")
    parser.add_argument("--setup", action="store_true", help="Setup environment only")
    parser.add_argument("--check", action="store_true", help="Check system requirements")
    
    args = parser.parse_args()
    
    print_banner()
    
    # Check system requirements
    check_python_version()
    
    if args.check:
        check_dependencies()
        setup_environment()
        print("✅ System check complete")
        return
    
    if args.install:
        if not install_dependencies():
            sys.exit(1)
        return
    
    if args.setup:
        create_directories()
        if not setup_environment():
            sys.exit(1)
        print("✅ Setup complete")
        return
    
    # Full startup sequence
    if not check_dependencies():
        choice = input("\n❓ Install missing dependencies? (y/n): ")
        if choice.lower() == 'y':
            if not install_dependencies():
                sys.exit(1)
        else:
            sys.exit(1)
    
    create_directories()
    
    if not setup_environment():
        sys.exit(1)
    
    # Run application
    run_application()


if __name__ == "__main__":
    main()