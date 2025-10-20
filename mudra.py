#!/usr/bin/env python3
"""
Mudra Console Debugger - No GUI, no X11 errors
"""

import subprocess
import sys
import time
from pynput import keyboard
from pynput.keyboard import Key, Listener as KeyboardListener

# Install pynput if needed
try:
    import pynput
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pynput"])

class MudraDebug:
    def __init__(self):
        self.expected = {
            'pinch_right': 'RIGHT',
            'pinch_left': 'LEFT', 
            'pinch_up': 'UP',
            'pinch_down': 'DOWN',
            'double_tap': 'ENTER',
            'twist': 'F2',
            'double_twist': 'F3'
        }
        
        self.testing = None
        self.test_start = 0
    
    def on_key_press(self, key):
        """Handle key presses"""
        key_name = str(key).replace('Key.', '').upper()
        timestamp = time.strftime("%H:%M:%S")
        
        print(f"[{timestamp}] Key received: {key_name}")
        
        # Check if testing
        if self.testing:
            expected = self.expected[self.testing]
            if key_name == expected:
                print(f"✅ CORRECT! {self.testing} → {key_name}")
            else:
                print(f"❌ WRONG! {self.testing} expected {expected}, got {key_name}")
                print(f"🔧 FIX: In Mudra app, change {self.testing} to send {expected}")
            self.testing = None
        
        if key == Key.esc:
            return False
    
    def run(self):
        """Start debugger"""
        print("🔍 MUDRA CONSOLE DEBUGGER")
        print("No GUI - just console output")
        print("\n=== COMMANDS ===")
        print("Type number + Enter to test gesture:")
        print("1 = PINCH + RIGHT")
        print("2 = PINCH + LEFT") 
        print("3 = PINCH + UP")
        print("4 = PINCH + DOWN")
        print("5 = DOUBLE TAP")
        print("6 = TWIST")
        print("7 = DOUBLE TWIST")
        print("ESC = exit")
        print("\n=== HOW TO USE ===")
        print("1. Type a number (1-7) and press Enter")
        print("2. Do that gesture on Mudra")
        print("3. See if correct key was received")
        print("\nStarting key listener...")
        
        # Start keyboard listener in background
        listener = KeyboardListener(on_press=self.on_key_press)
        listener.start()
        
        try:
            while True:
                try:
                    choice = input("\nEnter test number (1-7): ").strip()
                    
                    tests = {
                        '1': 'pinch_right',
                        '2': 'pinch_left',
                        '3': 'pinch_up', 
                        '4': 'pinch_down',
                        '5': 'double_tap',
                        '6': 'twist',
                        '7': 'double_twist'
                    }
                    
                    if choice in tests:
                        self.testing = tests[choice]
                        expected = self.expected[self.testing]
                        print(f"\n🎯 Testing: {self.testing}")
                        print(f"Expected key: {expected}")
                        print("Do the gesture now...")
                        self.test_start = time.time()
                    elif choice.lower() == 'q':
                        break
                    else:
                        print("Invalid choice. Use 1-7 or 'q' to quit")
                        
                except KeyboardInterrupt:
                    break
                except EOFError:
                    break
                    
        except KeyboardInterrupt:
            pass
        
        print("\n👋 Debugger stopped")
        listener.stop()

if __name__ == "__main__":
    debugger = MudraDebug()
    debugger.run()