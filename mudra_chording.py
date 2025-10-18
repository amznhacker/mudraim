#!/usr/bin/env python3
"""
Mudra Chording System - Fast gesture typing based on research
Uses chord combinations for efficient text input
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

class MudraChordingSystem:
    def __init__(self):
        self.kb = keyboard.Controller()
        self.typing_mode = False
        
        # Available gestures in keyboard mode
        self.gestures = {
            'right': Key.right,      # Pinch + right
            'left': Key.left,        # Pinch + left  
            'up': Key.up,           # Pinch + up
            'down': Key.down,       # Pinch + down
            'enter': Key.enter,     # Double tap
            'twist': Key.f1,        # Twist (unassigned)
            'dtwist': Key.f2        # Double twist (unassigned)
        }
        
        # Chord-based character mapping (inspired by stenography)
        # Using combinations of directional gestures for letters
        self.chords = {
            # Single gestures - most common letters
            ('right',): 'e',        # Most common letter
            ('left',): 't',         # Second most common
            ('up',): 'a',           # Third most common
            ('down',): 'o',         # Fourth most common
            
            # Two-gesture combinations - common letters
            ('right', 'up'): 'i',
            ('right', 'down'): 'n',
            ('left', 'up'): 's',
            ('left', 'down'): 'h',
            ('up', 'down'): 'r',
            ('right', 'left'): 'd',
            
            # Three-gesture combinations - less common letters
            ('right', 'up', 'down'): 'l',
            ('left', 'up', 'down'): 'c',
            ('right', 'left', 'up'): 'u',
            ('right', 'left', 'down'): 'm',
            
            # Special combinations
            ('twist',): ' ',        # Space
            ('dtwist',): '.',       # Period
            ('enter',): '\n',       # Enter/newline
            
            # More letters using twist combinations
            ('twist', 'right'): 'w',
            ('twist', 'left'): 'f',
            ('twist', 'up'): 'g',
            ('twist', 'down'): 'y',
            
            # Double twist combinations
            ('dtwist', 'right'): 'p',
            ('dtwist', 'left'): 'b',
            ('dtwist', 'up'): 'v',
            ('dtwist', 'down'): 'k',
            
            # Complex combinations for remaining letters
            ('right', 'twist'): 'j',
            ('left', 'twist'): 'x',
            ('up', 'twist'): 'q',
            ('down', 'twist'): 'z',
        }
        
        # Word prediction based on frequency
        self.common_words = {
            'th': 'the',
            'an': 'and', 
            'yo': 'you',
            'to': 'to',
            'of': 'of',
            'it': 'it',
            'in': 'in',
            'is': 'is',
            'he': 'he',
            'ha': 'have'
        }
        
        self.current_chord = []
        self.chord_timeout = 0.5  # 500ms to complete chord
        self.last_gesture_time = 0
        
    def process_gesture(self, gesture):
        """Process a gesture and add to current chord"""
        current_time = time.time()
        
        # If too much time passed, start new chord
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
        
        # If chord gets too long, reset
        if len(self.current_chord) > 4:
            print(f"Unknown chord: {self.current_chord}")
            self.current_chord = []
        
        return False
    
    def type_character(self, char):
        """Type a character with word prediction"""
        if char == '\n':
            self.kb.press(Key.enter)
            self.kb.release(Key.enter)
            print("↵")
        else:
            self.kb.press(char)
            self.kb.release(char)
            print(f"Typed: {char}")
    
    def on_key_press(self, key):
        """Handle gesture detection"""
        if not self.typing_mode:
            # F1 toggles typing mode
            if key == Key.f1:
                self.typing_mode = True
                print("\n🎯 CHORDING MODE ACTIVE")
                print("Use gesture combinations to type!")
                self.show_chord_help()
            return
        
        # In typing mode, detect gestures
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
        elif key == Key.f1:
            gesture = 'twist'
        elif key == Key.f2:
            gesture = 'dtwist'
        elif key == Key.esc:
            self.typing_mode = False
            print("\n📱 MOUSE MODE ACTIVE")
            return
        
        if gesture:
            self.process_gesture(gesture)
    
    def show_chord_help(self):
        """Show available chords"""
        print("\n=== CHORD REFERENCE ===")
        print("Single gestures:")
        print("  Right → 'e'    Left → 't'")
        print("  Up → 'a'       Down → 'o'")
        print("  Twist → space  Double-twist → '.'")
        print("\nTwo-gesture combinations:")
        print("  Right+Up → 'i'     Right+Down → 'n'")
        print("  Left+Up → 's'      Left+Down → 'h'")
        print("  Up+Down → 'r'      Right+Left → 'd'")
        print("\nPress ESC to return to mouse mode")
    
    def run(self):
        """Start the chording system"""
        print("🎯 MUDRA CHORDING SYSTEM")
        print("Based on stenography research for fast gesture typing!")
        print("\nSETUP:")
        print("1. Switch Mudra to keyboard mode (double-press button)")
        print("2. Assign gestures:")
        print("   - Pinch+Right → Right Arrow")
        print("   - Pinch+Left → Left Arrow") 
        print("   - Pinch+Up → Up Arrow")
        print("   - Pinch+Down → Down Arrow")
        print("   - Double-tap → Enter")
        print("   - Twist → F1")
        print("   - Double-twist → F2")
        print("\n3. Press F1 (twist) to start typing")
        print("4. Use gesture combinations (chords) to type letters")
        print("5. Press ESC to return to mouse mode")
        print("\nPress Ctrl+C to exit")
        
        with Listener(on_press=self.on_key_press) as listener:
            try:
                listener.join()
            except KeyboardInterrupt:
                print("\nMudra Chording System stopped")

if __name__ == "__main__":
    system = MudraChordingSystem()
    system.run()