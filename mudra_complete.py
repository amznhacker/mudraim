#!/usr/bin/env python3
"""
Complete Mudra System - Mouse + Keyboard
"""

import time
from pynput import mouse, keyboard
from pynput.mouse import Button, Listener as MouseListener
from pynput.keyboard import Key, Listener as KeyboardListener
from mudra_keyboard import MudraKeyboard

class MudraComplete:
    def __init__(self):
        self.keyboard_system = MudraKeyboard()
        self.mouse_controller = mouse.Controller()
        self.is_typing_mode = False
        
    def handle_gesture(self, gesture_type, data=None):
        """Route gestures to mouse or keyboard based on context"""
        
        if gesture_type == "hand_position":
            # Mouse cursor movement
            x, y = data
            self.mouse_controller.position = (x, y)
            
        elif gesture_type == "tap":
            if self.is_typing_mode:
                # Keyboard input
                position = data
                self.keyboard_system.handle_tap(position)
            else:
                # Mouse click
                self.mouse_controller.click(Button.left)
                
        elif gesture_type == "reverse_tap":
            if self.is_typing_mode:
                self.keyboard_system.handle_reverse_tap()
            else:
                self.mouse_controller.click(Button.right)
                
        elif gesture_type == "pinch_hold_start":
            if self.is_typing_mode:
                modifier = data or 'shift'
                self.keyboard_system.handle_pinch_hold_start(modifier)
            else:
                # Mouse drag start
                self.mouse_controller.press(Button.left)
                
        elif gesture_type == "pinch_hold_end":
            if self.is_typing_mode:
                modifier = data or 'shift'
                self.keyboard_system.handle_pinch_hold_end(modifier)
            else:
                # Mouse drag end
                self.mouse_controller.release(Button.left)
                
        elif gesture_type == "reverse_pinch_slide":
            direction = data
            if self.is_typing_mode:
                self.keyboard_system.handle_reverse_pinch_slide(direction)
            else:
                # Mouse scroll
                if direction in ['up', 'down']:
                    scroll_y = 1 if direction == 'up' else -1
                    self.mouse_controller.scroll(0, scroll_y)
                    
        elif gesture_type == "twist":
            if self.is_typing_mode:
                self.keyboard_system.handle_twist()
            else:
                # Toggle typing mode
                self.toggle_typing_mode()
                
        elif gesture_type == "double_twist":
            if self.is_typing_mode:
                self.keyboard_system.handle_double_twist()
            else:
                # Enter typing mode
                self.enter_typing_mode()
    
    def toggle_typing_mode(self):
        """Toggle between mouse and keyboard mode"""
        self.is_typing_mode = not self.is_typing_mode
        mode = "KEYBOARD" if self.is_typing_mode else "MOUSE"
        print(f"Switched to {mode} mode")
    
    def enter_typing_mode(self):
        """Enter typing mode (for text fields)"""
        self.is_typing_mode = True
        print("Entered KEYBOARD mode")
    
    def simulate_gesture(self, gesture, data=None):
        """Simulate gesture for testing"""
        print(f"Gesture: {gesture} {data if data else ''}")
        self.handle_gesture(gesture, data)

if __name__ == "__main__":
    system = MudraComplete()
    print("Mudra Complete System - Mouse + Keyboard")
    print("Commands:")
    print("  move <x> <y> - Move cursor")
    print("  tap [x y] - Click or type")
    print("  rtap - Right click or backspace")
    print("  twist - Switch modes or layer")
    print("  dtwist - Enter typing mode or Enter key")
    print("  hold/release - Drag or modifier")
    print("  slide <dir> - Scroll or arrows")
    print("  quit - Exit")
    
    while True:
        try:
            cmd = input(f"[{'KB' if system.is_typing_mode else 'MS'}]> ").strip().split()
            if not cmd:
                continue
                
            if cmd[0] == "quit":
                break
            elif cmd[0] == "move" and len(cmd) == 3:
                x, y = int(cmd[1]), int(cmd[2])
                system.simulate_gesture("hand_position", (x, y))
            elif cmd[0] == "tap":
                if len(cmd) == 3:
                    pos = (int(cmd[1]), int(cmd[2]))
                    system.simulate_gesture("tap", pos)
                else:
                    system.simulate_gesture("tap")
            elif cmd[0] == "rtap":
                system.simulate_gesture("reverse_tap")
            elif cmd[0] == "twist":
                system.simulate_gesture("twist")
            elif cmd[0] == "dtwist":
                system.simulate_gesture("double_twist")
            elif cmd[0] == "hold":
                modifier = cmd[1] if len(cmd) > 1 else None
                system.simulate_gesture("pinch_hold_start", modifier)
            elif cmd[0] == "release":
                modifier = cmd[1] if len(cmd) > 1 else None
                system.simulate_gesture("pinch_hold_end", modifier)
            elif cmd[0] == "slide" and len(cmd) == 2:
                system.simulate_gesture("reverse_pinch_slide", cmd[1])
            else:
                print("Invalid command")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")