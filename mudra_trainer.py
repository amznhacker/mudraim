#!/usr/bin/env python3
"""
Mudra Typing Trainer - Learn gestures fast
"""

import time
import random
from collections import defaultdict
import json
import os

class MudraTrainer:
    def __init__(self):
        self.stats_file = "training_stats.json"
        self.load_stats()
        
        # Training sets by difficulty
        self.beginner_chars = list("etaoinshrdlu")  # Most common letters
        self.intermediate_chars = list("cmfwypvbgkjqxz")
        self.advanced_chars = list("1234567890!@#$%^&*()")
        
        # Position mappings
        self.char_positions = {
            'a': (0,0), 'b': (0,1), 'c': (0,2), 'd': (1,0), 'e': (1,1), 'f': (1,2),
            'g': (2,0), 'h': (2,1), 'i': (2,2), 'j': (3,0), 'k': (3,1), 'l': (3,2),
            'm': (4,0), 'n': (4,1), 'o': (4,2), 'p': (5,0), 'q': (5,1), 'r': (5,2),
            's': (6,0), 't': (6,1), 'u': (6,2), 'v': (7,0), 'w': (7,1), 'x': (7,2),
            'y': (8,0), 'z': (8,1), ' ': (8,2),
            '1': (0,0), '2': (0,1), '3': (0,2), '4': (1,0), '5': (1,1), '6': (1,2),
            '7': (2,0), '8': (2,1), '9': (2,2), '0': (3,0)
        }
        
    def load_stats(self):
        """Load training statistics"""
        if os.path.exists(self.stats_file):
            with open(self.stats_file, 'r') as f:
                self.stats = json.load(f)
        else:
            self.stats = {
                'chars_learned': set(),
                'accuracy': defaultdict(float),
                'speed': defaultdict(float),
                'sessions': 0,
                'total_time': 0
            }
    
    def save_stats(self):
        """Save training statistics"""
        # Convert set to list for JSON serialization
        stats_copy = self.stats.copy()
        stats_copy['chars_learned'] = list(self.stats['chars_learned'])
        with open(self.stats_file, 'w') as f:
            json.dump(stats_copy, f, indent=2)
    
    def show_position(self, char):
        """Show visual position for character"""
        if char not in self.char_positions:
            return f"Character '{char}' not mapped"
            
        pos = self.char_positions[char]
        grid = [['·' for _ in range(3)] for _ in range(9)]
        grid[pos[0]][pos[1]] = '●'
        
        print(f"\nPosition for '{char}': ({pos[0]}, {pos[1]})")
        print("Grid visualization:")
        for i, row in enumerate(grid):
            print(f"{i}: {' '.join(row)}")
    
    def drill_character(self, char):
        """Practice single character"""
        print(f"\n=== Character Drill: '{char}' ===")
        self.show_position(char)
        
        correct = 0
        total = 5
        start_time = time.time()
        
        for i in range(total):
            print(f"\nRound {i+1}/{total}")
            print(f"Type gesture for: {char}")
            
            try:
                user_input = input("Enter position (x y): ").strip().split()
                if len(user_input) != 2:
                    print("Invalid format. Use: x y")
                    continue
                    
                x, y = int(user_input[0]), int(user_input[1])
                expected = self.char_positions[char]
                
                if (x, y) == expected:
                    print("✓ Correct!")
                    correct += 1
                else:
                    print(f"✗ Wrong. Expected: {expected}, Got: ({x}, {y})")
                    
            except (ValueError, KeyError):
                print("Invalid input")
        
        elapsed = time.time() - start_time
        accuracy = (correct / total) * 100
        speed = total / elapsed * 60  # chars per minute
        
        print(f"\n--- Results ---")
        print(f"Accuracy: {accuracy:.1f}% ({correct}/{total})")
        print(f"Speed: {speed:.1f} gestures/min")
        
        # Update stats
        self.stats['accuracy'][char] = accuracy
        self.stats['speed'][char] = speed
        if accuracy >= 80:
            self.stats['chars_learned'].add(char)
        
        return accuracy >= 80
    
    def word_challenge(self, difficulty='beginner'):
        """Practice typing words"""
        if difficulty == 'beginner':
            chars = self.beginner_chars
            words = ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had']
        elif difficulty == 'intermediate':
            chars = self.beginner_chars + self.intermediate_chars
            words = ['hello', 'world', 'python', 'coding', 'gesture', 'typing', 'fast', 'learn']
        else:
            chars = self.beginner_chars + self.intermediate_chars + self.advanced_chars
            words = ['hello123', 'test@email.com', 'password!', 'user#1', 'code$']
        
        word = random.choice(words)
        print(f"\n=== Word Challenge: '{word}' ===")
        
        # Show positions for each character
        for char in word:
            if char in self.char_positions:
                pos = self.char_positions[char]
                print(f"'{char}' -> ({pos[0]}, {pos[1]})")
        
        print(f"\nType the word: {word}")
        start_time = time.time()
        
        correct_chars = 0
        for i, char in enumerate(word):
            print(f"\nCharacter {i+1}/{len(word)}: '{char}'")
            try:
                user_input = input("Position (x y): ").strip().split()
                if len(user_input) == 2:
                    x, y = int(user_input[0]), int(user_input[1])
                    expected = self.char_positions.get(char)
                    if expected and (x, y) == expected:
                        print("✓")
                        correct_chars += 1
                    else:
                        print(f"✗ Expected: {expected}")
                else:
                    print("✗ Invalid format")
            except ValueError:
                print("✗ Invalid input")
        
        elapsed = time.time() - start_time
        accuracy = (correct_chars / len(word)) * 100
        wpm = (len(word) / elapsed) * 60
        
        print(f"\n--- Word Results ---")
        print(f"Accuracy: {accuracy:.1f}%")
        print(f"Speed: {wpm:.1f} chars/min")
        
        return accuracy >= 90
    
    def adaptive_training(self):
        """Adaptive training based on weakest characters"""
        weak_chars = []
        for char in self.beginner_chars:
            if char not in self.stats['chars_learned'] or self.stats['accuracy'].get(char, 0) < 90:
                weak_chars.append(char)
        
        if not weak_chars:
            print("🎉 All beginner characters mastered! Try intermediate mode.")
            return
        
        print(f"\n=== Adaptive Training ===")
        print(f"Focusing on weak characters: {weak_chars}")
        
        for char in weak_chars[:3]:  # Train 3 weakest
            self.drill_character(char)
    
    def progress_report(self):
        """Show learning progress"""
        print(f"\n=== Progress Report ===")
        print(f"Sessions completed: {self.stats['sessions']}")
        print(f"Characters learned: {len(self.stats['chars_learned'])}/26")
        
        if self.stats['chars_learned']:
            avg_accuracy = sum(self.stats['accuracy'].get(c, 0) for c in self.stats['chars_learned']) / len(self.stats['chars_learned'])
            avg_speed = sum(self.stats['speed'].get(c, 0) for c in self.stats['chars_learned']) / len(self.stats['chars_learned'])
            print(f"Average accuracy: {avg_accuracy:.1f}%")
            print(f"Average speed: {avg_speed:.1f} gestures/min")
        
        print(f"Mastered characters: {sorted(list(self.stats['chars_learned']))}")
    
    def run(self):
        """Main training loop"""
        print("🎯 Mudra Typing Trainer")
        print("Learn gestures fast with adaptive training!")
        
        while True:
            print(f"\n--- Main Menu ---")
            print("1. Character drill")
            print("2. Word challenge")
            print("3. Adaptive training")
            print("4. Progress report")
            print("5. Quit")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == '1':
                char = input("Enter character to practice: ").strip().lower()
                if char in self.char_positions:
                    self.drill_character(char)
                else:
                    print("Character not supported")
            elif choice == '2':
                difficulty = input("Difficulty (beginner/intermediate/advanced): ").strip().lower()
                self.word_challenge(difficulty)
            elif choice == '3':
                self.adaptive_training()
            elif choice == '4':
                self.progress_report()
            elif choice == '5':
                break
            else:
                print("Invalid option")
            
            self.stats['sessions'] += 1
            self.save_stats()

if __name__ == "__main__":
    trainer = MudraTrainer()
    trainer.run()