#!/usr/bin/env python3
"""
Mudra Complete Keyboard - All 26 letters, numbers, symbols + Simple Training
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

class MudraCompleteSystem:
    def __init__(self):
        self.kb = keyboard.Controller()
        
        # Simple gesture mapping
        self.gestures = {
            # Single gestures (5 most common letters)
            Key.right: 'e',
            Key.left: 't', 
            Key.up: 'a',
            Key.down: 'o',
            Key.enter: 'i',
        }
        
        # F2 combinations (twist + direction)
        self.f2_combos = {
            Key.right: 'n',
            Key.left: 's',
            Key.up: 'h', 
            Key.down: 'r',
            Key.enter: 'd',
        }
        
        # F3 combinations (double twist + direction)
        self.f3_combos = {
            Key.right: 'l',
            Key.left: 'c',
            Key.up: 'u',
            Key.down: 'm',
            Key.enter: 'w',
        }
        
        # Remaining letters (need double combos)
        self.double_combos = {
            ('f2f3', Key.right): 'f',
            ('f2f3', Key.left): 'g',
            ('f2f3', Key.up): 'y',
            ('f2f3', Key.down): 'p',
            ('f2f3', Key.enter): 'b',
            ('f3f2', Key.right): 'v',
            ('f3f2', Key.left): 'k',
            ('f3f2', Key.up): 'j',
            ('f3f2', Key.down): 'x',
            ('f3f2', Key.enter): 'q',
        }
        
        # Numbers (F2→F3 mode)
        self.numbers = {
            Key.right: '1',
            Key.left: '2',
            Key.up: '3',
            Key.down: '4',
            Key.enter: '5',
        }
        
        # State tracking
        self.waiting_for_combo = None
        self.combo_start_time = 0
        self.combo_timeout = 0.8
        self.mode = 'normal'  # normal, number, f2f3, f3f2
        
        # Training words
        self.training_words = ['the', 'and', 'you', 'that', 'it', 'to', 'at', 'be', 'or', 'an']
        self.current_word_index = 0
    
    def type_char(self, char):
        """Type a character"""
        if char == 'SPACE':
            self.kb.press(Key.space)
            self.kb.release(Key.space)
            print("→ space")
        elif char == 'BACKSPACE':
            self.kb.press(Key.backspace)
            self.kb.release(Key.backspace)
            print("→ backspace")
        else:
            self.kb.press(char)
            self.kb.release(char)
            print(f"→ {char}")
    
    def on_key_press(self, key):
        """Handle key presses"""
        current_time = time.time()
        
        # Handle timeouts
        if self.waiting_for_combo and current_time - self.combo_start_time > self.combo_timeout:
            if self.waiting_for_combo == 'f2':
                self.type_char('SPACE')
            elif self.waiting_for_combo == 'f3':
                self.type_char('BACKSPACE')
            elif self.waiting_for_combo == 'f2f3':
                self.mode = 'number'
                print("Number mode active")
            elif self.waiting_for_combo == 'f3f2':
                print("Symbol mode active")
            
            self.waiting_for_combo = None
            self.mode = 'normal'
        
        # Handle current key based on state
        if self.waiting_for_combo:
            if self.waiting_for_combo == 'f2' and key in self.f2_combos:
                self.type_char(self.f2_combos[key])
                self.waiting_for_combo = None
                return
            elif self.waiting_for_combo == 'f3' and key in self.f3_combos:
                self.type_char(self.f3_combos[key])
                self.waiting_for_combo = None
                return
            elif self.waiting_for_combo == 'f2f3' and key in self.double_combos:
                combo_key = ('f2f3', key)
                if combo_key in self.double_combos:
                    self.type_char(self.double_combos[combo_key])
                self.waiting_for_combo = None
                self.mode = 'normal'
                return
            elif self.waiting_for_combo == 'f3f2' and key in self.double_combos:
                combo_key = ('f3f2', key)
                if combo_key in self.double_combos:
                    self.type_char(self.double_combos[combo_key])
                self.waiting_for_combo = None
                self.mode = 'normal'
                return
        
        # Handle new keys
        if key in self.gestures:
            self.type_char(self.gestures[key])
        
        elif key == Key.f2:
            if self.waiting_for_combo == 'f3':
                # F3 then F2 = f3f2 mode
                self.waiting_for_combo = 'f3f2'
                self.combo_start_time = current_time
            else:
                self.waiting_for_combo = 'f2'
                self.combo_start_time = current_time
        
        elif key == Key.f3:
            if self.waiting_for_combo == 'f2':
                # F2 then F3 = f2f3 mode
                self.waiting_for_combo = 'f2f3'
                self.combo_start_time = current_time
            else:
                self.waiting_for_combo = 'f3'
                self.combo_start_time = current_time
        
        elif key == Key.f1:
            self.show_training()
        
        elif key == Key.esc:
            print("\nExiting...")
            return False
    
    def show_training(self):
        """Show training for current word"""
        word = self.training_words[self.current_word_index]
        print(f"\n=== TRAINING WORD: '{word.upper()}' ===")
        
        for char in word:
            gesture = self.get_gesture_for_char(char)
            print(f"'{char}' = {gesture}")
        
        print(f"\nType '{word}' using the gestures above")
        print("F1 = next word, ESC = exit")
        
        self.current_word_index = (self.current_word_index + 1) % len(self.training_words)
    
    def get_gesture_for_char(self, char):
        """Get gesture for character"""
        # Single gestures
        for key, value in self.gestures.items():
            if value == char:
                return key.name.upper()
        
        # F2 combos
        for key, value in self.f2_combos.items():
            if value == char:
                return f"F2+{key.name.upper()}"
        
        # F3 combos
        for key, value in self.f3_combos.items():
            if value == char:
                return f"F3+{key.name.upper()}"
        
        # Double combos
        for (mode, key), value in self.double_combos.items():
            if value == char:
                return f"{mode.upper()}+{key.name.upper()}"
        
        return "?"
    
    def show_help(self):
        """Show complete gesture reference"""
        print("\n=== COMPLETE GESTURE MAPPING ===")
        print("\nSINGLE GESTURES (Most Common):")
        print("RIGHT → e    LEFT → t    UP → a    DOWN → o    ENTER → i")
        
        print("\nSPECIAL FUNCTIONS:")
        print("F2 alone → SPACE    F3 alone → BACKSPACE")
        
        print("\nF2 COMBINATIONS:")
        print("F2+RIGHT → n    F2+LEFT → s    F2+UP → h    F2+DOWN → r    F2+ENTER → d")
        
        print("\nF3 COMBINATIONS:")
        print("F3+RIGHT → l    F3+LEFT → c    F3+UP → u    F3+DOWN → m    F3+ENTER → w")
        
        print("\nREMAINING LETTERS:")
        print("F2→F3+RIGHT → f    F2→F3+LEFT → g    F2→F3+UP → y    F2→F3+DOWN → p    F2→F3+ENTER → b")
        print("F3→F2+RIGHT → v    F3→F2+LEFT → k    F3→F2+UP → j    F3→F2+DOWN → x    F3→F2+ENTER → q")
        
        print("\nCONTROLS:")
        print("F1 = training word    ESC = exit")
    
    def run(self):
        """Start the system"""
        print("🎯 MUDRA COMPLETE SYSTEM")
        print("All 26 letters + numbers + symbols!")
        print("\n=== SETUP ===")
        print("1. Switch Mudra to keyboard mode (double-press button)")
        print("2. Assign: Twist → F2, Double-twist → F3")
        
        self.show_help()
        print("\nPress F1 for training, or start typing!")
        print("Press Ctrl+C to exit")
        
        with KeyboardListener(on_press=self.on_key_press) as listener:
            try:
                listener.join()
            except KeyboardInterrupt:
                print("\nMudra system stopped")

if __name__ == "__main__":
    system = MudraCompleteSystem()
    system.run()