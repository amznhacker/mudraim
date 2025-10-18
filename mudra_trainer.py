#!/usr/bin/env python3
"""
Mudra Typing Trainer - Learn to type fast with gestures
"""

import time
import random

class MudraTrainer:
    def __init__(self):
        # Character positions (what you'll eventually map to hand gestures)
        self.chars = {
            'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8,
            'j': 0, 'k': 1, 'l': 2, 'm': 3, 'n': 4, 'o': 5, 'p': 6, 'q': 7, 'r': 8,
            's': 0, 't': 1, 'u': 2, 'v': 3, 'w': 4, 'x': 5, 'y': 6, 'z': 7, ' ': 8
        }
        
        # Training words by difficulty
        self.easy_words = ['hi', 'go', 'be', 'do', 'if', 'he', 'we', 'me', 'to', 'at']
        self.medium_words = ['the', 'and', 'you', 'can', 'get', 'had', 'him', 'his', 'how', 'man']
        self.hard_words = ['hello', 'world', 'quick', 'brown', 'jumps', 'right', 'think', 'great']
        
    def show_layout(self):
        """Show character positions"""
        print("\n=== CHARACTER POSITIONS ===")
        print("Letters (Layer 1):")
        print("0:a  1:b  2:c")
        print("3:d  4:e  5:f") 
        print("6:g  7:h  8:i")
        print("\nMore letters (Layer 2):")
        print("0:j  1:k  2:l")
        print("3:m  4:n  5:o")
        print("6:p  7:q  8:r")
        print("\nMore letters (Layer 3):")
        print("0:s  1:t  2:u")
        print("3:v  4:w  5:x")
        print("6:y  7:z  8:space")
    
    def drill_word(self, word):
        """Practice typing a word"""
        print(f"\n=== WORD: '{word}' ===")
        print("Type using number keys 0-8:")
        
        for char in word:
            if char in self.chars:
                pos = self.chars[char]
                print(f"'{char}' → press {pos}")
            else:
                print(f"'{char}' → not mapped")
        
        print(f"\nNow type '{word}' using the positions above:")
        user_input = input("Your typing: ").strip()
        
        if user_input.lower() == word.lower():
            print("✓ Perfect!")
            return True
        else:
            print(f"✗ Expected: {word}, Got: {user_input}")
            return False
    
    def speed_test(self, difficulty='easy'):
        """Timed typing test"""
        if difficulty == 'easy':
            words = self.easy_words
        elif difficulty == 'medium':
            words = self.medium_words
        else:
            words = self.hard_words
        
        test_words = random.sample(words, 5)
        print(f"\n=== SPEED TEST ({difficulty.upper()}) ===")
        print(f"Type these 5 words: {' '.join(test_words)}")
        
        start_time = time.time()
        
        correct = 0
        for word in test_words:
            print(f"\nWord: {word}")
            if self.drill_word(word):
                correct += 1
        
        elapsed = time.time() - start_time
        accuracy = (correct / len(test_words)) * 100
        wpm = (len(' '.join(test_words)) / elapsed) * 60 / 5  # rough WPM
        
        print(f"\n=== RESULTS ===")
        print(f"Accuracy: {accuracy:.0f}% ({correct}/{len(test_words)})")
        print(f"Speed: {wpm:.1f} WPM")
        print(f"Time: {elapsed:.1f} seconds")
    
    def practice_session(self):
        """Guided practice session"""
        print("\n=== PRACTICE SESSION ===")
        print("Let's practice common letters first:")
        
        # Practice most common letters
        common_letters = ['e', 't', 'a', 'o', 'i', 'n', 's', 'h', 'r']
        
        for letter in common_letters[:5]:  # Practice first 5
            pos = self.chars[letter]
            print(f"\nLetter '{letter}' is at position {pos}")
            print("Practice: press the number key to type it")
            input(f"Press {pos} then Enter: ")
        
        print("\n✓ Great! Now let's try some words:")
        
        # Practice easy words
        for word in self.easy_words[:3]:
            self.drill_word(word)
    
    def run(self):
        """Main trainer menu"""
        print("🎯 MUDRA TYPING TRAINER")
        print("Learn to type with gesture positions!")
        
        while True:
            print("\n=== MENU ===")
            print("1. Show character layout")
            print("2. Practice session")
            print("3. Speed test (easy)")
            print("4. Speed test (medium)")
            print("5. Speed test (hard)")
            print("6. Quit")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == '1':
                self.show_layout()
            elif choice == '2':
                self.practice_session()
            elif choice == '3':
                self.speed_test('easy')
            elif choice == '4':
                self.speed_test('medium')
            elif choice == '5':
                self.speed_test('hard')
            elif choice == '6':
                break
            else:
                print("Invalid option")

if __name__ == "__main__":
    trainer = MudraTrainer()
    trainer.run()