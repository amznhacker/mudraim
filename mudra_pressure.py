#!/usr/bin/env python3
"""
Mudra Pressure Detection - Map pressure levels to number keys
"""

import subprocess
import sys
import time
from pynput import keyboard
from pynput.keyboard import Key, Listener

# Install pynput if needed
try:
    import pynput
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pynput"])
    from pynput import keyboard
    from pynput.keyboard import Key, Listener

class MudraPressureDetector:
    def __init__(self):
        self.kb = keyboard.Controller()
        self.typing_mode = False
        self.pressure_levels = {}
        self.calibrating = False
        
        # Character maps
        self.chars = [
            ['a','b','c','d','e','f','g','h','i'],  # Letters
            ['1','2','3','4','5','6','7','8','9'],  # Numbers  
            ['!','@','#','$','%','^','&','*','(']   # Symbols
        ]
        self.layer = 0
        
    def calibrate_pressure(self):
        """Calibrate 9 different pressure levels"""
        print("\n🎯 PRESSURE CALIBRATION")
        print("We'll map 9 different pressure levels to positions 0-8")
        print("This will let you type with pure gestures!")
        
        self.pressure_levels = {}
        
        for i in range(9):
            print(f"\n=== Position {i} (Character: {self.chars[0][i]}) ===")
            print("Apply pressure and hold...")
            print("We'll detect the pressure level for this position")
            
            # Simulate pressure detection (in real implementation, read from Mudra hardware)
            input(f"Press Enter when applying pressure for position {i}: ")
            
            # For now, we'll use keyboard keys as pressure simulation
            print(f"Pressure level for position {i} calibrated!")
            self.pressure_levels[i] = f"pressure_level_{i}"
        
        print("\n✅ Calibration complete!")
        print("Now you can type using pressure gestures!")
        
    def detect_pressure_gesture(self):
        """Detect which pressure level is being applied"""
        # In real implementation, this would read actual pressure from Mudra band
        # For simulation, we'll use keyboard input
        
        print("\nPressure detection active...")
        print("Apply pressure gestures to type!")
        print("(For simulation: press 0-8 keys)")
        
        while True:
            try:
                # Simulate pressure detection
                key_input = input("Pressure gesture (0-8, or 'q' to quit): ").strip()
                
                if key_input == 'q':
                    break
                elif key_input.isdigit() and 0 <= int(key_input) <= 8:
                    pos = int(key_input)
                    self.type_character(pos)
                else:
                    print("Invalid pressure level")
                    
            except KeyboardInterrupt:
                break
    
    def type_character(self, pos):
        """Type character based on pressure position"""
        if self.typing_mode and pos < len(self.chars[self.layer]):
            char = self.chars[self.layer][pos]
            self.kb.press(char)
            self.kb.release(char)
            print(f"Typed: {char} (pressure position {pos})")
        else:
            print(f"Pressure detected at position {pos}")
    
    def on_key_press(self, key):
        """Handle F1/F2 for mode switching"""
        try:
            if key == Key.f1:
                self.typing_mode = not self.typing_mode
                mode = "TYPING" if self.typing_mode else "MOUSE"
                print(f"\n🔄 Switched to {mode} mode")
                
            elif key == Key.f2:
                if self.typing_mode:
                    self.layer = (self.layer + 1) % 3
                    layers = ['Letters', 'Numbers', 'Symbols']
                    print(f"\n🔄 Switched to {layers[self.layer]} layer")
                    
        except AttributeError:
            pass
    
    def on_key_release(self, key):
        """Handle key releases"""
        if key == Key.esc:
            return False
    
    def run(self):
        """Main system"""
        print("🎯 MUDRA PRESSURE TYPING SYSTEM")
        print("Map pressure levels to typing positions!")
        
        while True:
            print("\n=== MENU ===")
            print("1. Calibrate pressure levels")
            print("2. Start pressure typing")
            print("3. Test with F1/F2 mode switching")
            print("4. Quit")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == '1':
                self.calibrate_pressure()
            elif choice == '2':
                self.detect_pressure_gesture()
            elif choice == '3':
                print("\nStarting with F1/F2 detection...")
                print("F1 = Toggle typing mode")
                print("F2 = Switch layers")
                print("Press ESC to stop")
                
                with Listener(on_press=self.on_key_press, on_release=self.on_key_release) as listener:
                    listener.join()
            elif choice == '4':
                break
            else:
                print("Invalid option")

if __name__ == "__main__":
    detector = MudraPressureDetector()
    detector.run()