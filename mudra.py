#!/usr/bin/env python3
"""
Mudra AI Learning System - Console-based to avoid X11 errors
"""

import subprocess
import sys
import time
import json
import os
import numpy as np
from collections import deque
from pynput import keyboard
from pynput.keyboard import Key, Listener as KeyboardListener

# Install required packages
packages = ['pynput', 'numpy', 'scikit-learn']
for package in packages:
    try:
        __import__(package.replace('-', '_'))
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
import pickle

class MudraAI:
    def __init__(self):
        self.kb = keyboard.Controller()
        
        # Gesture mappings
        self.gesture_labels = {
            'pinch_right': 'e',
            'pinch_left': 't', 
            'pinch_up': 'a',
            'pinch_down': 'o',
            'double_tap': 'i',
            'twist': ' ',
            'double_twist': 'BACKSPACE',
            'twist_pinch_right': 'n',
            'twist_pinch_left': 's',
            'twist_pinch_up': 'h',
            'twist_pinch_down': 'r',
            'twist_double_tap': 'd',
            'double_twist_pinch_right': 'l',
            'double_twist_pinch_left': 'c',
            'double_twist_pinch_up': 'u',
            'double_twist_pinch_down': 'm',
            'double_twist_double_tap': 'w',
        }
        
        # Neural network
        self.model = MLPClassifier(
            hidden_layer_sizes=(50, 25),
            max_iter=500,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        
        # Training data
        self.training_data = []
        self.training_labels = []
        
        # Gesture tracking
        self.current_sequence = []
        self.sequence_start_time = 0
        self.sequence_timeout = 1.5
        
        # Debouncing
        self.last_key = None
        self.last_key_time = 0
        self.debounce_delay = 0.15
        
        self.load_model()
    
    def extract_features(self, key_sequence):
        """Extract 10 simple features"""
        if not key_sequence:
            return np.zeros(10)
        
        features = [len(key_sequence)]  # Length
        
        # Key counts
        key_counts = {'right': 0, 'left': 0, 'up': 0, 'down': 0, 'enter': 0, 'f2': 0, 'f3': 0}
        for key_info in key_sequence:
            key_name = key_info['key']
            if key_name in key_counts:
                key_counts[key_name] += 1
        
        features.extend([key_counts['right'], key_counts['left'], key_counts['up'], 
                        key_counts['down'], key_counts['enter'], key_counts['f2'], key_counts['f3']])
        
        # Timing
        if len(key_sequence) > 1:
            total_time = key_sequence[-1]['time'] - key_sequence[0]['time']
            features.append(total_time)
        else:
            features.append(0)
        
        # First key
        first_key_encoding = {'right': 1, 'left': 2, 'up': 3, 'down': 4, 'enter': 5, 'f2': 6, 'f3': 7}
        features.append(first_key_encoding.get(key_sequence[0]['key'], 0))
        
        return np.array(features[:10])
    
    def classify_gesture(self, key_sequence):
        """Classify gesture"""
        features = self.extract_features(key_sequence)
        
        if not self.is_trained or len(self.training_data) < 5:
            return self.rule_based_classify(key_sequence)
        
        try:
            features_scaled = self.scaler.transform([features])
            prediction = self.model.predict(features_scaled)[0]
            confidence = max(self.model.predict_proba(features_scaled)[0])
            return prediction, confidence
        except:
            return self.rule_based_classify(key_sequence)
    
    def rule_based_classify(self, key_sequence):
        """Simple rule-based fallback"""
        if not key_sequence:
            return 'unknown', 0.0
        
        if len(key_sequence) == 1:
            key_name = key_sequence[0]['key']
            mapping = {
                'right': 'pinch_right',
                'left': 'pinch_left',
                'up': 'pinch_up',
                'down': 'pinch_down',
                'enter': 'double_tap',
                'f2': 'twist',
                'f3': 'double_twist'
            }
            return mapping.get(key_name, 'unknown'), 0.7
        
        elif len(key_sequence) == 2:
            first, second = key_sequence[0]['key'], key_sequence[1]['key']
            if first == 'f2':
                return f'twist_pinch_{second}', 0.6
            elif first == 'f3':
                return f'double_twist_pinch_{second}', 0.6
        
        return 'unknown', 0.0
    
    def add_training_data(self, features, label):
        """Add training example and retrain"""
        self.training_data.append(features)
        self.training_labels.append(label)
        
        if len(self.training_data) >= 5:
            self.train_model()
    
    def train_model(self):
        """Train neural network"""
        try:
            X = np.array(self.training_data)
            y = np.array(self.training_labels)
            
            self.scaler.fit(X)
            X_scaled = self.scaler.transform(X)
            
            self.model.fit(X_scaled, y)
            self.is_trained = True
            self.save_model()
            
            print(f"🧠 AI trained with {len(self.training_data)} examples")
        except Exception as e:
            print(f"Training error: {e}")
    
    def save_model(self):
        """Save model"""
        try:
            data = {
                'model': self.model,
                'scaler': self.scaler,
                'training_data': self.training_data,
                'training_labels': self.training_labels,
                'is_trained': self.is_trained
            }
            with open('mudra_ai.pkl', 'wb') as f:
                pickle.dump(data, f)
        except:
            pass
    
    def load_model(self):
        """Load model"""
        try:
            if os.path.exists('mudra_ai.pkl'):
                with open('mudra_ai.pkl', 'rb') as f:
                    data = pickle.load(f)
                    self.model = data['model']
                    self.scaler = data['scaler']
                    self.training_data = data['training_data']
                    self.training_labels = data['training_labels']
                    self.is_trained = data['is_trained']
                print(f"🧠 Loaded AI with {len(self.training_data)} examples")
        except:
            pass
    
    def type_char(self, char):
        """Type character"""
        if char == 'BACKSPACE':
            self.kb.press(Key.backspace)
            self.kb.release(Key.backspace)
        elif char == ' ':
            self.kb.press(Key.space)
            self.kb.release(Key.space)
        else:
            self.kb.press(char)
            self.kb.release(char)
    
    def process_sequence(self):
        """Process gesture sequence"""
        if not self.current_sequence:
            return
        
        gesture_name, confidence = self.classify_gesture(self.current_sequence)
        
        print(f"\n🎯 Detected: {gesture_name} (confidence: {confidence:.2f})")
        
        if gesture_name in self.gesture_labels:
            predicted_letter = self.gesture_labels[gesture_name]
            print(f"📝 Predicted: '{predicted_letter}'")
            
            # Get feedback
            feedback = input("Correct? (y/n/letter): ").strip().lower()
            
            features = self.extract_features(self.current_sequence)
            
            if feedback == 'y':
                # Correct prediction
                self.add_training_data(features, gesture_name)
                self.type_char(predicted_letter)
                print(f"✅ Typed '{predicted_letter}' - AI learned!")
            
            elif feedback == 'n':
                correct_letter = input("What letter should it be? ").strip().lower()
                if correct_letter:
                    # Find correct gesture for this letter
                    correct_gesture = None
                    for gesture, letter in self.gesture_labels.items():
                        if letter.lower() == correct_letter:
                            correct_gesture = gesture
                            break
                    
                    if correct_gesture:
                        self.add_training_data(features, correct_gesture)
                        self.type_char(correct_letter)
                        print(f"✅ Corrected to '{correct_letter}' - AI learned!")
                    else:
                        print("❌ Letter not in gesture set")
            
            elif len(feedback) == 1:
                # Direct letter input
                correct_gesture = None
                for gesture, letter in self.gesture_labels.items():
                    if letter.lower() == feedback:
                        correct_gesture = gesture
                        break
                
                if correct_gesture:
                    self.add_training_data(features, correct_gesture)
                    self.type_char(feedback)
                    print(f"✅ Learned '{feedback}' - AI updated!")
        else:
            print("❓ Unknown gesture")
        
        self.current_sequence = []
    
    def on_key_press(self, key):
        """Handle key presses"""
        current_time = time.time()
        
        # Debounce
        if key == self.last_key and current_time - self.last_key_time < self.debounce_delay:
            return
        
        self.last_key = key
        self.last_key_time = current_time
        
        # Map keys
        key_name = None
        if key == Key.right:
            key_name = 'right'
        elif key == Key.left:
            key_name = 'left'
        elif key == Key.up:
            key_name = 'up'
        elif key == Key.down:
            key_name = 'down'
        elif key == Key.enter:
            key_name = 'enter'
        elif key == Key.f2:
            key_name = 'f2'
        elif key == Key.f3:
            key_name = 'f3'
        elif key == Key.esc:
            print("\n👋 Exiting...")
            self.save_model()
            return False
        
        if key_name:
            # Start or continue sequence
            if not self.current_sequence:
                self.sequence_start_time = current_time
                print(f"\n🎮 Recording gesture... ({key_name})")
            else:
                print(f"   + {key_name}")
            
            self.current_sequence.append({
                'key': key_name,
                'time': current_time
            })
    
    def run(self):
        """Start AI system"""
        print("🤖 MUDRA AI LEARNING SYSTEM")
        print("Console-based - no GUI errors!")
        print("\n=== NEURAL NETWORK ===")
        print("• 2 hidden layers (50-25 neurons)")
        print("• 10 extracted features per gesture")
        print("• Learns from your corrections")
        print(f"• Current training examples: {len(self.training_data)}")
        
        print("\n=== GESTURES ===")
        print("PINCH+RIGHT → e    PINCH+LEFT → t    PINCH+UP → a")
        print("PINCH+DOWN → o     DOUBLE TAP → i")
        print("F2 (twist) → space    F3 (double-twist) → backspace")
        print("F2+direction → n,s,h,r,d")
        print("F3+direction → l,c,u,m,w")
        
        print("\n=== HOW TO USE ===")
        print("1. Make gesture → AI detects and predicts")
        print("2. Type 'y' if correct, 'n' if wrong")
        print("3. If wrong, type the correct letter")
        print("4. AI learns and improves!")
        print("5. ESC to exit")
        
        print("\n🎯 Ready! Make a gesture...")
        
        with KeyboardListener(on_press=self.on_key_press) as listener:
            try:
                while True:
                    # Check for sequence timeout
                    if (self.current_sequence and 
                        time.time() - self.sequence_start_time > self.sequence_timeout):
                        self.process_sequence()
                    
                    time.sleep(0.1)
            except KeyboardInterrupt:
                print("\n👋 Stopped")
            finally:
                self.save_model()

if __name__ == "__main__":
    app = MudraAI()
    app.run()