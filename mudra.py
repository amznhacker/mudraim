#!/usr/bin/env python3
"""
Mudra Gesture Interpreter - Two-stroke keyboard system
Based on the complete specification for fast gesture typing
"""

import subprocess
import sys
import time
import json
from datetime import datetime
from pynput import keyboard, mouse
from pynput.keyboard import Key, Listener

# Install pynput if needed
try:
    import pynput
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pynput"])
    from pynput import keyboard, mouse
    from pynput.keyboard import Key, Listener

class MudraInterpreter:
    def __init__(self):
        self.kb = keyboard.Controller()
        self.mouse_ctrl = mouse.Controller()
        
        # State
        self.mode = "TYPE"  # TYPE or POINTER
        self.buffer = []
        self.last_gesture_time = 0
        self.commit_timeout = 0.26  # 260ms
        self.hold_threshold = 0.7   # 700ms
        self.mode_toggle_hold = 0.8 # 800ms
        
        # Gesture mappings (F13-F19 from Mudra)
        self.gesture_keys = {
            Key.f13: 'R',  # Pinch + Right
            Key.f14: 'L',  # Pinch + Left  
            Key.f15: 'U',  # Pinch + Up
            Key.f16: 'D',  # Pinch + Down
            Key.f17: 'T',  # Double-Tap
            Key.f18: 'W',  # Twist
            Key.f19: 'DW'  # Double-Twist
        }
        
        # Single stroke mappings (top 5 letters = 40% of text)
        self.singles = {
            'R': 'e',  # 12.7%
            'U': 't',  # 9.1%
            'D': 'a',  # 8.2%
            'L': 'o',  # 7.5%
            'T': 'n'   # 6.7%
        }
        
        # Two-stroke 5x5 grid (remaining alphabet + punctuation)
        self.grid = {
            'RR': 's', 'RL': 'h', 'RU': 'r', 'RD': 'd', 'RT': 'l',
            'LR': 'c', 'LL': 'u', 'LU': 'm', 'LD': 'w', 'LT': 'f',
            'UR': 'g', 'UL': 'y', 'UU': 'p', 'UD': 'b', 'UT': 'v',
            'DR': 'k', 'DL': 'j', 'DU': 'x', 'DD': 'q', 'DT': 'z',
            'TR': ',', 'TL': '.', 'TU': "'", 'TD': '?', 'TT': '-'
        }
        
        # Numbers & symbols layer
        self.numsym = {
            'RR': '1', 'RL': '2', 'RU': '3', 'RD': '4', 'RT': '5',
            'LR': '6', 'LL': '7', 'LU': '8', 'LD': '9', 'LT': '0',
            'UR': '!', 'UL': '@', 'UU': '#', 'UD': '$', 'UT': '%',
            'DR': '&', 'DL': '*', 'DU': '(', 'DD': ')', 'DT': '_',
            'TR': ':', 'TL': ';', 'TU': '/', 'TD': '\\', 'TT': '='
        }
        
        # Modifiers (sticky)
        self.modifiers = {
            'shift': False,
            'ctrl': False,
            'alt': False,
            'meta': False
        }
        
        self.numsym_layer = False
        
    def log(self, message):
        """Debug logging"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] {message}")
    
    def commit_buffer(self):
        """Process current buffer and output character"""
        if not self.buffer:
            return
        
        if self.mode == "POINTER":
            self.handle_pointer_gesture()
            self.buffer = []
            return
        
        # TYPE mode
        if len(self.buffer) == 1:
            # Single stroke
            gesture = self.buffer[0]
            if gesture in self.singles:
                char = self.singles[gesture]
                self.type_character(char)
        
        elif len(self.buffer) == 2:
            # Two stroke
            combo = ''.join(self.buffer)
            
            if self.numsym_layer and combo in self.numsym:
                char = self.numsym[combo]
                self.type_character(char)
            elif combo in self.grid:
                char = self.grid[combo]
                self.type_character(char)
            else:
                self.log(f"Unknown combo: {combo}")
        
        self.buffer = []
    
    def type_character(self, char):
        """Type character with modifiers"""
        # Apply sticky modifiers
        if self.modifiers['shift']:
            self.kb.press(Key.shift)
        if self.modifiers['ctrl']:
            self.kb.press(Key.ctrl)
        if self.modifiers['alt']:
            self.kb.press(Key.alt)
        if self.modifiers['meta']:
            self.kb.press(Key.cmd)
        
        # Type character
        self.kb.press(char)
        self.kb.release(char)
        
        # Release modifiers
        if self.modifiers['shift']:
            self.kb.release(Key.shift)
        if self.modifiers['ctrl']:
            self.kb.release(Key.ctrl)
        if self.modifiers['alt']:
            self.kb.release(Key.alt)
        if self.modifiers['meta']:
            self.kb.release(Key.cmd)
        
        # Clear sticky modifiers (except for shortcuts)
        self.modifiers['shift'] = False
        
        self.log(f"Typed: {char}")
    
    def handle_special_gesture(self, gesture, is_hold=False):
        """Handle special gestures"""
        if gesture == 'W':  # Twist
            if is_hold:
                # Delete word
                self.kb.press(Key.ctrl)
                self.kb.press(Key.backspace)
                self.kb.release(Key.backspace)
                self.kb.release(Key.ctrl)
                self.log("Delete word")
            else:
                # Backspace
                self.kb.press(Key.backspace)
                self.kb.release(Key.backspace)
                self.log("Backspace")
        
        elif gesture == 'DW':  # Double-Twist
            if is_hold:
                # Toggle mode
                self.mode = "POINTER" if self.mode == "TYPE" else "TYPE"
                self.log(f"Mode: {self.mode}")
            else:
                # Space
                self.kb.press(Key.space)
                self.kb.release(Key.space)
                self.log("Space")
    
    def handle_pointer_gesture(self):
        """Handle gestures in pointer mode"""
        if len(self.buffer) == 1:
            gesture = self.buffer[0]
            if gesture == 'R':
                self.mouse_ctrl.move(10, 0)
            elif gesture == 'L':
                self.mouse_ctrl.move(-10, 0)
            elif gesture == 'U':
                self.mouse_ctrl.move(0, -10)
            elif gesture == 'D':
                self.mouse_ctrl.move(0, 10)
            elif gesture == 'T':
                self.mouse_ctrl.click(mouse.Button.left)
                self.log("Left click")
        
        elif len(self.buffer) == 2:
            combo = ''.join(self.buffer)
            if combo == 'RR':
                self.mouse_ctrl.click(mouse.Button.left, 2)  # Double click
                self.log("Double click")
            elif combo == 'LL':
                self.mouse_ctrl.click(mouse.Button.right)
                self.log("Right click")
    
    def on_key_press(self, key):
        """Handle gesture input"""
        if key not in self.gesture_keys:
            return
        
        gesture = self.gesture_keys[key]
        current_time = time.time()
        
        # Handle special gestures immediately
        if gesture in ['W', 'DW']:
            self.commit_buffer()  # Commit any pending buffer first
            self.handle_special_gesture(gesture)
            return
        
        # Add to buffer
        self.buffer.append(gesture)
        self.last_gesture_time = current_time
        
        self.log(f"Buffer: {self.buffer}")
        
        # Auto-commit if buffer full
        if len(self.buffer) >= 2:
            self.commit_buffer()
    
    def check_timeout(self):
        """Check if buffer should be committed due to timeout"""
        if self.buffer and time.time() - self.last_gesture_time > self.commit_timeout:
            self.commit_buffer()
    
    def show_status(self):
        """Show current status"""
        print(f"\n🎯 MUDRA INTERPRETER")
        print(f"Mode: {self.mode}")
        print(f"NumSym Layer: {'ON' if self.numsym_layer else 'OFF'}")
        print(f"Buffer: {self.buffer}")
        
        if self.mode == "TYPE":
            print("\nSingle strokes: R→e U→t D→a L→o T→n")
            print("Two strokes: RL→h RU→r LD→w etc.")
            print("Special: W→backspace DW→space")
        else:
            print("\nPointer: R/L/U/D→move T→click")
    
    def run(self):
        """Main interpreter loop"""
        print("🎯 MUDRA GESTURE INTERPRETER")
        print("Two-stroke keyboard system for fast typing!")
        print("\n=== SETUP REQUIRED ===")
        print("In Mudra Studio (Keyboard Mode), assign:")
        print("• Pinch+Right → F13")
        print("• Pinch+Left → F14") 
        print("• Pinch+Up → F15")
        print("• Pinch+Down → F16")
        print("• Double-Tap → F17")
        print("• Twist → F18")
        print("• Double-Twist → F19")
        print("\n=== READY TO TYPE ===")
        print("Single gestures: R→e, U→t, D→a, L→o, T→n")
        print("Two gestures: RL→h, RU→r, LD→w, etc.")
        print("W→backspace, DW→space")
        print("\nPress Ctrl+C to stop")
        
        # Start timeout checker
        import threading
        def timeout_checker():
            while True:
                self.check_timeout()
                time.sleep(0.05)  # Check every 50ms
        
        timeout_thread = threading.Thread(target=timeout_checker, daemon=True)
        timeout_thread.start()
        
        # Start listening
        with Listener(on_press=self.on_key_press) as listener:
            try:
                listener.join()
            except KeyboardInterrupt:
                print("\nMudra Interpreter stopped")

if __name__ == "__main__":
    interpreter = MudraInterpreter()
    interpreter.run()