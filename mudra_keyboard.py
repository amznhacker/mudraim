#!/usr/bin/env python3
"""
Mudra Keyboard System - Detects twist gestures and adds typing
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

class MudraKeyboard:
    def __init__(self):
        self.kb = keyboard.Controller()
        self.typing_mode = False
        self.layer = 0
        
        # Track pressed keys for combinations
        self.pressed_keys = set()
        
        # Character maps for positions 0-8
        self.chars = [
            ['a','b','c','d','e','f','g','h','i'],  # Letters
            ['1','2','3','4','5','6','7','8','9'],  # Numbers  
            ['!','@','#','$','%','^','&','*','(']   # Symbols
        ]
        
        print("🎯 Mudra Keyboard System Started")
        print("Your mouse already works perfectly!")
        print("\n=== SETUP INSTRUCTIONS ===")
        print("In your Mudra app, assign these shortcuts:")
        print("• Single twist → F1 key")
        print("• Double twist → F2 key")
        print("\n=== HOW TO USE ===")
        print("1. Use mouse normally (already working)")
        print("2. F1 (twist) = Toggle typing mode")
        print("3. F2 (double twist) = Switch layers")
        print("4. Number keys 0-8 = Type characters")
        print("\nPress Ctrl+C to stop")
        
    def on_key_press(self, key):
        """Handle key presses"""
        self.pressed_keys.add(key)
        
        try:
            # F1 = Single twist = Toggle typing mode
            if key == Key.f1:
                self.toggle_typing_mode()
                return
            
            # F2 = Double twist = Switch layers
            if key == Key.f2:
                self.switch_layer()
                return
            
            # Number keys for typing (only in typing mode)
            if self.typing_mode and hasattr(key, 'char') and key.char:
                if key.char.isdigit():
                    pos = int(key.char)
                    if 0 <= pos <= 8:
                        self.type_character(pos)
                        return
            
            # Backspace in typing mode
            if self.typing_mode and key == Key.backspace:
                print("Backspace")
                return
                
        except AttributeError:
            pass
    
    def on_key_release(self, key):
        """Handle key releases"""
        try:
            self.pressed_keys.discard(key)
        except KeyError:
            pass
        
        # Exit on Escape
        if key == Key.esc:
            print("\nStopping Mudra Keyboard...")
            return False
    
    def toggle_typing_mode(self):
        """Toggle between mouse and typing mode"""
        self.typing_mode = not self.typing_mode
        mode = "TYPING" if self.typing_mode else "MOUSE"
        print(f"\n🔄 Switched to {mode} mode")
        
        if self.typing_mode:
            print("Ready to type! Use number keys 0-8:")
            self.show_current_layer()
        else:
            print("Back to mouse mode")
    
    def switch_layer(self):
        """Switch typing layers"""
        if self.typing_mode:
            self.layer = (self.layer + 1) % 3
            layers = ['Letters', 'Numbers', 'Symbols']
            print(f"\n🔄 Switched to {layers[self.layer]} layer")
            self.show_current_layer()
        else:
            print("\n💡 Enter typing mode first (F1/twist)")
    
    def type_character(self, pos):
        """Type character at position"""
        if pos < len(self.chars[self.layer]):
            char = self.chars[self.layer][pos]
            self.kb.press(char)
            self.kb.release(char)
            print(f"Typed: {char}")
    
    def show_current_layer(self):
        """Show current character layout"""
        layer_name = ['Letters', 'Numbers', 'Symbols'][self.layer]
        print(f"\n{layer_name}:")
        chars = self.chars[self.layer]
        for i in range(0, 9, 3):
            row = chars[i:i+3]
            positions = [f"{j}:{char}" for j, char in enumerate(row, i)]
            print(f"  {' '.join(positions)}")
    
    def start(self):
        """Start the keyboard system"""
        print(f"\nCurrent mode: {'TYPING' if self.typing_mode else 'MOUSE'}")
        
        # Start listening for key presses
        with Listener(on_press=self.on_key_press, on_release=self.on_key_release) as listener:
            try:
                listener.join()
            except KeyboardInterrupt:
                print("\nMudra Keyboard stopped")

if __name__ == "__main__":
    keyboard_system = MudraKeyboard()
    keyboard_system.start()