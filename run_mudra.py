#!/usr/bin/env python3
"""
Main Mudra System Launcher
"""

import sys
import time
from mudra_bluetooth import MudraBluetoothInterface

def main():
    print("🎯 Mudra Complete System")
    print("Connecting to Mudra band...")
    
    interface = MudraBluetoothInterface()
    
    # Try to connect
    if interface.start():
        print("✅ Mudra band connected!")
        print("🖱️  Mouse mode active (default)")
        print("📝 Double twist to enter typing mode")
        print("🔄 Twist to toggle modes")
        print("Press Ctrl+C to exit")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")
            interface.stop()
    else:
        print("❌ Could not connect to Mudra band")
        print("Make sure it's paired and in range")
        sys.exit(1)

if __name__ == "__main__":
    main()