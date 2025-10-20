#!/usr/bin/env python3
"""
Mudra Debug Tool - See what keys are sent vs what you intended
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

class MudraDebugger:
    def __init__(self):
        self.kb = keyboard.Controller()
        
        # Expected mappings
        self.expected_mappings = {
            'pinch_right': 'RIGHT',
            'pinch_left': 'LEFT',
            'pinch_up': 'UP', 
            'pinch_down': 'DOWN',
            'double_tap': 'ENTER',
            'twist': 'F2',
            'double_twist': 'F3'
        }
        
        # Key history
        self.key_history = []
        self.max_history = 20
        
        # Current test
        self.current_test = None
        self.test_start_time = 0
        self.test_timeout = 3.0
        
        # Remove debouncing - it's causing issues
        self.processing = False
        
        self.create_gui()
    
    def create_gui(self):
        """Create debug GUI"""
        self.root = tk.Tk()
        self.root.title("🔍 Mudra Debugger")
        self.root.geometry("500x600")
        self.root.configure(bg='#f0f0f0')
        
        # Title
        title = tk.Label(self.root, text="🔍 Mudra Debug Tool", 
                        font=('Arial', 16, 'bold'), bg='#f0f0f0')
        title.pack(pady=10)
        
        # Instructions
        instructions = tk.Label(self.root, 
                              text="1. Click a gesture button\n2. Do that gesture on Mudra\n3. See what keys were received", 
                              font=('Arial', 10), bg='#f0f0f0', justify=tk.LEFT)
        instructions.pack(pady=5)
        
        # Test buttons frame
        test_frame = tk.LabelFrame(self.root, text="Test Gestures", font=('Arial', 12, 'bold'))
        test_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Create test buttons
        button_frame1 = tk.Frame(test_frame)
        button_frame1.pack(pady=5)
        
        tk.Button(button_frame1, text="PINCH + RIGHT", command=lambda: self.start_test('pinch_right'),
                 font=('Arial', 10), bg='#4CAF50', fg='white', width=15).pack(side=tk.LEFT, padx=2)
        
        tk.Button(button_frame1, text="PINCH + LEFT", command=lambda: self.start_test('pinch_left'),
                 font=('Arial', 10), bg='#4CAF50', fg='white', width=15).pack(side=tk.LEFT, padx=2)
        
        button_frame2 = tk.Frame(test_frame)
        button_frame2.pack(pady=5)
        
        tk.Button(button_frame2, text="PINCH + UP", command=lambda: self.start_test('pinch_up'),
                 font=('Arial', 10), bg='#4CAF50', fg='white', width=15).pack(side=tk.LEFT, padx=2)
        
        tk.Button(button_frame2, text="PINCH + DOWN", command=lambda: self.start_test('pinch_down'),
                 font=('Arial', 10), bg='#4CAF50', fg='white', width=15).pack(side=tk.LEFT, padx=2)
        
        button_frame3 = tk.Frame(test_frame)
        button_frame3.pack(pady=5)
        
        tk.Button(button_frame3, text="DOUBLE TAP", command=lambda: self.start_test('double_tap'),
                 font=('Arial', 10), bg='#2196F3', fg='white', width=15).pack(side=tk.LEFT, padx=2)
        
        tk.Button(button_frame3, text="TWIST", command=lambda: self.start_test('twist'),
                 font=('Arial', 10), bg='#FF9800', fg='white', width=15).pack(side=tk.LEFT, padx=2)
        
        tk.Button(button_frame3, text="DOUBLE TWIST", command=lambda: self.start_test('double_twist'),
                 font=('Arial', 10), bg='#F44336', fg='white', width=15).pack(side=tk.LEFT, padx=2)
        
        # Current test display
        test_display_frame = tk.LabelFrame(self.root, text="Current Test", font=('Arial', 12, 'bold'))
        test_display_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.test_label = tk.Label(test_display_frame, text="Click a button to start testing", 
                                  font=('Arial', 12), fg='#666')
        self.test_label.pack(pady=10)
        
        self.expected_label = tk.Label(test_display_frame, text="", 
                                     font=('Arial', 10), fg='#333')
        self.expected_label.pack(pady=2)
        
        self.received_label = tk.Label(test_display_frame, text="", 
                                     font=('Arial', 10), fg='#333')
        self.received_label.pack(pady=2)
        
        self.result_label = tk.Label(test_display_frame, text="", 
                                   font=('Arial', 12, 'bold'))
        self.result_label.pack(pady=5)
        
        # Key history
        history_frame = tk.LabelFrame(self.root, text="Key History (Last 20)", font=('Arial', 12, 'bold'))
        history_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create listbox with scrollbar
        list_frame = tk.Frame(history_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.history_listbox = tk.Listbox(list_frame, font=('Courier', 9))
        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.history_listbox.yview)
        self.history_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Control buttons
        control_frame = tk.Frame(self.root, bg='#f0f0f0')
        control_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(control_frame, text="Clear History", command=self.clear_history,
                 font=('Arial', 10), bg='#9E9E9E', fg='white').pack(side=tk.LEFT, padx=5)
        
        tk.Button(control_frame, text="Exit", command=self.exit_app,
                 font=('Arial', 10), bg='#607D8B', fg='white').pack(side=tk.RIGHT, padx=5)
        
        # Start keyboard listener
        self.keyboard_listener = KeyboardListener(on_press=self.on_key_press)
        self.keyboard_listener.start()
        
        # Update loop
        self.update_display()
    
    def start_test(self, gesture_name):
        """Start testing a specific gesture"""
        self.current_test = gesture_name
        self.test_start_time = time.time()
        
        expected_key = self.expected_mappings[gesture_name]
        
        self.test_label.config(text=f"Testing: {gesture_name.replace('_', ' ').upper()}", 
                              fg='#2196F3')
        self.expected_label.config(text=f"Expected key: {expected_key}")
        self.received_label.config(text="Received: (waiting...)")
        self.result_label.config(text="Do the gesture now!", fg='#FF9800')
        
        # Clear recent history for this test
        self.add_to_history(f"--- TESTING {gesture_name.upper()} ---", special=True)
    
    def add_to_history(self, message, special=False):
        """Add message to history"""
        timestamp = time.strftime("%H:%M:%S")
        
        if special:
            entry = f"[{timestamp}] {message}"
        else:
            entry = f"[{timestamp}] Key: {message}"
        
        self.key_history.append(entry)
        
        # Keep only last N entries
        if len(self.key_history) > self.max_history:
            self.key_history.pop(0)
        
        # Update listbox
        self.history_listbox.delete(0, tk.END)
        for item in self.key_history:
            self.history_listbox.insert(tk.END, item)
        
        # Scroll to bottom
        self.history_listbox.see(tk.END)
    
    def clear_history(self):
        """Clear key history"""
        self.key_history = []
        self.history_listbox.delete(0, tk.END)
    
    def update_display(self):
        """Update display and check test timeout"""
        if self.current_test and time.time() - self.test_start_time > self.test_timeout:
            self.result_label.config(text="Test timed out - try again", fg='#F44336')
            self.current_test = None
        
        self.root.after(100, self.update_display)
    
    def on_key_press(self, key):
        """Handle key presses"""
        # Prevent recursive processing
        if self.processing:
            return
        
        self.processing = True
        
        # Convert key to string
        key_str = str(key).replace('Key.', '').upper()
        
        # Add to history
        self.add_to_history(key_str)
        
        # Check if we're testing
        if self.current_test:
            expected_key = self.expected_mappings[self.current_test]
            
            self.received_label.config(text=f"Received: {key_str}")
            
            if key_str == expected_key:
                self.result_label.config(text="✅ CORRECT! Gesture works perfectly", fg='#4CAF50')
            else:
                self.result_label.config(text=f"❌ WRONG! Expected {expected_key}, got {key_str}", fg='#F44336')
                
                # Provide fix suggestion
                self.suggest_fix(self.current_test, expected_key, key_str)
            
            self.current_test = None
        
        # Exit on ESC
        if key == Key.esc:
            self.exit_app()
        
        # Reset processing flag
        self.processing = False
    
    def suggest_fix(self, gesture, expected, received):
        """Suggest how to fix the mapping"""
        fix_message = f"\n🔧 FIX: In Mudra app, change {gesture.replace('_', ' ')} from {received} to {expected}"
        self.add_to_history(fix_message, special=True)
        
        # Show in result label too
        self.result_label.config(text=f"❌ Fix needed: Change {gesture.replace('_', ' ')} to {expected}", fg='#F44336')
    
    def exit_app(self):
        """Exit application"""
        self.keyboard_listener.stop()
        self.root.quit()
    
    def run(self):
        """Start debugger"""
        print("🔍 MUDRA DEBUGGER")
        print("GUI will open to test your gestures...")
        print("\n=== HOW TO USE ===")
        print("1. Click a gesture button (e.g., 'PINCH + RIGHT')")
        print("2. Do that exact gesture on your Mudra band")
        print("3. See if the correct key was received")
        print("4. If wrong, follow the fix suggestion")
        
        try:
            self.root.mainloop()
        except Exception as e:
            print(f"Error: {e}")
        finally:
            if hasattr(self, 'keyboard_listener'):
                self.keyboard_listener.stop()

if __name__ == "__main__":
    debugger = MudraDebugger()
    debugger.run()