#!/usr/bin/env python3
"""
Mudra Simple Air Typing - Basic directional gestures that actually work
"""

import subprocess
import sys
import time
from pynput import keyboard, mouse
from pynput.keyboard import Key, Listener as KeyboardListener
from pynput.mouse import Listener as MouseListener

# Install pynput if needed
try:
    import pynput
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pynput"])

class SimpleAirTyping:
    def __init__(self):
        self.kb = keyboard.Controller()
        self.typing_mode = False
        self.start_pos = None
        self.gesture_active = False
        
        # Super simple gestures - just direction from start to end
        self.gestures = {
            'right': 'e',    # Most common letter
            'left': 't',     # Second most common
            'up': 'a',       # Third most common  
            'down': 'o',     # Fourth most common
            'up_right': 'i',
            'down_right': 'n',
            'up_left': 's', 
            'down_left': 'h',
        }
        
        self.min_distance = 50  # Minimum pixels to register gesture
    
    def get_gesture(self, start_x, start_y, end_x, end_y):
        """Get gesture from start to end position"""
        dx = end_x - start_x
        dy = end_y - start_y
        
        # Check if movement is big enough
        distance = (dx**2 + dy**2)**0.5
        if distance < self.min_distance:
            return None
        
        # Determine direction
        if abs(dx) > abs(dy) * 2:  # Mostly horizontal
            return 'right' if dx > 0 else 'left'
        elif abs(dy) > abs(dx) * 2:  # Mostly vertical
            return 'up' if dy < 0 else 'down'  # Note: y increases downward
        else:  # Diagonal
            if dx > 0 and dy < 0:
                return 'up_right'
            elif dx > 0 and dy > 0:
                return 'down_right'
            elif dx < 0 and dy < 0:
                return 'up_left'
            elif dx < 0 and dy > 0:
                return 'down_left'
        
        return None
    
    def on_mouse_click(self, x, y, button, pressed):
        """Handle mouse clicks for gesture start/end"""
        if not self.typing_mode:
            return
        
        if button == mouse.Button.left:
            if pressed:
                # Start gesture
                self.start_pos = (x, y)
                self.gesture_active = True
                print(f"Gesture start: ({x}, {y})")
            else:
                # End gesture
                if self.gesture_active and self.start_pos:
                    gesture = self.get_gesture(self.start_pos[0], self.start_pos[1], x, y)
                    if gesture and gesture in self.gestures:
                        letter = self.gestures[gesture]
                        self.kb.press(letter)
                        self.kb.release(letter)
                        print(f"✓ {gesture} → '{letter}'")
                    else:
                        print(f"? No gesture detected")
                
                self.gesture_active = False
                self.start_pos = None
        
        elif button == mouse.Button.right and pressed:
            # Right click = space
            self.kb.press(Key.space)
            self.kb.release(Key.space)
            print("✓ Space")
    
    def on_key_press(self, key):
        """Handle keyboard input"""
        # F1 = Toggle typing mode
        if key == Key.f1:
            self.typing_mode = not self.typing_mode
            mode = "AIR TYPING" if self.typing_mode else "MOUSE"
            print(f"\n🎯 {mode} MODE")
            if self.typing_mode:
                self.show_help()
            return
        
        if not self.typing_mode:
            return
        
        # ESC = Exit typing mode
        if key == Key.esc:
            self.typing_mode = False
            print("\n🖱️ MOUSE MODE")
    
    def show_help(self):
        """Show gesture help"""
        print("=== SIMPLE AIR GESTURES ===")
        print("Hold LEFT CLICK and drag, then release:")
        print("→ = 'e'    ← = 't'    ↑ = 'a'    ↓ = 'o'")
        print("↗ = 'i'    ↘ = 'n'    ↖ = 's'    ↙ = 'h'")
        print("RIGHT CLICK = space")
        print("ESC = mouse mode")
    
    def run(self):
        """Start air typing system"""
        print("🎯 SIMPLE AIR TYPING")
        print("Click and drag to make gestures!")
        print("\n=== SETUP ===")
        print("Assign in Mudra app: Twist → F1")
        print("\n=== USAGE ===")
        print("1. F1 (twist) → Enter air typing mode")
        print("2. HOLD left click and drag in a direction")
        print("3. RELEASE to type the letter")
        print("4. Right click → space")
        print("5. F1 again → back to mouse mode")
        print("\nPress any key to start...")
        input()
        
        print(f"\nMode: {'AIR TYPING' if self.typing_mode else 'MOUSE'}")
        print("Press Ctrl+C to exit")
        
        # Start listeners
        mouse_listener = MouseListener(on_click=self.on_mouse_click)
        keyboard_listener = KeyboardListener(on_press=self.on_key_press)
        
        mouse_listener.start()
        keyboard_listener.start()
        
        try:
            keyboard_listener.join()
        except KeyboardInterrupt:
            print("\nAir typing stopped")
        
        mouse_listener.stop()

if __name__ == "__main__":
    system = SimpleAirTyping()
    system.run()