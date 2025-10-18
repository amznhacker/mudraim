#!/usr/bin/env python3
"""
Mudra Debug Tool - Figure out what gestures send
"""

import subprocess
import sys
import time
import threading
from datetime import datetime

# Install dependencies
try:
    import pynput
    from pynput import mouse, keyboard
    from pynput.mouse import Listener as MouseListener
    from pynput.keyboard import Listener as KeyboardListener
except ImportError:
    print("Installing pynput...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pynput"])
    from pynput import mouse, keyboard
    from pynput.mouse import Listener as MouseListener
    from pynput.keyboard import Listener as KeyboardListener

class MudraDebugger:
    def __init__(self):
        self.events = []
        self.running = True
        
    def log_event(self, event_type, data):
        """Log all events with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        event = f"[{timestamp}] {event_type}: {data}"
        print(event)
        self.events.append(event)
    
    def on_mouse_move(self, x, y):
        """Track mouse movement"""
        self.log_event("MOUSE_MOVE", f"({x}, {y})")
    
    def on_mouse_click(self, x, y, button, pressed):
        """Track mouse clicks"""
        action = "PRESS" if pressed else "RELEASE"
        self.log_event("MOUSE_CLICK", f"{button} {action} at ({x}, {y})")
    
    def on_mouse_scroll(self, x, y, dx, dy):
        """Track mouse scroll"""
        direction = "UP" if dy > 0 else "DOWN" if dy < 0 else "NONE"
        self.log_event("MOUSE_SCROLL", f"{direction} ({dx}, {dy}) at ({x}, {y})")
    
    def on_key_press(self, key):
        """Track key presses"""
        try:
            self.log_event("KEY_PRESS", f"'{key.char}'")
        except AttributeError:
            self.log_event("KEY_PRESS", f"{key}")
    
    def on_key_release(self, key):
        """Track key releases"""
        try:
            self.log_event("KEY_RELEASE", f"'{key.char}'")
        except AttributeError:
            self.log_event("KEY_RELEASE", f"{key}")
        
        # Exit on Escape
        if key == keyboard.Key.esc:
            print("\nStopping debugger...")
            self.running = False
            return False
    
    def start_debugging(self):
        """Start all event listeners"""
        print("🔍 MUDRA DEBUGGER STARTED")
        print("=" * 50)
        print("Connect your Mudra band and perform these actions:")
        print("1. Move your hand (cursor movement)")
        print("2. Pinch (left click)")
        print("3. Reverse tap (right click)")
        print("4. Scroll gesture")
        print("5. Single twist")
        print("6. Double twist")
        print("7. Any other gestures")
        print("\nPress ESC to stop debugging")
        print("=" * 50)
        
        # Start mouse listener
        mouse_listener = MouseListener(
            on_move=self.on_mouse_move,
            on_click=self.on_mouse_click,
            on_scroll=self.on_mouse_scroll
        )
        
        # Start keyboard listener
        keyboard_listener = KeyboardListener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        
        # Start both listeners
        mouse_listener.start()
        keyboard_listener.start()
        
        try:
            # Keep running until ESC is pressed
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nStopping...")
        
        # Stop listeners
        mouse_listener.stop()
        keyboard_listener.stop()
        
        print("\n" + "=" * 50)
        print("DEBUGGING COMPLETE")
        print(f"Total events captured: {len(self.events)}")
        
        # Save log to file
        with open("mudra_debug_log.txt", "w") as f:
            f.write("Mudra Band Debug Log\n")
            f.write("=" * 30 + "\n")
            for event in self.events:
                f.write(event + "\n")
        
        print("Log saved to: mudra_debug_log.txt")
        print("\nNow tell me what you observed for each gesture!")

def main():
    debugger = MudraDebugger()
    debugger.start_debugging()

if __name__ == "__main__":
    main()