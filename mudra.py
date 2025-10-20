#!/usr/bin/env python3
"""
Mudra Typing - System-wide gesture typing for Ubuntu
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
        
        self.create_gui()
    
    def create_gui(self):
        """Small status window"""
        self.root = tk.Tk()
        self.root.title("Mudra")
        self.root.geometry("250x120+50+50")
        self.root.attributes("-topmost", True)
        self.root.configure(bg='lightgreen')
        
        # Status
        self.status_label = tk.Label(self.root, text="Ready", 
                                   font=('Arial', 12, 'bold'), 
                                   bg='lightgreen')
        self.status_label.pack(pady=5)
        
        # Last typed
        self.typed_label = tk.Label(self.root, text="", 
                                  font=('Arial', 14, 'bold'), 
                                  bg='lightgreen', fg='blue')
        self.typed_label.pack(pady=5)
        
        # Instructions
        tk.Label(self.root, text="F2=Twist, F3=Double-twist", 
                font=('Arial', 8), bg='lightgreen').pack()
        tk.Label(self.root, text="Works system-wide!", 
                font=('Arial', 8), bg='lightgreen').pack()
        
        # Start keyboard listener
        self.keyboard_listener = KeyboardListener(on_press=self.on_key_press)
        self.keyboard_listener.start()
        
        # Update loop
        self.update_display()
    
    def update_display(self):
        """Check for timeouts"""
        if self.waiting_for and time.time() - self.combo_start_time > self.combo_timeout:
            if self.waiting_for == 'f2':
                self.type_char(' ')
                self.show_typed("SPACE")
            elif self.waiting_for == 'f3':
                self.type_char('BACKSPACE')
                self.show_typed("⌫")
            
            self.waiting_for = None
            self.status_label.config(text="Ready")
        
        self.root.after(100, self.update_display)
    
    def show_typed(self, text):
        """Show what was typed"""
        self.typed_label.config(text=f"→ {text}")
        self.root.after(1500, lambda: self.typed_label.config(text=""))
    
    def type_char(self, char):
        """Type character system-wide"""
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
        """Handle key presses"""
        current_time = time.time()
        
        # Debounce hardware spam
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
                self.status_label.config(text="Ready")
                return
            elif self.waiting_for == 'f3' and key in self.f3_combos:
                letter = self.f3_combos[key]
                self.type_char(letter)
                self.show_typed(letter.upper())
                self.waiting_for = None
                self.status_label.config(text="Ready")
                return
        
        # Handle new keys
        if key in self.gestures:
            letter = self.gestures[key]
            self.type_char(letter)
            self.show_typed(letter.upper())
        
        elif key == Key.f2:
            self.waiting_for = 'f2'
            self.combo_start_time = current_time
            self.status_label.config(text="F2+?")
        
        elif key == Key.f3:
            self.waiting_for = 'f3'
            self.combo_start_time = current_time
            self.status_label.config(text="F3+?")
        
        elif key == Key.esc:
            self.root.quit()
            return False
    
    def run(self):
        """Start system"""
        print("🎯 MUDRA TYPING - SYSTEM-WIDE")
        print("Works in browser, terminal, any app!")
        print("\n=== SETUP ===")
        print("Mudra keyboard mode: Twist→F2, Double-twist→F3")
        print("\n=== GESTURES ===")
        print("RIGHT→e  LEFT→t  UP→a  DOWN→o  ENTER→i")
        print("F2+direction: n,s,h,r,d")
        print("F3+direction: l,c,u,m,w")
        print("F2 alone→space, F3 alone→backspace")
        print("\nSmall window shows status. ESC to exit.")
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nStopped")
        finally:
            self.keyboard_listener.stop()

if __name__ == "__main__":
    system = MudraTyping()
    system.run()