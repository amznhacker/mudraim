#!/usr/bin/env python3
"""
Mudra Typing with Visual Feedback - Small GUI showing gesture state
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

class MudraTypingGUI:
    def __init__(self):
        self.kb = keyboard.Controller()
        
        # Simple mappings
        self.single_gestures = {
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
        self.current_state = "Ready"
        self.waiting_for = None
        self.combo_start_time = 0
        self.combo_timeout = 1.5  # Longer timeout
        
        # Hardware debouncing for Mudra band spam
        self.last_key = None
        self.last_key_time = 0
        self.debounce_delay = 0.3  # 300ms debounce
        
        self.create_gui()
    
    def create_gui(self):
        """Create small status GUI"""
        self.root = tk.Tk()
        self.root.title("Mudra Status")
        self.root.geometry("300x200+50+50")
        self.root.attributes("-topmost", True)
        self.root.configure(bg='lightblue')
        
        # Status display
        self.status_label = tk.Label(self.root, text="Ready", 
                                   font=('Arial', 14, 'bold'), 
                                   bg='lightblue', fg='black')
        self.status_label.pack(pady=10)
        
        # Current gesture
        self.gesture_label = tk.Label(self.root, text="Waiting for gesture...", 
                                    font=('Arial', 12), 
                                    bg='lightblue', fg='blue')
        self.gesture_label.pack(pady=5)
        
        # Last typed
        self.typed_label = tk.Label(self.root, text="", 
                                  font=('Arial', 16, 'bold'), 
                                  bg='lightblue', fg='green')
        self.typed_label.pack(pady=10)
        
        # Instructions
        instructions = tk.Label(self.root, 
                              text="F2=Twist, F3=Double-twist\nESC=Exit", 
                              font=('Arial', 9), 
                              bg='lightblue')
        instructions.pack(pady=5)
        
        # Progress bar for combo timing
        self.progress_frame = tk.Frame(self.root, bg='lightblue')
        self.progress_frame.pack(pady=5)
        
        self.progress_canvas = tk.Canvas(self.progress_frame, width=200, height=10, bg='white')
        self.progress_canvas.pack()
        
        # Start keyboard listener
        self.keyboard_listener = KeyboardListener(on_press=self.on_key_press)
        self.keyboard_listener.start()
        
        # Start update loop
        self.update_display()
    
    def update_status(self, status, gesture="", typed=""):
        """Update GUI status"""
        self.status_label.config(text=status)
        if gesture:
            self.gesture_label.config(text=gesture)
        if typed:
            self.typed_label.config(text=f"→ {typed}")
            # Clear after 2 seconds
            self.root.after(2000, lambda: self.typed_label.config(text=""))
    
    def update_progress(self):
        """Update combo progress bar"""
        if self.waiting_for:
            elapsed = time.time() - self.combo_start_time
            progress = min(elapsed / self.combo_timeout, 1.0)
            
            self.progress_canvas.delete("all")
            width = int(200 * progress)
            color = 'orange' if progress < 0.8 else 'red'
            self.progress_canvas.create_rectangle(0, 0, width, 10, fill=color, outline="")
        else:
            self.progress_canvas.delete("all")
    
    def update_display(self):
        """Update display loop"""
        current_time = time.time()
        
        # Check for combo timeout
        if self.waiting_for and current_time - self.combo_start_time > self.combo_timeout:
            if self.waiting_for == 'f2':
                self.type_char(' ')
                self.update_status("Ready", "", "SPACE")
            elif self.waiting_for == 'f3':
                self.type_char('BACKSPACE')
                self.update_status("Ready", "", "BACKSPACE")
            
            self.waiting_for = None
        
        self.update_progress()
        self.root.after(50, self.update_display)  # Update every 50ms
    
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
        """Handle key presses"""
        current_time = time.time()
        
        # Hardware debouncing - ignore repeated keys from Mudra band
        if key == self.last_key and current_time - self.last_key_time < self.debounce_delay:
            return  # Ignore spam from hardware
        
        self.last_key = key
        self.last_key_time = current_time
        
        # Handle combinations first
        if self.waiting_for:
            if self.waiting_for == 'f2' and key in self.f2_combos:
                letter = self.f2_combos[key]
                self.type_char(letter)
                self.update_status("Ready", f"F2+{key.name.upper()}", letter.upper())
                self.waiting_for = None
                return
            elif self.waiting_for == 'f3' and key in self.f3_combos:
                letter = self.f3_combos[key]
                self.type_char(letter)
                self.update_status("Ready", f"F3+{key.name.upper()}", letter.upper())
                self.waiting_for = None
                return
        
        # Handle new keys
        if key in self.single_gestures:
            letter = self.single_gestures[key]
            self.type_char(letter)
            self.update_status("Ready", key.name.upper(), letter.upper())
        
        elif key == Key.f2:
            self.waiting_for = 'f2'
            self.combo_start_time = current_time
            self.update_status("Waiting for combo...", "F2 + ?")
        
        elif key == Key.f3:
            self.waiting_for = 'f3'
            self.combo_start_time = current_time
            self.update_status("Waiting for combo...", "F3 + ?")
        
        elif key == Key.esc:
            self.root.quit()
            return False
    
    def run(self):
        """Start the system"""
        print("🎯 MUDRA TYPING WITH VISUAL FEEDBACK")
        print("Small GUI window will show gesture status")
        print("\n=== SETUP ===")
        print("Assign: Twist → F2, Double-twist → F3")
        print("\n=== GESTURES ===")
        print("Single: RIGHT=e, LEFT=t, UP=a, DOWN=o, ENTER=i")
        print("F2+direction: n,s,h,r,d")
        print("F3+direction: l,c,u,m,w")
        print("F2 alone = space, F3 alone = backspace")
        print("\nGUI window opening...")
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nStopped")
        finally:
            self.keyboard_listener.stop()

if __name__ == "__main__":
    system = MudraTypingGUI()
    system.run()