#!/usr/bin/env python3
"""
Mudra Improved Gesture Typing - Fixed horizontal detection and simplified double gestures
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

class ImprovedMudraTyping:
    def __init__(self):
        self.kb = keyboard.Controller()
        self.typing_mode = False
        self.start_pos = None
        self.gesture_active = False
        
        # Simplified - only single gestures that work reliably
        self.gestures = {
            'right': 'e',        # Most common
            'left': 't',         
            'up': 'a',           
            'down': 'o',         
            'up_right': 'i',     
            'down_right': 'n',   
            'up_left': 's',      
            'down_left': 'h',
            # Add more common letters to single gestures
            'double_right': 'r',    # Quick double right
            'double_left': 'd',     # Quick double left
            'double_up': 'l',       # Quick double up
            'double_down': 'c',     # Quick double down
        }
        
        self.min_distance = 30  # Reduced for better sensitivity
        self.last_gesture = None
        self.last_gesture_time = 0
        self.double_gesture_window = 0.5  # 500ms for double gesture
    
    def get_direction(self, start_x, start_y, end_x, end_y):
        """Improved direction detection with better horizontal handling"""
        dx = end_x - start_x
        dy = end_y - start_y
        
        distance = (dx**2 + dy**2)**0.5
        if distance < self.min_distance:
            return None
        
        # More forgiving horizontal/vertical detection
        abs_dx = abs(dx)
        abs_dy = abs(dy)
        
        # Pure horizontal (more lenient)
        if abs_dx > abs_dy * 1.5:  # Was 2, now 1.5 for easier horizontal
            return 'right' if dx > 0 else 'left'
        
        # Pure vertical (more lenient)
        elif abs_dy > abs_dx * 1.5:  # Was 2, now 1.5 for easier vertical
            return 'up' if dy < 0 else 'down'
        
        # Diagonal - only if clearly diagonal
        else:
            if dx > 0 and dy < 0:
                return 'up_right'
            elif dx > 0 and dy > 0:
                return 'down_right'
            elif dx < 0 and dy < 0:
                return 'up_left'
            elif dx < 0 and dy > 0:
                return 'down_left'
        
        return None
    
    def process_gesture(self, gesture):
        """Process gesture with improved double gesture detection"""
        current_time = time.time()
        
        # Check for double gesture (same direction twice quickly)
        if (self.last_gesture == gesture and 
            current_time - self.last_gesture_time < self.double_gesture_window):
            
            double_gesture = f"double_{gesture}"
            if double_gesture in self.gestures:
                letter = self.gestures[double_gesture]
                self.type_letter(letter)
                print(f"✓ {gesture}+{gesture} → '{letter}'")
                self.last_gesture = None  # Reset to prevent triple
                return
        
        # Single gesture
        if gesture in self.gestures:
            letter = self.gestures[gesture]
            self.type_letter(letter)
            print(f"✓ {gesture} → '{letter}'")
        else:
            print(f"? {gesture}")
        
        self.last_gesture = gesture
        self.last_gesture_time = current_time
    
    def type_letter(self, letter):
        """Type a letter"""
        self.kb.press(letter)
        self.kb.release(letter)
    
    def on_mouse_click(self, x, y, button, pressed):
        """Handle mouse clicks with better gesture detection"""
        if not self.typing_mode:
            return
        
        if button == mouse.Button.left:
            if pressed:
                self.start_pos = (x, y)
                self.gesture_active = True
                print(f"Start: ({x}, {y})")  # Debug
            else:
                if self.gesture_active and self.start_pos:
                    gesture = self.get_direction(self.start_pos[0], self.start_pos[1], x, y)
                    if gesture:
                        dx = x - self.start_pos[0]
                        dy = y - self.start_pos[1]
                        distance = (dx**2 + dy**2)**0.5
                        print(f"End: ({x}, {y}), Distance: {distance:.1f}, Direction: {gesture}")  # Debug
                        self.process_gesture(gesture)
                    else:
                        print(f"No gesture detected (too small or unclear)")
                self.gesture_active = False
                self.start_pos = None
        
        elif button == mouse.Button.right and pressed:
            self.kb.press(Key.space)
            self.kb.release(Key.space)
            print("✓ Space")
    
    def on_key_press(self, key):
        """Handle keyboard input"""
        if key == Key.f1:
            self.typing_mode = not self.typing_mode
            mode = "IMPROVED TYPING" if self.typing_mode else "MOUSE"
            print(f"\n🎯 {mode} MODE")
            if self.typing_mode:
                self.show_help()
            return
        
        if not self.typing_mode:
            return
        
        if key == Key.esc:
            self.typing_mode = False
            print("\n🖱️ MOUSE MODE")
        elif key == Key.backspace:
            print("← Backspace")
    
    def show_help(self):
        """Show improved gesture reference"""
        print("=== IMPROVED GESTURES ===")
        print("Single gestures:")
        print("→ e  ← t  ↑ a  ↓ o")
        print("↗ i  ↘ n  ↖ s  ↙ h")
        print("\nDouble gestures (same direction twice):")
        print("→→ r  ←← d  ↑↑ l  ↓↓ c")
        print("\nTips:")
        print("- Make clear, deliberate gestures")
        print("- Horizontal gestures are now easier")
        print("- Double gestures: quick repeat in same direction")
    
    def run(self):
        """Start the improved system"""
        print("🎯 MUDRA IMPROVED TYPING")
        print("Fixed horizontal detection and simplified double gestures!")
        print("\n=== IMPROVEMENTS ===")
        print("✓ Better horizontal gesture detection")
        print("✓ Simplified double gestures (same direction twice)")
        print("✓ Debug output to help you learn")
        print("✓ More forgiving gesture recognition")
        print("\n=== SETUP ===")
        print("Assign in Mudra: Twist → F1")
        print("\n=== USAGE ===")
        print("1. F1 → typing mode")
        print("2. Drag clearly in directions")
        print("3. Double gestures: same direction twice quickly")
        print("4. Right click → space")
        print("\nPress any key to start...")
        input()
        
        print(f"\nMode: {'IMPROVED TYPING' if self.typing_mode else 'MOUSE'}")
        print("Watch the debug output to learn gesture patterns!")
        
        mouse_listener = MouseListener(on_click=self.on_mouse_click)
        keyboard_listener = KeyboardListener(on_press=self.on_key_press)
        
        mouse_listener.start()
        keyboard_listener.start()
        
        try:
            keyboard_listener.join()
        except KeyboardInterrupt:
            print("\nImproved typing stopped")
        
        mouse_listener.stop()

if __name__ == "__main__":
    system = ImprovedMudraTyping()
    system.run()