#!/usr/bin/env python3
"""
Mudra Band Virtual Keyboard
Maps hand gestures to keyboard input using layered character system
"""

import time
from enum import Enum
from pynput import keyboard
from pynput.keyboard import Key, Listener
import threading

class Layer(Enum):
    LETTERS = 0
    NUMBERS = 1
    SYMBOLS = 2

class MudraKeyboard:
    def __init__(self):
        self.controller = keyboard.Controller()
        self.current_layer = Layer.LETTERS
        self.is_shift_held = False
        self.is_ctrl_held = False
        self.is_alt_held = False
        
        # Character maps for each layer based on hand positions
        # Using a 3x3 grid mapping for finger positions
        self.letter_map = {
            (0, 0): 'a', (0, 1): 'b', (0, 2): 'c',
            (1, 0): 'd', (1, 1): 'e', (1, 2): 'f',
            (2, 0): 'g', (2, 1): 'h', (2, 2): 'i',
            (3, 0): 'j', (3, 1): 'k', (3, 2): 'l',
            (4, 0): 'm', (4, 1): 'n', (4, 2): 'o',
            (5, 0): 'p', (5, 1): 'q', (5, 2): 'r',
            (6, 0): 's', (6, 1): 't', (6, 2): 'u',
            (7, 0): 'v', (7, 1): 'w', (7, 2): 'x',
            (8, 0): 'y', (8, 1): 'z', (8, 2): ' '
        }
        
        self.number_map = {
            (0, 0): '1', (0, 1): '2', (0, 2): '3',
            (1, 0): '4', (1, 1): '5', (1, 2): '6',
            (2, 0): '7', (2, 1): '8', (2, 2): '9',
            (3, 0): '0', (3, 1): '.', (3, 2): ',',
        }
        
        self.symbol_map = {
            (0, 0): '!', (0, 1): '@', (0, 2): '#',
            (1, 0): '$', (1, 1): '%', (1, 2): '^',
            (2, 0): '&', (2, 1): '*', (2, 2): '(',
            (3, 0): ')', (3, 1): '-', (3, 2): '+',
            (4, 0): '=', (4, 1): '[', (4, 2): ']',
            (5, 0): '{', (5, 1): '}', (5, 2): '\\',
            (6, 0): '|', (6, 1): ';', (6, 2): ':',
            (7, 0): '"', (7, 1): "'", (7, 2): '<',
            (8, 0): '>', (8, 1): '?', (8, 2): '/'
        }

    def get_current_map(self):
        """Return the current character map based on layer"""
        if self.current_layer == Layer.LETTERS:
            return self.letter_map
        elif self.current_layer == Layer.NUMBERS:
            return self.number_map
        else:
            return self.symbol_map

    def handle_tap(self, position):
        """Handle tap gesture - type character"""
        char_map = self.get_current_map()
        char = char_map.get(position)
        
        if char:
            if self.is_shift_held and char.isalpha():
                char = char.upper()
            self.controller.press(char)
            self.controller.release(char)

    def handle_reverse_tap(self):
        """Handle reverse tap - backspace"""
        self.controller.press(Key.backspace)
        self.controller.release(Key.backspace)

    def handle_twist(self):
        """Handle twist - switch layers"""
        if self.current_layer == Layer.LETTERS:
            self.current_layer = Layer.NUMBERS
        elif self.current_layer == Layer.NUMBERS:
            self.current_layer = Layer.SYMBOLS
        else:
            self.current_layer = Layer.LETTERS
        print(f"Switched to layer: {self.current_layer.name}")

    def handle_double_twist(self):
        """Handle double twist - Enter or Tab"""
        self.controller.press(Key.enter)
        self.controller.release(Key.enter)

    def handle_pinch_hold_start(self, modifier='shift'):
        """Handle pinch and hold start - modifier key down"""
        if modifier == 'shift':
            self.is_shift_held = True
            self.controller.press(Key.shift)
        elif modifier == 'ctrl':
            self.is_ctrl_held = True
            self.controller.press(Key.ctrl)
        elif modifier == 'alt':
            self.is_alt_held = True
            self.controller.press(Key.alt)

    def handle_pinch_hold_end(self, modifier='shift'):
        """Handle pinch and hold end - modifier key up"""
        if modifier == 'shift' and self.is_shift_held:
            self.is_shift_held = False
            self.controller.release(Key.shift)
        elif modifier == 'ctrl' and self.is_ctrl_held:
            self.is_ctrl_held = False
            self.controller.release(Key.ctrl)
        elif modifier == 'alt' and self.is_alt_held:
            self.is_alt_held = False
            self.controller.release(Key.alt)

    def handle_reverse_pinch_slide(self, direction):
        """Handle reverse pinch and slide - arrow keys/scroll"""
        if direction == 'up':
            self.controller.press(Key.up)
            self.controller.release(Key.up)
        elif direction == 'down':
            self.controller.press(Key.down)
            self.controller.release(Key.down)
        elif direction == 'left':
            self.controller.press(Key.left)
            self.controller.release(Key.left)
        elif direction == 'right':
            self.controller.press(Key.right)
            self.controller.release(Key.right)

    def type_text(self, text):
        """Type a string of text"""
        for char in text:
            self.controller.press(char)
            self.controller.release(char)
            time.sleep(0.01)  # Small delay between characters

if __name__ == "__main__":
    keyboard_system = MudraKeyboard()
    print("Mudra Virtual Keyboard initialized")
    print(f"Current layer: {keyboard_system.current_layer.name}")
    
    # Keep the program running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down Mudra Keyboard")