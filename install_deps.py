#!/usr/bin/env python3
"""
Install dependencies for LlamaCloud PDF Parser
"""

import subprocess
import sys

def install_packages():
    """Install required packages."""
    packages = [
        "fastapi",
        "uvicorn",
        "llama-cloud>=2.1",
        "nest_asyncio"
    ]
    
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                package, "--break-system-packages"
            ])
            print(f"✓ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"✗ Error installing {package}: {e}")
            return False
    
    return True

if __name__ == "__main__":
    if install_packages():
        print("\n✅ All dependencies installed successfully!")
    else:
        print("\n❌ Some packages failed to install")
        sys.exit(1)
