#!/usr/bin/env python3
"""
Mudra Keyboard Mode Typing - Using actual keyboard gestures
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

class MudraKeyboardTyping:
    def __init__(self):
        self.kb = keyboard.Controller()
        self.typing_mode = False
        
        # Single gestures - most common letters (covers 65% of text)
        self.single_gestures = {
            Key.right: 'e',        # PINCH + RIGHT → 'e' (12.7%)
            Key.left: 't',         # PINCH + LEFT → 't' (9.1%)
            Key.up: 'a',           # PINCH + UP → 'a' (8.2%)
            Key.down: 'o',         # PINCH + DOWN → 'o' (7.5%)
            Key.enter: 'i',        # DOUBLE TAP → 'i' (7.0%)
        }
        
        # Assign twist and double twist
        self.twist_key = Key.f2      # Will assign TWIST → F2
        self.double_twist_key = Key.f3  # Will assign DOUBLE TWIST → F3
        
        # More letters using twist combinations
        self.twist_gestures = {
            (self.twist_key, Key.right): 'n',   # TWIST + RIGHT → 'n' (6.7%)
            (self.twist_key, Key.left): 's',    # TWIST + LEFT → 's' (6.3%)
            (self.twist_key, Key.up): 'h',      # TWIST + UP → 'h' (6.1%)
            (self.twist_key, Key.down): 'r',    # TWIST + DOWN → 'r' (6.0%)
            (self.twist_key, Key.enter): 'd',   # TWIST + DOUBLE TAP → 'd' (4.3%)
        }
        
        # Double twist for more letters
        self.double_twist_gestures = {
            (self.double_twist_key, Key.right): 'l',  # DOUBLE TWIST + RIGHT → 'l' (4.0%)
            (self.double_twist_key, Key.left): 'c',   # DOUBLE TWIST + LEFT → 'c' (2.8%)
            (self.double_twist_key, Key.up): 'u',     # DOUBLE TWIST + UP → 'u' (2.8%)
            (self.double_twist_key, Key.down): 'm',   # DOUBLE TWIST + DOWN → 'm' (2.4%)
            (self.double_twist_key, Key.enter): 'w',  # DOUBLE TWIST + DOUBLE TAP → 'w' (2.4%)
        }
        
        # Special functions
        self.space_key = self.twist_key  # TWIST alone → space
        self.backspace_key = self.double_twist_key  # DOUBLE TWIST alone → backspace
        
        # Combo tracking
        self.last_key = None
        self.last_key_time = 0
        self.combo_timeout = 0.5  # 500ms for combinations
    
    def process_key(self, key):
        """Process keyboard gesture"""
        current_time = time.time()
        
        # Check for combinations with twist/double twist
        if self.last_key and current_time - self.last_key_time < self.combo_timeout:
            combo = (self.last_key, key)
            
            # Check twist combinations
            if combo in self.twist_gestures:
                letter = self.twist_gestures[combo]
                self.type_letter(letter)
                print(f"✓ TWIST+{key.name} → '{letter}'")
                self.last_key = None
                return
            
            # Check double twist combinations
            if combo in self.double_twist_gestures:
                letter = self.double_twist_gestures[combo]
                self.type_letter(letter)
                print(f"✓ DOUBLE TWIST+{key.name} → '{letter}'")
                self.last_key = None
                return
        
        # Single gestures
        if key in self.single_gestures:
            letter = self.single_gestures[key]
            self.type_letter(letter)
            print(f"✓ {key.name} → '{letter}'")
        
        # Special keys
        elif key == self.space_key:
            # Check if it's part of a combo or standalone
            if self.last_key and current_time - self.last_key_time < self.combo_timeout:
                # It's part of a combo, wait for next key
                pass
            else:
                # Standalone twist = space
                self.kb.press(Key.space)
                self.kb.release(Key.space)
                print("✓ TWIST → space")
        
        elif key == self.backspace_key:
            # Check if it's part of a combo or standalone
            if self.last_key and current_time - self.last_key_time < self.combo_timeout:
                # It's part of a combo, wait for next key
                pass
            else:
                # Standalone double twist = backspace
                self.kb.press(Key.backspace)
                self.kb.release(Key.backspace)
                print("✓ DOUBLE TWIST → backspace")
        
        else:
            print(f"? Unknown key: {key}")
        
        self.last_key = key
        self.last_key_time = current_time
    
    def type_letter(self, letter):
        """Type a letter"""
        self.kb.press(letter)
        self.kb.release(letter)
    
    def on_key_press(self, key):
        """Handle all key presses"""
        # F1 = Toggle typing mode (assign TWIST in mouse mode to F1)
        if key == Key.f1:
            self.typing_mode = not self.typing_mode
            mode = "KEYBOARD TYPING" if self.typing_mode else "MOUSE"
            print(f"\n🎯 {mode} MODE")
            if self.typing_mode:
                self.show_help()
            return
        
        # Only process gestures in typing mode
        if not self.typing_mode:
            return
        
        # ESC = Exit typing mode
        if key == Key.esc:
            self.typing_mode = False
            print("\n🖱️ MOUSE MODE")
            return
        
        # Process keyboard gestures
        self.process_key(key)
    
    def show_help(self):
        """Show gesture reference"""
        print("=== KEYBOARD MODE GESTURES ===")
        print("Single gestures:")
        print("  PINCH+RIGHT → 'e'    PINCH+LEFT → 't'")
        print("  PINCH+UP → 'a'       PINCH+DOWN → 'o'")
        print("  DOUBLE TAP → 'i'")
        print("\nTwist combinations:")
        print("  TWIST+RIGHT → 'n'    TWIST+LEFT → 's'")
        print("  TWIST+UP → 'h'       TWIST+DOWN → 'r'")
        print("  TWIST alone → space")
        print("\nDouble twist combinations:")
        print("  DOUBLE TWIST+RIGHT → 'l'    DOUBLE TWIST+LEFT → 'c'")
        print("  DOUBLE TWIST alone → backspace")
        print("\nESC = mouse mode")
    
    def run(self):
        """Start the system"""
        print("🎯 MUDRA KEYBOARD MODE TYPING")
        print("Using your actual keyboard mode gestures!")
        print("\n=== SETUP ===")
        print("Mouse Mode: Twist → F1")
        print("Keyboard Mode: Twist → F2, Double-twist → F3")
        print("\n=== USAGE ===")
        print("F1 → typing mode, use gestures, F1 → mouse mode")
        print("\nPress Enter to start...")
        input()
        
        print(f"\nCurrent mode: {'KEYBOARD TYPING' if self.typing_mode else 'MOUSE'}")
        print("Press Ctrl+C to exit")
        
        with KeyboardListener(on_press=self.on_key_press) as listener:
            try:
                listener.join()
            except KeyboardInterrupt:
                print("\nMudra keyboard typing stopped")

if __name__ == "__main__":
    system = MudraKeyboardTyping()
    system.run()