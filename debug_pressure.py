#!/usr/bin/env python3
"""
Debug Mudra Pressure System - See what's happening
"""

import subprocess
import sys
import time
from datetime import datetime

# Install pynput if needed
try:
    import pynput
    from pynput import keyboard, mouse
    from pynput.keyboard import Key, Listener as KeyboardListener
    from pynput.mouse import Listener as MouseListener
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pynput"])
    from pynput import keyboard, mouse
    from pynput.keyboard import Key, Listener as KeyboardListener
    from pynput.mouse import Listener as MouseListener

class PressureDebugger:
    def __init__(self):
        self.kb = keyboard.Controller()
        self.events = []
        self.running = True
        self.typing_mode = False
        self.pressure_simulation = False
        
        # Character mapping
        self.chars = ['a','b','c','d','e','f','g','h','i']
        
    def log_event(self, event_type, data):
        """Log all events with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        event = f"[{timestamp}] {event_type}: {data}"
        print(event)
        self.events.append(event)
    
    def on_key_press(self, key):
        """Track all key presses"""
        try:
            if hasattr(key, 'char') and key.char:
                self.log_event("KEY_PRESS", f"'{key.char}'")
                
                # Simulate pressure detection with number keys
                if self.pressure_simulation and key.char.isdigit():
                    pos = int(key.char)
                    if 0 <= pos <= 8:
                        self.simulate_pressure_input(pos)
            else:
                self.log_event("KEY_PRESS", f"{key}")
                
                # Handle F1/F2
                if key == Key.f1:
                    self.toggle_typing_mode()
                elif key == Key.f2:
                    self.log_event("GESTURE", "Double twist detected")
                    
        except AttributeError:
            self.log_event("KEY_PRESS", f"{key}")
    
    def on_key_release(self, key):
        """Track key releases"""
        try:
            if hasattr(key, 'char') and key.char:
                self.log_event("KEY_RELEASE", f"'{key.char}'")
            else:
                self.log_event("KEY_RELEASE", f"{key}")
        except AttributeError:
            self.log_event("KEY_RELEASE", f"{key}")
        
        # Exit on Escape
        if key == Key.esc:
            self.log_event("SYSTEM", "Stopping debugger...")
            self.running = False
            return False
    
    def toggle_typing_mode(self):
        """Toggle typing mode"""
        self.typing_mode = not self.typing_mode
        mode = "TYPING" if self.typing_mode else "MOUSE"
        self.log_event("MODE_CHANGE", f"Switched to {mode} mode")
        
        if self.typing_mode:
            self.log_event("INFO", "Ready for pressure gestures (0-8 keys)")
            self.show_pressure_layout()
    
    def simulate_pressure_input(self, pressure_level):
        """Simulate pressure input"""
        self.log_event("PRESSURE_DETECTED", f"Level {pressure_level}")
        
        if self.typing_mode and pressure_level < len(self.chars):
            char = self.chars[pressure_level]
            self.kb.press(char)
            self.kb.release(char)
            self.log_event("CHARACTER_TYPED", f"'{char}' from pressure {pressure_level}")
        else:
            self.log_event("PRESSURE_IGNORED", f"Not in typing mode or invalid level")
    
    def show_pressure_layout(self):
        """Show pressure to character mapping"""
        self.log_event("LAYOUT", "Pressure levels:")
        for i, char in enumerate(self.chars):
            self.log_event("LAYOUT", f"  Pressure {i} → '{char}'")
    
    def start_debugging(self):
        """Start the debugging session"""
        print("🔍 MUDRA PRESSURE DEBUGGER")
        print("=" * 50)
        print("This will help us understand pressure detection")
        print()
        print("INSTRUCTIONS:")
        print("1. Connect your Mudra band")
        print("2. Perform gestures and see what gets detected")
        print("3. Test pressure simulation with number keys 0-8")
        print("4. Use F1 (twist) to toggle typing mode")
        print("5. Use F2 (double twist) for layer switching")
        print()
        print("Press 'p' to enable pressure simulation mode")
        print("Press ESC to stop debugging")
        print("=" * 50)
        
        # Start keyboard listener
        keyboard_listener = KeyboardListener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        
        keyboard_listener.start()
        
        try:
            # Interactive commands
            while self.running:
                try:
                    cmd = input("\nCommand (p=pressure mode, s=show layout, q=quit): ").strip().lower()
                    
                    if cmd == 'p':
                        self.pressure_simulation = not self.pressure_simulation
                        status = "ON" if self.pressure_simulation else "OFF"
                        self.log_event("SYSTEM", f"Pressure simulation {status}")
                        if self.pressure_simulation:
                            print("Now press 0-8 keys to simulate pressure levels")
                    
                    elif cmd == 's':
                        self.show_pressure_layout()
                    
                    elif cmd == 'q':
                        break
                        
                except EOFError:
                    break
                    
        except KeyboardInterrupt:
            self.log_event("SYSTEM", "Interrupted by user")
        
        keyboard_listener.stop()
        
        print("\n" + "=" * 50)
        print("DEBUGGING COMPLETE")
        print(f"Total events captured: {len(self.events)}")
        
        # Save log
        with open("pressure_debug_log.txt", "w") as f:
            f.write("Mudra Pressure Debug Log\n")
            f.write("=" * 30 + "\n")
            for event in self.events:
                f.write(event + "\n")
        
        print("Log saved to: pressure_debug_log.txt")
        print("\nNow show me the log and tell me what you observed!")

def main():
    debugger = PressureDebugger()
    debugger.start_debugging()

if __name__ == "__main__":
    main()