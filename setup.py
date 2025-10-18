#!/usr/bin/env python3
"""
Setup script for Mudra Virtual Keyboard
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("✗ Failed to install dependencies")
        return False
    return True

def setup_permissions():
    """Setup permissions for keyboard input on Linux"""
    print("Setting up permissions for keyboard input...")
    print("You may need to add your user to the 'input' group:")
    print("sudo usermod -a -G input $USER")
    print("Then log out and log back in.")

def main():
    print("Setting up Mudra Virtual Keyboard...")
    
    if not install_requirements():
        sys.exit(1)
    
    if sys.platform.startswith('linux'):
        setup_permissions()
    
    print("\n✓ Setup complete!")
    print("Run: python3 mudra_interface.py")

if __name__ == "__main__":
    main()