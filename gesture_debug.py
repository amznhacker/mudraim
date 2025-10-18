#!/usr/bin/env python3
"""
Simple Gesture Debugger - See what your Mudra band sends
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

class GestureDebugger:
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
        """Track mouse movement (only log significant moves)"""
        # Only log every 10th move to avoid spam
        if len(self.events) % 10 == 0:
            self.log_event("MOUSE_MOVE", f"({x}, {y})")
    
    def on_mouse_click(self, x, y, button, pressed):
        """Track mouse clicks"""
        action = "PRESS" if pressed else "RELEASE"
        self.log_event("MOUSE_CLICK", f"{button} {action} at ({x}, {y})")
    
    def on_mouse_scroll(self, x, y, dx, dy):
        """Track mouse scroll"""
        direction = "UP" if dy > 0 else "DOWN" if dy < 0 else "HORIZONTAL"
        self.log_event("MOUSE_SCROLL", f"{direction} ({dx}, {dy}) at ({x}, {y})")
    
    def on_key_press(self, key):
        """Track key presses"""
        try:
            if hasattr(key, 'char') and key.char:
                self.log_event("KEY_PRESS", f"'{key.char}'")
            else:
                self.log_event("KEY_PRESS", f"{key}")
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
            print("\nStopping debugger...")
            self.running = False
            return False
    
    def start_debugging(self):
        """Start the debugging session"""
        print("🔍 MUDRA GESTURE DEBUGGER")
        print("=" * 50)
        print("Perform your Mudra gestures and see what gets detected!")
        print()
        print("INSTRUCTIONS:")
        print("1. Connect your Mudra band")
        print("2. Perform each gesture ONE AT A TIME")
        print("3. Tell me what gesture you just did")
        print("4. I'll show you what was detected")
        print()
        print("GESTURES TO TEST:")
        print("- Twist (single)")
        print("- Double twist") 
        print("- Pinch")
        print("- Reverse tap")
        print("- Scroll gestures")
        print("- Any other gestures your Mudra can do")
        print()
        print("Press ESC to stop debugging")
        print("=" * 50)
        
        # Start both listeners
        mouse_listener = MouseListener(
            on_move=self.on_mouse_move,
            on_click=self.on_mouse_click,
            on_scroll=self.on_mouse_scroll
        )
        
        keyboard_listener = KeyboardListener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        
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
        with open("gesture_debug_log.txt", "w") as f:
            f.write("Mudra Gesture Debug Log\n")
            f.write("=" * 30 + "\n")
            for event in self.events:
                f.write(event + "\n")
        
        print("Log saved to: gesture_debug_log.txt")
        print("\nNow tell me what gestures you performed and what you saw!")

def main():
    debugger = GestureDebugger()
    debugger.start_debugging()

if __name__ == "__main__":
    main()