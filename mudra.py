#!/usr/bin/env python3
"""
Mudra Complete System - Mouse + Fast Gesture Typing
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

class MudraSystem:
    def __init__(self):
        self.kb = keyboard.Controller()
        self.typing_mode = False
        
        # Chord-based typing (inspired by stenography)
        # Maps gesture combinations to letters
        self.chords = {
            # Single gestures - most common letters (80% of text)
            ('right',): 'e',        # 12.7% frequency
            ('left',): 't',         # 9.1% frequency  
            ('up',): 'a',           # 8.2% frequency
            ('down',): 'o',         # 7.5% frequency
            
            # Two-gesture combinations - common letters
            ('right', 'up'): 'i',      # 7.0%
            ('right', 'down'): 'n',    # 6.7%
            ('left', 'up'): 's',       # 6.3%
            ('left', 'down'): 'h',     # 6.1%
            ('up', 'down'): 'r',       # 6.0%
            ('right', 'left'): 'd',    # 4.3%
            
            # Three-gesture combinations
            ('right', 'up', 'down'): 'l',     # 4.0%
            ('left', 'up', 'down'): 'c',      # 2.8%
            ('right', 'left', 'up'): 'u',     # 2.8%
            ('right', 'left', 'down'): 'm',   # 2.4%
            
            # Using twist for space and common letters
            ('twist',): ' ',           # Space (most important)
            ('twist', 'right'): 'w',   # 2.4%
            ('twist', 'left'): 'f',    # 2.2%
            ('twist', 'up'): 'g',      # 2.0%
            ('twist', 'down'): 'y',    # 2.0%
            
            # Using double twist
            ('dtwist',): '.',          # Period
            ('dtwist', 'right'): 'p',  # 1.9%
            ('dtwist', 'left'): 'b',   # 1.3%
            ('dtwist', 'up'): 'v',     # 1.0%
            ('dtwist', 'down'): 'k',   # 0.8%
            
            # Complex combinations for rare letters
            ('right', 'twist'): 'j',   # 0.15%
            ('left', 'twist'): 'x',    # 0.15%
            ('up', 'twist'): 'q',      # 0.10%
            ('down', 'twist'): 'z',    # 0.07%
            
            # Special
            ('enter',): '\n',          # Enter/newline
        }
        
        self.current_chord = []
        self.chord_timeout = 0.8  # 800ms to complete chord
        self.last_gesture_time = 0
        
    def process_gesture(self, gesture):
        """Process gesture and build chord"""
        current_time = time.time()
        
        # Reset chord if timeout
        if current_time - self.last_gesture_time > self.chord_timeout:
            self.current_chord = []
        
        self.current_chord.append(gesture)
        self.last_gesture_time = current_time
        
        # Try to match chord
        chord_tuple = tuple(sorted(self.current_chord))
        
        if chord_tuple in self.chords:
            char = self.chords[chord_tuple]
            self.type_character(char)
            self.current_chord = []
            return True
        
        # Reset if chord too long
        if len(self.current_chord) > 3:
            print(f"Unknown: {self.current_chord}")
            self.current_chord = []
        
        return False
    
    def type_character(self, char):
        """Type character"""
        if char == '\n':
            self.kb.press(Key.enter)
            self.kb.release(Key.enter)
            print("↵")
        else:
            self.kb.press(char)
            self.kb.release(char)
            print(f"→ {char}")
    
    def on_key_press(self, key):
        """Handle all input"""
        # F1 = Toggle typing mode (from mouse mode twist)
        if key == Key.f1:
            self.typing_mode = not self.typing_mode
            mode = "TYPING" if self.typing_mode else "MOUSE"
            print(f"\n🔄 {mode} MODE")
            if self.typing_mode:
                self.show_help()
            return
        
        # Only process gestures in typing mode
        if not self.typing_mode:
            return
        
        # Map keyboard mode gestures
        gesture = None
        if key == Key.right:
            gesture = 'right'
        elif key == Key.left:
            gesture = 'left'
        elif key == Key.up:
            gesture = 'up'
        elif key == Key.down:
            gesture = 'down'
        elif key == Key.enter:
            gesture = 'enter'
        elif key == Key.f2:
            gesture = 'twist'
        elif key == Key.f3:
            gesture = 'dtwist'
        elif key == Key.esc:
            self.typing_mode = False
            print("\n📱 MOUSE MODE")
            return
        
        if gesture:
            self.process_gesture(gesture)
    
    def show_help(self):
        """Show chord reference"""
        print("=== GESTURE CHORDS ===")
        print("Single: Right→e  Left→t  Up→a  Down→o")
        print("Combos: Right+Up→i  Right+Down→n  Left+Up→s")
        print("Space: Twist    Period: Double-twist")
        print("ESC = Mouse mode")
    
    def train(self):
        """Training mode"""
        print("\n🎯 TRAINING MODE")
        print("Practice common words:")
        
        words = ['to', 'the', 'and', 'it', 'at', 'he']
        
        for word in words:
            print(f"\nWord: '{word}'")
            for char in word:
                for chord, letter in self.chords.items():
                    if letter == char:
                        print(f"  '{char}' → {'+'.join(chord)}")
                        break
            input("Practice this word, then press Enter...")
    
    def run(self):
        """Main system"""
        print("🎯 MUDRA COMPLETE SYSTEM")
        print("Mouse + Fast Gesture Typing")
        print("\n=== SETUP INSTRUCTIONS ===")
        print("1. MOUSE MODE (default Mudra gestures work)")
        print("2. KEYBOARD MODE (double-press Mudra button):")
        print("   • Pinch+Right → Right Arrow")
        print("   • Pinch+Left → Left Arrow")
        print("   • Pinch+Up → Up Arrow") 
        print("   • Pinch+Down → Down Arrow")
        print("   • Double-tap → Enter")
        print("   • Twist → F2")
        print("   • Double-twist → F3")
        print("3. Mouse mode twist → F1")
        print("\n=== USAGE ===")
        print("• Browse with mouse gestures")
        print("• F1 (twist) = Enter typing mode")
        print("• Use gesture combinations to type")
        print("• F1 again = Back to mouse")
        print("\nPress 't' for training, or any key to start...")
        
        choice = input().strip().lower()
        if choice == 't':
            self.train()
        
        print(f"\nCurrent mode: {'TYPING' if self.typing_mode else 'MOUSE'}")
        print("Press Ctrl+C to exit")
        
        with Listener(on_press=self.on_key_press) as listener:
            try:
                listener.join()
            except KeyboardInterrupt:
                print("\nMudra system stopped")

if __name__ == "__main__":
    system = MudraSystem()
    system.run()