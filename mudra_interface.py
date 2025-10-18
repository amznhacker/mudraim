#!/usr/bin/env python3
"""
Mudra Band Interface
Simulates gesture input for testing the virtual keyboard
In production, this would connect to actual Mudra band hardware
"""

import time
import threading
from mudra_keyboard import MudraKeyboard

class MudraInterface:
    def __init__(self):
        self.keyboard = MudraKeyboard()
        self.is_running = False
        
    def start(self):
        """Start the Mudra interface"""
        self.is_running = True
        print("Mudra Interface started")
        print("Commands:")
        print("  tap <x> <y> - Tap at position (0-8, 0-2)")
        print("  rtap - Reverse tap (backspace)")
        print("  twist - Switch layer")
        print("  dtwist - Double twist (enter)")
        print("  hold <modifier> - Hold modifier (shift/ctrl/alt)")
        print("  release <modifier> - Release modifier")
        print("  slide <direction> - Slide (up/down/left/right)")
        print("  type <text> - Type text directly")
        print("  quit - Exit")
        
        while self.is_running:
            try:
                command = input("> ").strip().split()
                if not command:
                    continue
                    
                cmd = command[0].lower()
                
                if cmd == "quit":
                    self.stop()
                elif cmd == "tap" and len(command) == 3:
                    x, y = int(command[1]), int(command[2])
                    self.keyboard.handle_tap((x, y))
                elif cmd == "rtap":
                    self.keyboard.handle_reverse_tap()
                elif cmd == "twist":
                    self.keyboard.handle_twist()
                elif cmd == "dtwist":
                    self.keyboard.handle_double_twist()
                elif cmd == "hold" and len(command) == 2:
                    self.keyboard.handle_pinch_hold_start(command[1])
                elif cmd == "release" and len(command) == 2:
                    self.keyboard.handle_pinch_hold_end(command[1])
                elif cmd == "slide" and len(command) == 2:
                    self.keyboard.handle_reverse_pinch_slide(command[1])
                elif cmd == "type" and len(command) > 1:
                    text = " ".join(command[1:])
                    self.keyboard.type_text(text)
                else:
                    print("Invalid command")
                    
            except KeyboardInterrupt:
                self.stop()
            except Exception as e:
                print(f"Error: {e}")
    
    def stop(self):
        """Stop the Mudra interface"""
        self.is_running = False
        print("Mudra Interface stopped")

if __name__ == "__main__":
    interface = MudraInterface()
    interface.start()