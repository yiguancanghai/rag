#!/usr/bin/env python3
"""
Simple startup script for IntelliDocs Pro
"""

import os
import sys
from pathlib import Path

# Ensure we're in the project root directory
project_root = Path(__file__).parent
os.chdir(project_root)

# Add the project root to Python path
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "app"))

# Set environment variable for imports
os.environ["PYTHONPATH"] = f"{project_root}:{project_root}/app"

if __name__ == "__main__":
    # Import and run streamlit
    import subprocess
    
    print("🚀 Starting IntelliDocs Pro...")
    print("   Project root:", project_root)
    print("   Python path:", sys.path[:3])
    print("   Access URL: http://localhost:8501")
    print()
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "app/main.py",
            "--server.port=8501",
            "--server.address=localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 Stopped IntelliDocs Pro")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)