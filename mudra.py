#!/usr/bin/env python3
"""
Mudra Typing - System-wide gesture typing with nice UI
"""

import subprocess
import sys
import time
import tkinter as tk
from tkinter import ttk
from pynput import keyboard
from pynput.keyboard import Key, Listener as KeyboardListener

# Install pynput if needed
try:
    import pynput
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pynput"])

class MudraTypingUI:
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
        self.session_start = time.time()
        
        self.create_ui()
    
    def create_ui(self):
        """Create nice UI"""
        self.root = tk.Tk()
        self.root.title("🎯 Mudra Typing")
        self.root.geometry("400x500+100+100")
        self.root.configure(bg='#2c3e50')
        self.root.attributes("-topmost", True)
        
        # Main container
        main_frame = tk.Frame(self.root, bg='#2c3e50', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = tk.Label(main_frame, text="🎯 Mudra Typing", 
                        font=('Arial', 18, 'bold'), 
                        fg='#ecf0f1', bg='#2c3e50')
        title.pack(pady=(0, 20))
        
        # Status section
        status_frame = tk.Frame(main_frame, bg='#34495e', relief=tk.RAISED, bd=2)
        status_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(status_frame, text="Status", font=('Arial', 12, 'bold'), 
                fg='#ecf0f1', bg='#34495e').pack(pady=5)
        
        self.status_label = tk.Label(status_frame, text="Ready", 
                                   font=('Arial', 14, 'bold'), 
                                   fg='#2ecc71', bg='#34495e')
        self.status_label.pack(pady=5)
        
        # Last typed section
        typed_frame = tk.Frame(main_frame, bg='#34495e', relief=tk.RAISED, bd=2)
        typed_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(typed_frame, text="Last Typed", font=('Arial', 12, 'bold'), 
                fg='#ecf0f1', bg='#34495e').pack(pady=5)
        
        self.typed_label = tk.Label(typed_frame, text="", 
                                  font=('Arial', 20, 'bold'), 
                                  fg='#3498db', bg='#34495e', height=2)
        self.typed_label.pack(pady=5)
        
        # Stats section
        stats_frame = tk.Frame(main_frame, bg='#34495e', relief=tk.RAISED, bd=2)
        stats_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(stats_frame, text="Session Stats", font=('Arial', 12, 'bold'), 
                fg='#ecf0f1', bg='#34495e').pack(pady=5)
        
        self.stats_label = tk.Label(stats_frame, text="Characters: 0", 
                                  font=('Arial', 10), 
                                  fg='#ecf0f1', bg='#34495e')
        self.stats_label.pack(pady=2)
        
        # Gesture reference (collapsible)
        self.ref_visible = tk.BooleanVar(value=False)
        
        ref_toggle = tk.Button(main_frame, text="▼ Show Gestures", 
                              command=self.toggle_reference,
                              font=('Arial', 10), bg='#3498db', fg='white',
                              relief=tk.FLAT, cursor='hand2')
        ref_toggle.pack(pady=(0, 10))
        
        # Reference frame (initially hidden)
        self.ref_frame = tk.Frame(main_frame, bg='#34495e', relief=tk.RAISED, bd=2)
        
        ref_text = """Single Gestures:
RIGHT → e    LEFT → t    UP → a    DOWN → o    ENTER → i

F2 Combinations (Twist):
F2+RIGHT → n    F2+LEFT → s    F2+UP → h
F2+DOWN → r    F2+ENTER → d    F2 alone → SPACE

F3 Combinations (Double-twist):
F3+RIGHT → l    F3+LEFT → c    F3+UP → u
F3+DOWN → m    F3+ENTER → w    F3 alone → BACKSPACE"""
        
        tk.Label(self.ref_frame, text=ref_text, 
                font=('Courier', 9), fg='#ecf0f1', bg='#34495e',
                justify=tk.LEFT).pack(pady=10, padx=10)
        
        # Control buttons
        button_frame = tk.Frame(main_frame, bg='#2c3e50')
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Button(button_frame, text="Reset Stats", command=self.reset_stats,
                 font=('Arial', 10), bg='#e74c3c', fg='white',
                 relief=tk.FLAT, cursor='hand2').pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(button_frame, text="Exit", command=self.exit_app,
                 font=('Arial', 10), bg='#95a5a6', fg='white',
                 relief=tk.FLAT, cursor='hand2').pack(side=tk.RIGHT)
        
        # Start keyboard listener
        self.keyboard_listener = KeyboardListener(on_press=self.on_key_press)
        self.keyboard_listener.start()
        
        # Update loop
        self.update_display()
    
    def toggle_reference(self):
        """Toggle gesture reference visibility"""
        if self.ref_visible.get():
            self.ref_frame.pack_forget()
            self.ref_visible.set(False)
            # Find the toggle button and update text
            for widget in self.root.winfo_children():
                for child in widget.winfo_children():
                    if isinstance(child, tk.Button) and "Show Gestures" in child.cget("text"):
                        child.config(text="▼ Show Gestures")
        else:
            self.ref_frame.pack(fill=tk.X, pady=(0, 15))
            self.ref_visible.set(True)
            # Find the toggle button and update text
            for widget in self.root.winfo_children():
                for child in widget.winfo_children():
                    if isinstance(child, tk.Button) and "Show Gestures" in child.cget("text"):
                        child.config(text="▲ Hide Gestures")
    
    def reset_stats(self):
        """Reset session statistics"""
        self.chars_typed = 0
        self.session_start = time.time()
        self.update_stats()
    
    def exit_app(self):
        """Exit application"""
        self.keyboard_listener.stop()
        self.root.quit()
    
    def update_stats(self):
        """Update statistics display"""
        session_time = int(time.time() - self.session_start)
        minutes = session_time // 60
        seconds = session_time % 60
        
        stats_text = f"Characters: {self.chars_typed}\nTime: {minutes}m {seconds}s"
        self.stats_label.config(text=stats_text)
    
    def update_display(self):
        """Update display and handle timeouts"""
        # Handle combo timeouts
        if self.waiting_for and time.time() - self.combo_start_time > self.combo_timeout:
            if self.waiting_for == 'f2':
                self.type_char(' ')
                self.show_typed("SPACE")
            elif self.waiting_for == 'f3':
                self.type_char('BACKSPACE')
                self.show_typed("⌫")
            
            self.waiting_for = None
            self.status_label.config(text="Ready", fg='#2ecc71')
        
        # Update stats
        self.update_stats()
        
        # Schedule next update
        self.root.after(100, self.update_display)
    
    def show_typed(self, text):
        """Show what was typed"""
        self.typed_label.config(text=text)
        self.chars_typed += 1
        # Clear after 2 seconds
        self.root.after(2000, lambda: self.typed_label.config(text=""))
    
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
                self.status_label.config(text="Ready", fg='#2ecc71')
                return
            elif self.waiting_for == 'f3' and key in self.f3_combos:
                letter = self.f3_combos[key]
                self.type_char(letter)
                self.show_typed(letter.upper())
                self.waiting_for = None
                self.status_label.config(text="Ready", fg='#2ecc71')
                return
        
        # Handle new keys
        if key in self.gestures:
            letter = self.gestures[key]
            self.type_char(letter)
            self.show_typed(letter.upper())
        
        elif key == Key.f2:
            self.waiting_for = 'f2'
            self.combo_start_time = current_time
            self.status_label.config(text="F2 + ?", fg='#f39c12')
        
        elif key == Key.f3:
            self.waiting_for = 'f3'
            self.combo_start_time = current_time
            self.status_label.config(text="F3 + ?", fg='#f39c12')
        
        elif key == Key.esc:
            self.exit_app()
            return False
    
    def run(self):
        """Start the application"""
        print("🎯 MUDRA TYPING - NICE UI")
        print("System-wide gesture typing with beautiful interface!")
        print("\n=== SETUP ===")
        print("Mudra keyboard mode: Twist→F2, Double-twist→F3")
        print("\nUI window will open with all controls and reference...")
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nStopped")
        finally:
            if hasattr(self, 'keyboard_listener'):
                self.keyboard_listener.stop()

if __name__ == "__main__":
    app = MudraTypingUI()
    app.run()