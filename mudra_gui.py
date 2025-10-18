#!/usr/bin/env python3
"""
Mudra GUI - Visual interface for testing and debugging
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
from mudra import SimpleMudra

class MudraGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎯 Mudra Control System")
        self.root.geometry("800x600")
        
        self.mudra = SimpleMudra()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the GUI interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status section
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.mode_label = ttk.Label(status_frame, text="Mode: MOUSE", font=("Arial", 14, "bold"))
        self.mode_label.grid(row=0, column=0, sticky=tk.W)
        
        self.layer_label = ttk.Label(status_frame, text="Layer: Letters", font=("Arial", 12))
        self.layer_label.grid(row=0, column=1, sticky=tk.E)
        
        # Character layout
        layout_frame = ttk.LabelFrame(main_frame, text="Character Layout", padding="10")
        layout_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        self.create_character_grid(layout_frame)
        
        # Control panel
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        self.create_controls(control_frame)
        
        # Log section
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="10")
        log_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        self.log("🎯 Mudra GUI started")
        self.update_status()
    
    def create_character_grid(self, parent):
        """Create visual character grid"""
        self.char_buttons = []
        
        # Create 3x3 grid of character buttons
        for i in range(9):
            row = i // 3
            col = i % 3
            
            btn = tk.Button(parent, text="", width=8, height=3, 
                          command=lambda pos=i: self.tap_position(pos),
                          font=("Arial", 16, "bold"))
            btn.grid(row=row, column=col, padx=2, pady=2)
            self.char_buttons.append(btn)
        
        self.update_character_grid()
    
    def create_controls(self, parent):
        """Create control buttons"""
        # Mode controls
        ttk.Button(parent, text="Toggle Mode", command=self.toggle_mode).grid(row=0, column=0, pady=2, sticky=(tk.W, tk.E))
        ttk.Button(parent, text="Switch Layer", command=self.switch_layer).grid(row=1, column=0, pady=2, sticky=(tk.W, tk.E))
        
        ttk.Separator(parent, orient='horizontal').grid(row=2, column=0, sticky=(tk.W, tk.E), pady=10)
        
        # Mouse controls
        ttk.Label(parent, text="Mouse Controls:").grid(row=3, column=0, sticky=tk.W)
        ttk.Button(parent, text="Left Click", command=self.left_click).grid(row=4, column=0, pady=2, sticky=(tk.W, tk.E))
        ttk.Button(parent, text="Right Click", command=self.right_click).grid(row=5, column=0, pady=2, sticky=(tk.W, tk.E))
        
        # Mouse position
        pos_frame = ttk.Frame(parent)
        pos_frame.grid(row=6, column=0, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(pos_frame, text="X:").grid(row=0, column=0)
        self.x_entry = ttk.Entry(pos_frame, width=6)
        self.x_entry.grid(row=0, column=1, padx=2)
        self.x_entry.insert(0, "500")
        
        ttk.Label(pos_frame, text="Y:").grid(row=0, column=2)
        self.y_entry = ttk.Entry(pos_frame, width=6)
        self.y_entry.grid(row=0, column=3, padx=2)
        self.y_entry.insert(0, "300")
        
        ttk.Button(pos_frame, text="Move", command=self.move_mouse).grid(row=0, column=4, padx=5)
        
        ttk.Separator(parent, orient='horizontal').grid(row=7, column=0, sticky=(tk.W, tk.E), pady=10)
        
        # Keyboard controls
        ttk.Label(parent, text="Keyboard Controls:").grid(row=8, column=0, sticky=tk.W)
        ttk.Button(parent, text="Backspace", command=self.backspace).grid(row=9, column=0, pady=2, sticky=(tk.W, tk.E))
        ttk.Button(parent, text="Enter", command=self.enter_key).grid(row=10, column=0, pady=2, sticky=(tk.W, tk.E))
        
        # Configure column weight
        parent.columnconfigure(0, weight=1)
    
    def update_character_grid(self):
        """Update character grid based on current layer"""
        chars = self.mudra.chars[self.mudra.layer]
        
        for i, btn in enumerate(self.char_buttons):
            if i < len(chars):
                char = chars[i]
                btn.config(text=f"{i}\n{char}", state='normal')
                
                # Color coding
                if self.mudra.typing_mode:
                    btn.config(bg='lightgreen')
                else:
                    btn.config(bg='lightgray')
            else:
                btn.config(text="", state='disabled', bg='white')
    
    def update_status(self):
        """Update status display"""
        mode = "TYPING" if self.mudra.typing_mode else "MOUSE"
        self.mode_label.config(text=f"Mode: {mode}")
        
        layers = ['Letters', 'Numbers', 'Symbols']
        self.layer_label.config(text=f"Layer: {layers[self.mudra.layer]}")
        
        self.update_character_grid()
        
        # Schedule next update
        self.root.after(100, self.update_status)
    
    def log(self, message):
        """Add message to log"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
    
    def tap_position(self, pos):
        """Handle character tap"""
        if self.mudra.typing_mode and pos < len(self.mudra.chars[self.mudra.layer]):
            char = self.mudra.chars[self.mudra.layer][pos]
            self.mudra.handle_input(f"tap {pos}")
            self.log(f"Typed: {char} (position {pos})")
        else:
            self.mudra.handle_input("tap")
            self.log("Mouse click")
    
    def toggle_mode(self):
        """Toggle between mouse and typing mode"""
        if self.mudra.typing_mode:
            self.mudra.handle_input("mouse")
            self.log("Switched to MOUSE mode")
        else:
            self.mudra.handle_input("twist")
            self.log("Switched to TYPING mode")
    
    def switch_layer(self):
        """Switch typing layer"""
        if self.mudra.typing_mode:
            self.mudra.handle_input("twist")
            layers = ['Letters', 'Numbers', 'Symbols']
            self.log(f"Switched to {layers[self.mudra.layer]} layer")
    
    def left_click(self):
        """Perform left click"""
        self.mudra.handle_input("tap")
        self.log("Left click")
    
    def right_click(self):
        """Perform right click"""
        self.mudra.handle_input("rtap")
        self.log("Right click")
    
    def move_mouse(self):
        """Move mouse to specified position"""
        try:
            x = int(self.x_entry.get())
            y = int(self.y_entry.get())
            self.mudra.handle_input(f"move {x} {y}")
            self.log(f"Moved mouse to ({x}, {y})")
        except ValueError:
            self.log("Invalid coordinates")
    
    def backspace(self):
        """Perform backspace"""
        self.mudra.handle_input("rtap")
        self.log("Backspace")
    
    def enter_key(self):
        """Perform enter"""
        self.mudra.handle_input("dtwist")
        self.log("Enter key")
    
    def run(self):
        """Start the GUI"""
        self.root.mainloop()

def main():
    """Launch GUI"""
    try:
        gui = MudraGUI()
        gui.run()
    except Exception as e:
        print(f"GUI Error: {e}")
        print("Make sure tkinter is installed")
        print("On Ubuntu: sudo apt-get install python3-tk")

if __name__ == "__main__":
    main()