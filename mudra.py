#!/usr/bin/env python3
"""
Mudra Complete Keyboard - All 26 letters, numbers, symbols + Training GUI
"""

import subprocess
import sys
import time
import tkinter as tk
from tkinter import ttk
import random
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
        
        # Complete gesture mapping
        self.gestures = {
            # Single gestures (5 most common letters)
            Key.right: 'e',
            Key.left: 't', 
            Key.up: 'a',
            Key.down: 'o',
            Key.enter: 'i',
            
            # F2 combinations (twist + direction)
            ('f2', Key.right): 'n',
            ('f2', Key.left): 's',
            ('f2', Key.up): 'h', 
            ('f2', Key.down): 'r',
            ('f2', Key.enter): 'd',
            
            # F3 combinations (double twist + direction)
            ('f3', Key.right): 'l',
            ('f3', Key.left): 'c',
            ('f3', Key.up): 'u',
            ('f3', Key.down): 'm',
            ('f3', Key.enter): 'w',
            
            # Double combinations (remaining letters)
            ('f2', 'f3', Key.right): 'f',
            ('f2', 'f3', Key.left): 'g',
            ('f2', 'f3', Key.up): 'y',
            ('f2', 'f3', Key.down): 'p',
            ('f2', 'f3', Key.enter): 'b',
            ('f3', 'f2', Key.right): 'v',
            ('f3', 'f2', Key.left): 'k',
            ('f3', 'f2', Key.up): 'j',
            ('f3', 'f2', Key.down): 'x',
            ('f3', 'f2', Key.enter): 'q',
            ('f2', Key.right, Key.left): 'z',
            
            # Numbers (F2 then F3 + direction)
            ('f2', 'f3'): 'NUMBER_MODE',
            ('number', Key.right): '1',
            ('number', Key.left): '2',
            ('number', Key.up): '3',
            ('number', Key.down): '4',
            ('number', Key.enter): '5',
            ('number', Key.right, Key.up): '6',
            ('number', Key.right, Key.down): '7',
            ('number', Key.left, Key.up): '8',
            ('number', Key.left, Key.down): '9',
            ('number', Key.up, Key.down): '0',
            
            # Symbols (F3 then F2 + direction)
            ('f3', 'f2'): 'SYMBOL_MODE',
            ('symbol', Key.right): '.',
            ('symbol', Key.left): ',',
            ('symbol', Key.up): '!',
            ('symbol', Key.down): '?',
            ('symbol', Key.enter): ';',
        }
        
        # Special functions
        self.special_functions = {
            Key.f2: ' ',  # Space
            Key.f3: 'BACKSPACE',
        }
        
        # Gesture sequence tracking
        self.current_sequence = []
        self.sequence_start_time = 0
        self.sequence_timeout = 1.0
        self.mode = 'normal'  # normal, number, symbol
        
        # Training data
        self.training_words = [
            'the', 'and', 'you', 'that', 'was', 'for', 'are', 'with', 'his', 'they',
            'at', 'be', 'this', 'have', 'from', 'or', 'one', 'had', 'by', 'word'
        ]
        
        self.create_gui()
    
    def create_gui(self):
        """Create training GUI"""
        self.root = tk.Tk()
        self.root.title("Mudra Complete Training")
        self.root.geometry("800x600")
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title = ttk.Label(main_frame, text="🎯 Mudra Complete Training", font=('Arial', 16, 'bold'))
        title.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Training section
        training_frame = ttk.LabelFrame(main_frame, text="Training", padding="10")
        training_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Current word to practice
        self.word_label = ttk.Label(training_frame, text="Practice word:", font=('Arial', 12))
        self.word_label.grid(row=0, column=0, sticky=tk.W)
        
        self.current_word = tk.StringVar(value="the")
        self.word_display = ttk.Label(training_frame, textvariable=self.current_word, 
                                     font=('Arial', 20, 'bold'), foreground='blue')
        self.word_display.grid(row=1, column=0, pady=10)
        
        # Progress
        self.progress_label = ttk.Label(training_frame, text="Progress: 0/3", font=('Arial', 10))
        self.progress_label.grid(row=2, column=0, sticky=tk.W)
        
        # Typed text
        self.typed_text = tk.StringVar()
        self.typed_display = ttk.Label(training_frame, textvariable=self.typed_text,
                                      font=('Arial', 16), foreground='green')
        self.typed_display.grid(row=3, column=0, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(training_frame)
        button_frame.grid(row=4, column=0, pady=10)
        
        ttk.Button(button_frame, text="New Word", command=self.new_word).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_typed).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Show Gestures", command=self.show_gestures).pack(side=tk.LEFT, padx=5)
        
        # Gesture reference
        ref_frame = ttk.LabelFrame(main_frame, text="Gesture Reference", padding="10")
        ref_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Create scrollable text for gestures
        self.gesture_text = tk.Text(ref_frame, height=15, width=80, font=('Courier', 9))
        scrollbar = ttk.Scrollbar(ref_frame, orient=tk.VERTICAL, command=self.gesture_text.yview)
        self.gesture_text.configure(yscrollcommand=scrollbar.set)
        
        self.gesture_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.populate_gesture_reference()
        
        # Status
        self.status_label = ttk.Label(main_frame, text="Ready to train! Use your Mudra gestures.", 
                                     font=('Arial', 10))
        self.status_label.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Start keyboard listener
        self.keyboard_listener = KeyboardListener(on_press=self.on_key_press)
        self.keyboard_listener.start()
        
        self.new_word()
    
    def populate_gesture_reference(self):
        """Fill gesture reference"""
        ref_text = """COMPLETE GESTURE MAPPING

SINGLE GESTURES (Most Common):
RIGHT → e    LEFT → t    UP → a    DOWN → o    ENTER → i

SPECIAL FUNCTIONS:
F2 alone → SPACE    F3 alone → BACKSPACE

TWIST COMBINATIONS (F2 + direction):
F2+RIGHT → n    F2+LEFT → s    F2+UP → h    F2+DOWN → r    F2+ENTER → d

DOUBLE TWIST COMBINATIONS (F3 + direction):
F3+RIGHT → l    F3+LEFT → c    F3+UP → u    F3+DOWN → m    F3+ENTER → w

REMAINING LETTERS (F2+F3 combinations):
F2→F3+RIGHT → f    F2→F3+LEFT → g    F2→F3+UP → y    F2→F3+DOWN → p    F2→F3+ENTER → b
F3→F2+RIGHT → v    F3→F2+LEFT → k    F3→F2+UP → j    F3→F2+DOWN → x    F3→F2+ENTER → q
F2+RIGHT+LEFT → z

NUMBERS (F2→F3 then direction):
F2→F3 = Number Mode, then:
RIGHT → 1    LEFT → 2    UP → 3    DOWN → 4    ENTER → 5
RIGHT+UP → 6    RIGHT+DOWN → 7    LEFT+UP → 8    LEFT+DOWN → 9    UP+DOWN → 0

SYMBOLS (F3→F2 then direction):
F3→F2 = Symbol Mode, then:
RIGHT → .    LEFT → ,    UP → !    DOWN → ?    ENTER → ;

EXAMPLES:
"the" = t+h+e = LEFT + (F2+UP) + RIGHT
"and" = a+n+d = UP + (F2+RIGHT) + (F2+ENTER)
"""
        self.gesture_text.insert(tk.END, ref_text)
        self.gesture_text.config(state=tk.DISABLED)
    
    def new_word(self):
        """Get new training word"""
        word = random.choice(self.training_words)
        self.current_word.set(word)
        self.clear_typed()
        self.show_word_gestures(word)
    
    def clear_typed(self):
        """Clear typed text"""
        self.typed_text.set("")
    
    def show_gestures(self):
        """Show gestures for current word"""
        word = self.current_word.get()
        self.show_word_gestures(word)
    
    def show_word_gestures(self, word):
        """Show how to type a word"""
        gestures = []
        for char in word.lower():
            gesture = self.get_gesture_for_char(char)
            if gesture:
                gestures.append(f"'{char}' = {gesture}")
        
        gesture_str = " → ".join(gestures)
        self.status_label.config(text=f"Gestures: {gesture_str}")
    
    def get_gesture_for_char(self, char):
        """Get gesture sequence for character"""
        # Reverse lookup in gestures dict
        for key, value in self.gestures.items():
            if value == char:
                if isinstance(key, tuple):
                    return "+".join(str(k).replace('Key.', '') for k in key)
                else:
                    return str(key).replace('Key.', '')
        return "?"
    
    def process_gesture_sequence(self, sequence):
        """Process completed gesture sequence"""
        # Convert sequence to tuple for lookup
        seq_tuple = tuple(sequence)
        
        if seq_tuple in self.gestures:
            result = self.gestures[seq_tuple]
            
            if result == 'NUMBER_MODE':
                self.mode = 'number'
                self.status_label.config(text="Number mode active - use directions for numbers")
                return
            elif result == 'SYMBOL_MODE':
                self.mode = 'symbol'
                self.status_label.config(text="Symbol mode active - use directions for symbols")
                return
            else:
                self.type_character(result)
                self.mode = 'normal'
        else:
            self.status_label.config(text=f"Unknown gesture: {sequence}")
    
    def type_character(self, char):
        """Type character and update display"""
        if char == 'BACKSPACE':
            current = self.typed_text.get()
            if current:
                self.typed_text.set(current[:-1])
        else:
            current = self.typed_text.get()
            self.typed_text.set(current + char)
        
        # Check if word is complete
        if self.typed_text.get().lower() == self.current_word.get().lower():
            self.status_label.config(text="✓ Word complete! Great job!")
            self.root.after(2000, self.new_word)
    
    def on_key_press(self, key):
        """Handle key presses"""
        current_time = time.time()
        
        # Reset sequence if timeout
        if current_time - self.sequence_start_time > self.sequence_timeout:
            self.current_sequence = []
        
        # Handle special functions first
        if key in self.special_functions:
            if len(self.current_sequence) == 0:  # Only if not part of sequence
                func = self.special_functions[key]
                if func == ' ':
                    self.type_character(' ')
                elif func == 'BACKSPACE':
                    self.type_character('BACKSPACE')
                return
        
        # Add to sequence
        self.current_sequence.append(key)
        self.sequence_start_time = current_time
        
        # Check for matches
        # First check single gestures
        if len(self.current_sequence) == 1 and key in self.gestures:
            # Wait a bit to see if it's part of a combo
            self.root.after(200, lambda: self.check_single_gesture(key, current_time))
        
        # Check combinations
        seq_tuple = tuple(self.current_sequence)
        if seq_tuple in self.gestures:
            self.process_gesture_sequence(self.current_sequence)
            self.current_sequence = []
    
    def check_single_gesture(self, key, press_time):
        """Check if single gesture should be processed"""
        if (len(self.current_sequence) == 1 and 
            self.current_sequence[0] == key and
            time.time() - press_time > 0.2):
            
            if key in self.gestures:
                self.type_character(self.gestures[key])
                self.current_sequence = []
    
    def run(self):
        """Start the training system"""
        print("🎯 MUDRA COMPLETE TRAINING")
        print("Training GUI will open...")
        print("Assign in Mudra keyboard mode:")
        print("• Twist → F2")
        print("• Double-twist → F3")
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nTraining stopped")
        finally:
            self.keyboard_listener.stop()

if __name__ == "__main__":
    system = MudraCompleteSystem()
    system.run()