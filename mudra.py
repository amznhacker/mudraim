#!/usr/bin/env python3
"""
Mudra Typing - Simple UI that works
"""

import subprocess
import sys
import time
import tkinter as tk
from pynput import keyboard
from pynput.keyboard import Key, Listener as KeyboardListener

# Install pynput if needed
try:
    import pynput
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pynput"])

class MudraTyping:
    def __init__(self):
        self.kb = keyboard.Controller()
        
        # Gesture mappings
        self.gestures = {
            Key.right: 'e',
            Key.left: 't', 
            Key.up: 'a',
            Key.down: 'o',
            Key.enter: 'i',
        }
        
        self.f2_combos = {
            Key.right: 'n',
            Key.left: 's',
            Key.up: 'h', 
            Key.down: 'r',
            Key.enter: 'd',
        }
        
        self.f3_combos = {
            Key.right: 'l',
            Key.left: 'c',
            Key.up: 'u',
            Key.down: 'm',
            Key.enter: 'w',
        }
        
        # State
        self.waiting_for = None
        self.combo_start_time = 0
        self.combo_timeout = 1.2
        
        # Hardware debouncing
        self.last_key = None
        self.last_key_time = 0
        self.debounce_delay = 0.25
        
        # Stats
        self.chars_typed = 0
        
        self.create_ui()
    
    def create_ui(self):
        """Create minimal UI"""
        self.root = tk.Tk()
        self.root.title("Mudra")
        self.root.geometry("200x150")
        self.root.configure(bg='lightblue')
        self.root.attributes("-topmost", True)
        
        # Status
        tk.Label(self.root, text="Mudra Typing", font=('Arial', 12, 'bold'), 
                bg='lightblue').pack(pady=5)
        
        self.status_label = tk.Label(self.root, text="Ready", 
                                   font=('Arial', 10, 'bold'), 
                                   bg='lightblue', fg='green')
        self.status_label.pack(pady=5)
        
        # Last typed
        self.typed_label = tk.Label(self.root, text="", 
                                  font=('Arial', 14, 'bold'), 
                                  bg='lightblue', fg='blue')
        self.typed_label.pack(pady=5)
        
        # Stats
        self.stats_label = tk.Label(self.root, text="Chars: 0", 
                                  font=('Arial', 9), 
                                  bg='lightblue')
        self.stats_label.pack(pady=2)
        
        # Controls
        button_frame = tk.Frame(self.root, bg='lightblue')
        button_frame.pack(pady=5)
        
        tk.Button(button_frame, text="Reset", command=self.reset_stats,
                 font=('Arial', 8)).pack(side=tk.LEFT, padx=2)
        
        tk.Button(button_frame, text="Exit", command=self.exit_app,
                 font=('Arial', 8)).pack(side=tk.LEFT, padx=2)
        
        # Start keyboard listener
        self.keyboard_listener = KeyboardListener(on_press=self.on_key_press)
        self.keyboard_listener.start()
        
        # Update loop
        self.update_display()
    
    def reset_stats(self):
        """Reset stats"""
        self.chars_typed = 0
    
    def exit_app(self):
        """Exit"""
        self.keyboard_listener.stop()
        self.root.quit()
    
    def update_display(self):
        """Update display"""
        # Handle timeouts
        if self.waiting_for and time.time() - self.combo_start_time > self.combo_timeout:
            if self.waiting_for == 'f2':
                self.type_char(' ')
                self.show_typed("SPACE")
            elif self.waiting_for == 'f3':
                self.type_char('BACKSPACE')
                self.show_typed("⌫")
            
            self.waiting_for = None
            self.status_label.config(text="Ready", fg='green')
        
        # Update stats
        self.stats_label.config(text=f"Chars: {self.chars_typed}")
        
        self.root.after(100, self.update_display)
    
    def show_typed(self, text):
        """Show typed character"""
        self.typed_label.config(text=text)
        self.chars_typed += 1
        self.root.after(1500, lambda: self.typed_label.config(text=""))
    
    def type_char(self, char):
        """Type character"""
        if char == 'BACKSPACE':
            self.kb.press(Key.backspace)
            self.kb.release(Key.backspace)
        elif char == ' ':
            self.kb.press(Key.space)
            self.kb.release(Key.space)
        else:
            self.kb.press(char)
            self.kb.release(char)
    
    def on_key_press(self, key):
        """Handle keys"""
        current_time = time.time()
        
        # Debounce
        if key == self.last_key and current_time - self.last_key_time < self.debounce_delay:
            return
        
        self.last_key = key
        self.last_key_time = current_time
        
        # Handle combinations
        if self.waiting_for:
            if self.waiting_for == 'f2' and key in self.f2_combos:
                letter = self.f2_combos[key]
                self.type_char(letter)
                self.show_typed(letter.upper())
                self.waiting_for = None
                self.status_label.config(text="Ready", fg='green')
                return
            elif self.waiting_for == 'f3' and key in self.f3_combos:
                letter = self.f3_combos[key]
                self.type_char(letter)
                self.show_typed(letter.upper())
                self.waiting_for = None
                self.status_label.config(text="Ready", fg='green')
                return
        
        # Handle new keys
        if key in self.gestures:
            letter = self.gestures[key]
            self.type_char(letter)
            self.show_typed(letter.upper())
        
        elif key == Key.f2:
            self.waiting_for = 'f2'
            self.combo_start_time = current_time
            self.status_label.config(text="F2+?", fg='orange')
        
        elif key == Key.f3:
            self.waiting_for = 'f3'
            self.combo_start_time = current_time
            self.status_label.config(text="F3+?", fg='orange')
        
        elif key == Key.esc:
            self.exit_app()
    
    def run(self):
        """Start app"""
        print("🎯 MUDRA TYPING")
        print("Simple UI - no X11 errors!")
        print("\nSetup: Twist→F2, Double-twist→F3")
        print("Gestures: RIGHT→e, LEFT→t, UP→a, DOWN→o, ENTER→i")
        print("F2+direction: n,s,h,r,d")
        print("F3+direction: l,c,u,m,w")
        
        try:
            self.root.mainloop()
        except Exception as e:
            print(f"Error: {e}")
        finally:
            if hasattr(self, 'keyboard_listener'):
                self.keyboard_listener.stop()

if __name__ == "__main__":
    app = MudraTyping()
    app.run()