#!/usr/bin/env python3
"""
Mudra Speed Test - Measure your typing speed
"""

import time
import random

class MudraSpeedTest:
    def __init__(self):
        self.test_texts = {
            'easy': [
                "the quick brown fox jumps over the lazy dog",
                "hello world this is a test of your speed",
                "coding is fun when you learn new things"
            ],
            'medium': [
                "Python is a powerful programming language used for many applications",
                "Machine learning and artificial intelligence are changing the world",
                "The future of technology depends on innovation and creativity"
            ],
            'hard': [
                "Advanced algorithms require careful optimization and testing procedures",
                "Cybersecurity professionals must stay updated with the latest threats",
                "Quantum computing represents a paradigm shift in computational power"
            ]
        }
        
        self.char_positions = {
            'a': (0,0), 'b': (0,1), 'c': (0,2), 'd': (1,0), 'e': (1,1), 'f': (1,2),
            'g': (2,0), 'h': (2,1), 'i': (2,2), 'j': (3,0), 'k': (3,1), 'l': (3,2),
            'm': (4,0), 'n': (4,1), 'o': (4,2), 'p': (5,0), 'q': (5,1), 'r': (5,2),
            's': (6,0), 't': (6,1), 'u': (6,2), 'v': (7,0), 'w': (7,1), 'x': (7,2),
            'y': (8,0), 'z': (8,1), ' ': (8,2)
        }
    
    def run_test(self, difficulty='easy', duration=60):
        """Run a typing speed test"""
        text = random.choice(self.test_texts[difficulty])
        print(f"\n=== {difficulty.upper()} Speed Test ({duration}s) ===")
        print(f"Type this text using gesture positions:\n")
        print(f'"{text}"\n')
        
        input("Press Enter when ready...")
        
        start_time = time.time()
        correct_chars = 0
        total_chars = len(text)
        errors = 0
        
        print(f"\nStart typing! ({duration} seconds)")
        
        for i, target_char in enumerate(text):
            if time.time() - start_time > duration:
                break
                
            remaining_time = duration - (time.time() - start_time)
            if remaining_time <= 0:
                break
                
            print(f"\nTime: {remaining_time:.1f}s | Progress: {i+1}/{total_chars}")
            print(f"Target: '{target_char}'")
            
            if target_char in self.char_positions:
                pos = self.char_positions[target_char]
                print(f"Position: ({pos[0]}, {pos[1]})")
            
            try:
                user_input = input("Gesture (x y): ").strip().split()
                if len(user_input) == 2:
                    x, y = int(user_input[0]), int(user_input[1])
                    expected = self.char_positions.get(target_char)
                    
                    if expected and (x, y) == expected:
                        correct_chars += 1
                        print("✓")
                    else:
                        errors += 1
                        print(f"✗ Expected: {expected}")
                else:
                    errors += 1
                    print("✗ Invalid format")
            except ValueError:
                errors += 1
                print("✗ Invalid input")
        
        elapsed = time.time() - start_time
        self.show_results(correct_chars, errors, elapsed, text[:i+1])
    
    def show_results(self, correct, errors, elapsed, attempted_text):
        """Display test results"""
        total_attempts = correct + errors
        accuracy = (correct / total_attempts * 100) if total_attempts > 0 else 0
        
        # Calculate WPM (Words Per Minute)
        # Standard: 5 characters = 1 word
        words_typed = correct / 5
        wpm = (words_typed / elapsed) * 60
        
        # Calculate CPM (Characters Per Minute)
        cpm = (correct / elapsed) * 60
        
        print(f"\n=== Results ===")
        print(f"Time: {elapsed:.1f} seconds")
        print(f"Characters typed correctly: {correct}")
        print(f"Errors: {errors}")
        print(f"Accuracy: {accuracy:.1f}%")
        print(f"Speed: {wpm:.1f} WPM")
        print(f"Speed: {cpm:.1f} CPM")
        
        # Performance rating
        if wpm >= 40:
            rating = "🚀 EXPERT"
        elif wpm >= 25:
            rating = "⭐ ADVANCED"
        elif wpm >= 15:
            rating = "👍 GOOD"
        elif wpm >= 10:
            rating = "📈 IMPROVING"
        else:
            rating = "🌱 BEGINNER"
        
        print(f"Rating: {rating}")
        
        # Suggestions
        if accuracy < 90:
            print("\n💡 Focus on accuracy before speed")
        elif wpm < 20:
            print("\n💡 Practice more to increase speed")
        else:
            print("\n🎉 Great job! Keep practicing!")
    
    def quick_test(self):
        """30-second quick test"""
        self.run_test('easy', 30)
    
    def run(self):
        """Main menu"""
        while True:
            print(f"\n=== Mudra Speed Test ===")
            print("1. Quick test (30s, easy)")
            print("2. Standard test (60s)")
            print("3. Custom test")
            print("4. Quit")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == '1':
                self.quick_test()
            elif choice == '2':
                difficulty = input("Difficulty (easy/medium/hard): ").strip().lower()
                if difficulty in self.test_texts:
                    self.run_test(difficulty, 60)
                else:
                    print("Invalid difficulty")
            elif choice == '3':
                difficulty = input("Difficulty (easy/medium/hard): ").strip().lower()
                try:
                    duration = int(input("Duration (seconds): "))
                    if difficulty in self.test_texts and duration > 0:
                        self.run_test(difficulty, duration)
                    else:
                        print("Invalid input")
                except ValueError:
                    print("Invalid duration")
            elif choice == '4':
                break
            else:
                print("Invalid option")

if __name__ == "__main__":
    speed_test = MudraSpeedTest()
    speed_test.run()