#!/usr/bin/env python3
"""
Mudra Gesture Pad - Dedicated area for gesture typing
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

class GesturePad:
    def __init__(self):
        self.kb = keyboard.Controller()
        self.typing_mode = False
        
        # Gesture mappings
        self.gestures = {
            'right': 'e',        
            'left': 't',         
            'up': 'a',           
            'down': 'o',         
            'up_right': 'i',     
            'down_right': 'n',   
            'up_left': 's',      
            'down_left': 'h',
            'double_right': 'r',
            'double_left': 'd',
            'double_up': 'l',
            'double_down': 'c',
        }
        
        self.start_pos = None
        self.last_gesture = None
        self.last_gesture_time = 0
        self.double_gesture_window = 0.5
        self.min_distance = 20
        
        # Create gesture pad window
        self.create_gesture_pad()
    
    def create_gesture_pad(self):
        """Create small floating gesture pad"""
        self.root = tk.Tk()
        self.root.title("Mudra Gesture Pad")
        self.root.geometry("200x200+100+100")  # 200x200 pixels, positioned at (100,100)
        self.root.attributes("-topmost", True)  # Always on top
        self.root.configure(bg='lightblue')
        
        # Canvas for drawing gestures
        self.canvas = tk.Canvas(self.root, width=180, height=150, bg='white', relief='sunken', bd=2)
        self.canvas.pack(pady=10)
        
        # Status label
        self.status_label = tk.Label(self.root, text="Mouse Mode", bg='lightblue', font=('Arial', 10))
        self.status_label.pack()
        
        # Instructions
        instructions = tk.Label(self.root, text="F1: Toggle | Draw gestures in white area", 
                              bg='lightblue', font=('Arial', 8), wraplength=180)
        instructions.pack()
        
        # Bind mouse events to canvas only
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        
        # Draw grid lines for reference
        self.draw_grid()
        
        # Start keyboard listener
        self.keyboard_listener = KeyboardListener(on_press=self.on_key_press)
        self.keyboard_listener.start()
    
    def draw_grid(self):
        """Draw reference grid"""
        # Light grid lines
        for i in range(0, 180, 30):
            self.canvas.create_line(i, 0, i, 150, fill='lightgray', width=1)
        for i in range(0, 150, 30):
            self.canvas.create_line(0, i, 180, i, fill='lightgray', width=1)
        
        # Center cross
        self.canvas.create_line(90, 0, 90, 150, fill='gray', width=2)
        self.canvas.create_line(0, 75, 180, 75, fill='gray', width=2)
    
    def get_direction(self, start_x, start_y, end_x, end_y):
        """Get gesture direction"""
        dx = end_x - start_x
        dy = end_y - start_y
        
        distance = (dx**2 + dy**2)**0.5
        if distance < self.min_distance:
            return None
        
        abs_dx = abs(dx)
        abs_dy = abs(dy)
        
        # Horizontal
        if abs_dx > abs_dy * 1.5:
            return 'right' if dx > 0 else 'left'
        # Vertical  
        elif abs_dy > abs_dx * 1.5:
            return 'up' if dy < 0 else 'down'
        # Diagonal
        else:
            if dx > 0 and dy < 0:
                return 'up_right'
            elif dx > 0 and dy > 0:
                return 'down_right'
            elif dx < 0 and dy < 0:
                return 'up_left'
            elif dx < 0 and dy > 0:
                return 'down_left'
        
        return None
    
    def process_gesture(self, gesture):
        """Process gesture and type letter"""
        if not self.typing_mode:
            return
            
        current_time = time.time()
        
        # Check for double gesture
        if (self.last_gesture == gesture and 
            current_time - self.last_gesture_time < self.double_gesture_window):
            
            double_gesture = f"double_{gesture}"
            if double_gesture in self.gestures:
                letter = self.gestures[double_gesture]
                self.type_letter(letter)
                self.show_feedback(f"{gesture}+{gesture} → '{letter}'")
                self.last_gesture = None
                return
        
        # Single gesture
        if gesture in self.gestures:
            letter = self.gestures[gesture]
            self.type_letter(letter)
            self.show_feedback(f"{gesture} → '{letter}'")
        
        self.last_gesture = gesture
        self.last_gesture_time = current_time
    
    def type_letter(self, letter):
        """Type letter"""
        self.kb.press(letter)
        self.kb.release(letter)
    
    def show_feedback(self, text):
        """Show gesture feedback"""
        self.status_label.config(text=text)
        self.root.after(2000, lambda: self.status_label.config(text="Typing Mode" if self.typing_mode else "Mouse Mode"))
    
    def on_canvas_click(self, event):
        """Start gesture"""
        if self.typing_mode:
            self.start_pos = (event.x, event.y)
            self.canvas.delete("gesture_line")  # Clear previous line
    
    def on_canvas_drag(self, event):
        """Show gesture line while dragging"""
        if self.typing_mode and self.start_pos:
            self.canvas.delete("gesture_line")
            self.canvas.create_line(self.start_pos[0], self.start_pos[1], 
                                  event.x, event.y, fill='red', width=3, tags="gesture_line")
    
    def on_canvas_release(self, event):
        """Complete gesture"""
        if self.typing_mode and self.start_pos:
            gesture = self.get_direction(self.start_pos[0], self.start_pos[1], event.x, event.y)
            if gesture:
                self.process_gesture(gesture)
            
            # Clear gesture line after short delay
            self.root.after(500, lambda: self.canvas.delete("gesture_line"))
            self.start_pos = None
    
    def on_key_press(self, key):
        """Handle keyboard input"""
        if key == Key.f1:
            self.typing_mode = not self.typing_mode
            mode = "Typing Mode" if self.typing_mode else "Mouse Mode"
            self.status_label.config(text=mode)
            
            # Change canvas color to indicate mode
            color = 'lightyellow' if self.typing_mode else 'white'
            self.canvas.config(bg=color)
            return
        
        if not self.typing_mode:
            return
        
        # Space and backspace
        if key == Key.space:
            self.show_feedback("Space")
        elif key == Key.backspace:
            self.show_feedback("Backspace")
    
    def run(self):
        """Start the gesture pad"""
        print("🎯 MUDRA GESTURE PAD")
        print("Dedicated area for gesture typing!")
        print("\n=== FEATURES ===")
        print("✓ Small floating window - doesn't interfere with mouse")
        print("✓ Draw gestures only in the white area")
        print("✓ Visual feedback with red gesture lines")
        print("✓ Always on top for easy access")
        print("\n=== USAGE ===")
        print("1. F1 → Toggle typing mode (window turns yellow)")
        print("2. Draw gestures in the white area")
        print("3. → e, ← t, ↑ a, ↓ o, etc.")
        print("4. Double gestures: →→ r, ←← d")
        print("\nGesture pad window will open...")
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nGesture pad closed")
        finally:
            self.keyboard_listener.stop()

if __name__ == "__main__":
    pad = GesturePad()
    pad.run()