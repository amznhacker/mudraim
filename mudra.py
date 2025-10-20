#!/usr/bin/env python3
"""
Mudra Air Typing - Draw letters in the air with mouse gestures
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

class MudraAirTyping:
    def __init__(self):
        self.kb = keyboard.Controller()
        self.typing_mode = False
        self.mouse_path = []
        self.last_pos = None
        self.gesture_timeout = 1.0  # 1 second to complete letter
        self.last_move_time = 0
        
        # Simple letter patterns based on mouse movement directions
        self.patterns = {
            # Straight lines
            'right': 'i',           # Straight line right
            'left': 'l',            # Straight line left  
            'up': 't',              # Straight line up
            'down': 'j',            # Straight line down
            
            # Simple shapes
            'right,down': 'r',      # L shape
            'down,right': 'r',      # L shape (reverse)
            'right,up': 'p',        # Reverse L
            'up,right': 'p',        # Reverse L (reverse)
            'left,down': 'f',       # Backwards L
            'down,left': 'f',       # Backwards L (reverse)
            'left,up': 'b',         # Backwards reverse L
            'up,left': 'b',         # Backwards reverse L (reverse)
            
            # Curves and loops
            'right,down,left': 'c', # C shape
            'left,down,right': 'u', # U shape
            'up,right,down': 'n',   # Arch
            'down,right,up': 'n',   # Arch (reverse)
            
            # Common letters with simple gestures
            'right,left': 'e',      # Back and forth = most common letter
            'up,down': 'a',         # Up and down = second most common
            'down,up': 'o',         # Down and up
            'left,right': 's',      # Left and right
            
            # Diagonal movements
            'right,down,right': 'k', # Zigzag
            'left,up,right': 'v',    # V shape
            'right,up,left': 'w',    # W shape (simplified)
            
            # More patterns
            'up,down,up': 'm',       # Mountain shape
            'down,up,down': 'h',     # Hill shape
            'right,up,right': 'y',   # Y shape
            'left,down,left': 'g',   # G shape
            'up,right,down,left': 'q', # Square
            'right,down,left,up': 'x', # X pattern
            'down,right,up,left': 'z', # Z pattern
        }
    
    def get_direction(self, x1, y1, x2, y2):
        """Get movement direction"""
        dx = x2 - x1
        dy = y2 - y1
        
        # Minimum movement threshold
        if abs(dx) < 10 and abs(dy) < 10:
            return None
            
        # Determine primary direction
        if abs(dx) > abs(dy):
            return 'right' if dx > 0 else 'left'
        else:
            return 'down' if dy > 0 else 'up'
    
    def process_gesture(self):
        """Process completed gesture and type letter"""
        if len(self.mouse_path) < 2:
            return
            
        # Convert path to direction sequence
        directions = []
        for i in range(len(self.mouse_path) - 1):
            x1, y1 = self.mouse_path[i]
            x2, y2 = self.mouse_path[i + 1]
            direction = self.get_direction(x1, y1, x2, y2)
            if direction and (not directions or directions[-1] != direction):
                directions.append(direction)
        
        # Match pattern
        pattern = ','.join(directions)
        if pattern in self.patterns:
            letter = self.patterns[pattern]
            self.kb.press(letter)
            self.kb.release(letter)
            print(f"✓ {pattern} → '{letter}'")
        else:
            print(f"? Unknown: {pattern}")
        
        self.mouse_path = []
    
    def on_mouse_move(self, x, y):
        """Track mouse movement for air typing"""
        if not self.typing_mode:
            return
            
        current_time = time.time()
        
        # Reset if timeout
        if current_time - self.last_move_time > self.gesture_timeout:
            if self.mouse_path:
                self.process_gesture()
            self.mouse_path = []
        
        self.mouse_path.append((x, y))
        self.last_move_time = current_time
        
        # Limit path length
        if len(self.mouse_path) > 20:
            self.mouse_path = self.mouse_path[-10:]
    
    def on_mouse_click(self, x, y, button, pressed):
        """Handle mouse clicks"""
        if not self.typing_mode:
            return
            
        if pressed and button == mouse.Button.left:
            # Left click = space
            self.kb.press(Key.space)
            self.kb.release(Key.space)
            print("✓ Click → space")
        elif pressed and button == mouse.Button.right:
            # Right click = process current gesture
            self.process_gesture()
    
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
            return
        
        # Backspace
        if key == Key.backspace:
            print("← backspace")
            return
        
        # Enter
        if key == Key.enter:
            print("↵ enter")
            return
    
    def show_help(self):
        """Show air typing help"""
        print("=== AIR TYPING PATTERNS ===")
        print("Draw letters in the air with mouse movement:")
        print("→ = 'i'    ← = 'l'    ↑ = 't'    ↓ = 'j'")
        print("→← = 'e'   ↑↓ = 'a'   ↓↑ = 'o'   ←→ = 's'")
        print("→↓ = 'r'   ↑→ = 'p'   ←↓ = 'f'   ←↑ = 'b'")
        print("Left click = space")
        print("Right click = finish letter")
        print("ESC = mouse mode")
    
    def run(self):
        """Start air typing system"""
        print("🎯 MUDRA AIR TYPING")
        print("Draw letters in the air with mouse gestures!")
        print("\n=== SETUP ===")
        print("Mouse Mode: Twist → F1")
        print("\n=== USAGE ===")
        print("1. F1 (twist) → Enter air typing mode")
        print("2. Move mouse to draw letter shapes in the air")
        print("3. Left click → space")
        print("4. Right click → finish current letter")
        print("5. F1 again → back to mouse mode")
        print("\nPress any key to start...")
        input()
        
        print(f"\nMode: {'AIR TYPING' if self.typing_mode else 'MOUSE'}")
        print("Press Ctrl+C to exit")
        
        # Start listeners
        mouse_listener = MouseListener(
            on_move=self.on_mouse_move,
            on_click=self.on_mouse_click
        )
        keyboard_listener = KeyboardListener(on_press=self.on_key_press)
        
        mouse_listener.start()
        keyboard_listener.start()
        
        try:
            keyboard_listener.join()
        except KeyboardInterrupt:
            print("\nAir typing stopped")
        
        mouse_listener.stop()

if __name__ == "__main__":
    system = MudraAirTyping()
    system.run()