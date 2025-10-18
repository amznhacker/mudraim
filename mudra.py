#!/usr/bin/env python3
"""
Mudra - One-click launcher for complete gesture control
"""

import os
import sys
import subprocess
import time
import json
import threading
from pathlib import Path

def install_deps():
    """Auto-install dependencies"""
    try:
        import pynput
        print("✓ Dependencies already installed")
        return True
    except ImportError:
        print("Installing dependencies...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pynput"])
            print("✓ Dependencies installed")
            return True
        except:
            print("✗ Failed to install dependencies")
            print("Run: pip install pynput")
            return False

def check_permissions():
    """Check Linux permissions"""
    if sys.platform.startswith('linux'):
        print("Note: If keyboard input fails, run:")
        print("sudo usermod -a -G input $USER")
        print("Then log out and back in")

class SimpleMudra:
    def __init__(self):
        from pynput import keyboard, mouse
        from pynput.keyboard import Key
        from pynput.mouse import Button
        
        self.kb = keyboard.Controller()
        self.mouse = mouse.Controller()
        self.typing_mode = False
        self.layer = 0  # 0=letters, 1=numbers, 2=symbols
        
        # Simple character maps
        self.chars = [
            # Layer 0: Letters (3x3 grid)
            ['a','b','c','d','e','f','g','h','i'],
            # Layer 1: Numbers  
            ['1','2','3','4','5','6','7','8','9'],
            # Layer 2: Symbols
            ['!','@','#','$','%','^','&','*','(']
        ]
    
    def handle_input(self, cmd):
        """Handle gesture commands"""
        parts = cmd.strip().split()
        if not parts:
            return
            
        action = parts[0].lower()
        
        if action == 'tap':
            if len(parts) == 2 and self.typing_mode:
                # Type character by position (0-8)
                try:
                    pos = int(parts[1])
                    if 0 <= pos < 9:
                        char = self.chars[self.layer][pos]
                        self.kb.press(char)
                        self.kb.release(char)
                        print(f"Typed: {char}")
                except ValueError:
                    pass
            else:
                # Mouse click
                self.mouse.click(Button.left)
                print("Click")
        
        elif action == 'rtap':
            if self.typing_mode:
                self.kb.press(Key.backspace)
                self.kb.release(Key.backspace)
                print("Backspace")
            else:
                self.mouse.click(Button.right)
                print("Right click")
        
        elif action == 'pinch':
            # Pinch = left click (same as tap for consistency)
            self.mouse.click(Button.left)
            print("Left click (pinch)")
        
        elif action == 'twist':
            # Toggle between mouse and typing mode
            self.typing_mode = not self.typing_mode
            mode = "TYPING" if self.typing_mode else "MOUSE"
            print(f"Switched to {mode} mode")
        
        elif action == 'dtwist':
            if self.typing_mode:
                # Switch layers in typing mode
                self.layer = (self.layer + 1) % 3
                layers = ['Letters', 'Numbers', 'Symbols']
                print(f"Layer: {layers[self.layer]}")
            else:
                # Middle click in mouse mode
                self.mouse.click(Button.middle)
                print("Middle click")
        
        elif action == 'move':
            if len(parts) == 3:
                try:
                    x, y = int(parts[1]), int(parts[2])
                    self.mouse.position = (x, y)
                    print(f"Move to ({x}, {y})")
                except ValueError:
                    pass
        
        elif action == 'scroll':
            if len(parts) == 2:
                direction = parts[1].lower()
                if direction == 'up':
                    self.mouse.scroll(0, 1)
                elif direction == 'down':
                    self.mouse.scroll(0, -1)
                print(f"Scroll {direction}")
        
        elif action == 'mouse':
            self.typing_mode = False
            print("MOUSE MODE ON")
        
        elif action == 'help':
            self.show_help()
    
    def show_help(self):
        """Show command help"""
        print("\n=== MUDRA COMMANDS ===")
        print("tap [0-8]     - Left click or type character at position")
        print("pinch         - Left click (same as tap)")
        print("rtap          - Right click or backspace")  
        print("twist         - Toggle between mouse/typing mode")
        print("dtwist        - Switch typing layers or middle click")
        print("move <x> <y>  - Move mouse cursor")
        print("scroll up/down- Scroll page")
        print("mouse         - Switch to mouse mode")
        print("train         - Start typing trainer")
        print("test          - Start speed test")
        print("layout        - Show character layout")
        print("quit          - Exit")
        
        if self.typing_mode:
            print(f"\nCurrent layer: {['Letters', 'Numbers', 'Symbols'][self.layer]}")
            print("Characters:")
            for i, char in enumerate(self.chars[self.layer]):
                print(f"  {i}: {char}")
    
    def show_layout(self):
        """Show character layout"""
        print("\n=== CHARACTER LAYOUT ===")
        for layer_num, layer_name in enumerate(['Letters', 'Numbers', 'Symbols']):
            print(f"\n{layer_name}:")
            chars = self.chars[layer_num]
            for i in range(0, 9, 3):
                row = chars[i:i+3]
                positions = [f"{j}:{char}" for j, char in enumerate(row, i)]
                print(f"  {' '.join(positions)}")

def run_trainer():
    """Simple trainer"""
    print("\n=== QUICK TRAINER ===")
    print("Practice typing common letters:")
    
    common = ['e', 't', 'a', 'o', 'i', 'n']
    positions = {'e': 4, 't': 7, 'a': 0, 'o': 8, 'i': 8, 'n': 7}  # Approximate
    
    for char in common:
        pos = positions.get(char, 0)
        print(f"\nType '{char}' using: tap {pos}")
        input("Press Enter when ready...")
    
    print("✓ Basic training complete!")

def run_speed_test():
    """Simple speed test"""
    print("\n=== SPEED TEST ===")
    test_word = "hello"
    print(f"Type: {test_word}")
    print("Use these commands:")
    
    # Show positions for each letter
    word_positions = {'h': 7, 'e': 4, 'l': 5, 'o': 8}
    for char in test_word:
        pos = word_positions.get(char, 0)
        print(f"  '{char}' -> tap {pos}")
    
    input("\nPress Enter when done...")
    print("✓ Speed test complete!")

def main():
    """Main launcher"""
    print("🎯 MUDRA - Gesture Control System")
    print("=" * 40)
    
    # Auto-setup
    if not install_deps():
        return
    check_permissions()
    
    # Initialize system
    try:
        mudra = SimpleMudra()
        print("✓ Mudra system ready!")
    except Exception as e:
        print(f"✗ Setup failed: {e}")
        return
    
    # Show initial help
    mudra.show_help()
    
    # Main loop
    print(f"\n[{'TYPING' if mudra.typing_mode else 'MOUSE'}] Ready for commands:")
    
    while True:
        try:
            mode = 'TYPING' if mudra.typing_mode else 'MOUSE'
            cmd = input(f"[{mode}]> ").strip()
            
            if cmd.lower() == 'quit':
                break
            elif cmd.lower() == 'train':
                run_trainer()
            elif cmd.lower() == 'test':
                run_speed_test()
            elif cmd.lower() == 'layout':
                mudra.show_layout()
            elif cmd.lower() == 'help':
                mudra.show_help()
            else:
                mudra.handle_input(cmd)
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n👋 Mudra system stopped")

if __name__ == "__main__":
    main()