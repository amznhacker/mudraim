#!/usr/bin/env python3
"""
Mudra AI Learning System - Neural Network Gesture Recognition
"""

import subprocess
import sys
import time
import tkinter as tk
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

class MudraAISystem:
    def __init__(self):
        self.kb = keyboard.Controller()
        
        # Gesture mappings
        self.gesture_labels = {
            'pinch_right': 'e',
            'pinch_left': 't', 
            'pinch_up': 'a',
            'pinch_down': 'o',
            'double_tap': 'i',
            'twist': 'SPACE',
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
            hidden_layer_sizes=(100, 50, 25),  # 3 hidden layers
            activation='relu',
            solver='adam',
            learning_rate='adaptive',
            max_iter=1000,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        
        # Gesture data collection
        self.gesture_buffer = deque(maxlen=10)  # Last 10 key events
        self.current_sequence = []
        self.sequence_start_time = 0
        self.sequence_timeout = 2.0
        
        # Training data
        self.training_data = []
        self.training_labels = []
        
        # State
        self.waiting_for_feedback = False
        self.last_prediction = None
        self.last_features = None
        
        # Hardware debouncing
        self.last_key = None
        self.last_key_time = 0
        self.debounce_delay = 0.1
        
        # Load existing model
        self.load_model()
        
        self.create_ui()
    
    def extract_features(self, key_sequence):
        """Extract features from key sequence for ML"""
        if not key_sequence:
            return np.zeros(20)  # 20 features
        
        features = []
        
        # Basic sequence info
        features.append(len(key_sequence))  # Sequence length
        
        # Key types (one-hot encoded)
        key_types = {'right': 0, 'left': 0, 'up': 0, 'down': 0, 'enter': 0, 'f2': 0, 'f3': 0}
        for key_info in key_sequence:
            key_name = key_info['key']
            if key_name in key_types:
                key_types[key_name] += 1
        
        features.extend(key_types.values())  # 7 features
        
        # Timing features
        if len(key_sequence) > 1:
            timings = [key_sequence[i+1]['time'] - key_sequence[i]['time'] 
                      for i in range(len(key_sequence)-1)]
            features.append(np.mean(timings))  # Average timing
            features.append(np.std(timings) if len(timings) > 1 else 0)  # Timing variance
            features.append(max(timings))  # Max gap
            features.append(min(timings))  # Min gap
        else:
            features.extend([0, 0, 0, 0])
        
        # Sequence patterns (bigrams)
        bigrams = {'f2_right': 0, 'f2_left': 0, 'f2_up': 0, 'f2_down': 0, 'f2_enter': 0,
                  'f3_right': 0, 'f3_left': 0, 'f3_up': 0, 'f3_down': 0, 'f3_enter': 0}
        
        for i in range(len(key_sequence) - 1):
            bigram = f"{key_sequence[i]['key']}_{key_sequence[i+1]['key']}"
            if bigram in bigrams:
                bigrams[bigram] += 1
        
        features.extend(bigrams.values())  # 10 features
        
        # Pad or truncate to exactly 20 features
        features = features[:20]
        while len(features) < 20:
            features.append(0)
        
        return np.array(features)
    
    def classify_gesture(self, key_sequence):
        """Use ML to classify gesture"""
        features = self.extract_features(key_sequence)
        
        if not self.is_trained or len(self.training_data) < 10:
            # Fallback to rule-based classification
            return self.rule_based_classify(key_sequence)
        
        try:
            # Scale features
            features_scaled = self.scaler.transform([features])
            
            # Predict
            prediction = self.model.predict(features_scaled)[0]
            confidence = max(self.model.predict_proba(features_scaled)[0])
            
            return prediction, confidence
        except:
            return self.rule_based_classify(key_sequence)
    
    def rule_based_classify(self, key_sequence):
        """Fallback rule-based classification"""
        if not key_sequence:
            return 'unknown', 0.0
        
        # Simple rules for initial classification
        if len(key_sequence) == 1:
            key_name = key_sequence[0]['key']
            if key_name == 'right':
                return 'pinch_right', 0.7
            elif key_name == 'left':
                return 'pinch_left', 0.7
            elif key_name == 'up':
                return 'pinch_up', 0.7
            elif key_name == 'down':
                return 'pinch_down', 0.7
            elif key_name == 'enter':
                return 'double_tap', 0.7
            elif key_name == 'f2':
                return 'twist', 0.7
            elif key_name == 'f3':
                return 'double_twist', 0.7
        
        elif len(key_sequence) == 2:
            first, second = key_sequence[0]['key'], key_sequence[1]['key']
            if first == 'f2':
                return f'twist_pinch_{second}', 0.6
            elif first == 'f3':
                return f'double_twist_pinch_{second}', 0.6
        
        return 'unknown', 0.0
    
    def add_training_data(self, features, label):
        """Add training example"""
        self.training_data.append(features)
        self.training_labels.append(label)
        
        # Retrain if we have enough data
        if len(self.training_data) >= 10:
            self.train_model()
    
    def train_model(self):
        """Train the neural network"""
        if len(self.training_data) < 5:
            return
        
        try:
            X = np.array(self.training_data)
            y = np.array(self.training_labels)
            
            # Scale features
            self.scaler.fit(X)
            X_scaled = self.scaler.transform(X)
            
            # Train model
            self.model.fit(X_scaled, y)
            self.is_trained = True
            
            # Save model
            self.save_model()
            
            print(f"Model trained with {len(self.training_data)} examples")
        except Exception as e:
            print(f"Training error: {e}")
    
    def save_model(self):
        """Save trained model"""
        try:
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'training_data': self.training_data,
                'training_labels': self.training_labels,
                'is_trained': self.is_trained
            }
            with open('mudra_ai_model.pkl', 'wb') as f:
                pickle.dump(model_data, f)
        except Exception as e:
            print(f"Save error: {e}")
    
    def load_model(self):
        """Load trained model"""
        try:
            if os.path.exists('mudra_ai_model.pkl'):
                with open('mudra_ai_model.pkl', 'rb') as f:
                    model_data = pickle.load(f)
                    self.model = model_data['model']
                    self.scaler = model_data['scaler']
                    self.training_data = model_data['training_data']
                    self.training_labels = model_data['training_labels']
                    self.is_trained = model_data['is_trained']
                print(f"Loaded model with {len(self.training_data)} training examples")
        except Exception as e:
            print(f"Load error: {e}")
    
    def create_ui(self):
        """Create AI learning UI"""
        self.root = tk.Tk()
        self.root.title("🤖 Mudra AI")
        self.root.geometry("350x300")
        self.root.configure(bg='#1a1a2e')
        self.root.attributes("-topmost", True)
        
        # Title
        tk.Label(self.root, text="🤖 Mudra AI Learning", 
                font=('Arial', 14, 'bold'), 
                fg='#00ff41', bg='#1a1a2e').pack(pady=5)
        
        # Status
        self.status_label = tk.Label(self.root, text="Neural Network Ready", 
                                   font=('Arial', 10), 
                                   fg='#ffffff', bg='#1a1a2e')
        self.status_label.pack(pady=5)
        
        # Detected gesture
        tk.Label(self.root, text="Detected Gesture:", 
                font=('Arial', 9), fg='#ffffff', bg='#1a1a2e').pack()
        self.detected_label = tk.Label(self.root, text="", 
                                     font=('Arial', 11, 'bold'), 
                                     fg='#00bfff', bg='#1a1a2e')
        self.detected_label.pack(pady=2)
        
        # AI Prediction
        tk.Label(self.root, text="AI Prediction:", 
                font=('Arial', 9), fg='#ffffff', bg='#1a1a2e').pack()
        self.prediction_label = tk.Label(self.root, text="", 
                                       font=('Arial', 16, 'bold'), 
                                       fg='#ff6b6b', bg='#1a1a2e')
        self.prediction_label.pack(pady=2)
        
        # Confidence
        self.confidence_label = tk.Label(self.root, text="", 
                                       font=('Arial', 9), 
                                       fg='#ffd93d', bg='#1a1a2e')
        self.confidence_label.pack(pady=2)
        
        # Feedback buttons
        self.feedback_frame = tk.Frame(self.root, bg='#1a1a2e')
        
        tk.Label(self.feedback_frame, text="Is this correct?", 
                font=('Arial', 10), fg='#ffffff', bg='#1a1a2e').pack(pady=2)
        
        button_frame = tk.Frame(self.feedback_frame, bg='#1a1a2e')
        button_frame.pack()
        
        tk.Button(button_frame, text="✓ CORRECT", command=self.feedback_correct,
                 font=('Arial', 9), bg='#4ecdc4', fg='white').pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="✗ WRONG", command=self.feedback_wrong,
                 font=('Arial', 9), bg='#ff6b6b', fg='white').pack(side=tk.LEFT, padx=5)
        
        # Correction entry
        self.correction_frame = tk.Frame(self.root, bg='#1a1a2e')
        
        tk.Label(self.correction_frame, text="Correct letter:", 
                font=('Arial', 9), fg='#ffffff', bg='#1a1a2e').pack()
        
        self.correction_entry = tk.Entry(self.correction_frame, width=5, 
                                       font=('Arial', 14), justify='center')
        self.correction_entry.pack(pady=2)
        
        tk.Button(self.correction_frame, text="LEARN", command=self.learn_correction,
                 font=('Arial', 9), bg='#6c5ce7', fg='white').pack(pady=2)
        
        # AI Stats
        self.stats_label = tk.Label(self.root, text="Training examples: 0", 
                                  font=('Arial', 8), 
                                  fg='#a0a0a0', bg='#1a1a2e')
        self.stats_label.pack(pady=5)
        
        # Controls
        control_frame = tk.Frame(self.root, bg='#1a1a2e')
        control_frame.pack(pady=5)
        
        tk.Button(control_frame, text="Reset AI", command=self.reset_ai,
                 font=('Arial', 8), bg='#fd79a8').pack(side=tk.LEFT, padx=2)
        
        tk.Button(control_frame, text="Exit", command=self.exit_app,
                 font=('Arial', 8), bg='#636e72').pack(side=tk.LEFT, padx=2)
        
        # Start keyboard listener
        self.keyboard_listener = KeyboardListener(on_press=self.on_key_press)
        self.keyboard_listener.start()
        
        # Update loop
        self.update_display()
    
    def update_display(self):
        """Update display"""
        # Check for sequence timeout
        if (self.current_sequence and 
            time.time() - self.sequence_start_time > self.sequence_timeout):
            
            # Process the sequence
            gesture_name, confidence = self.classify_gesture(self.current_sequence)
            
            self.detected_label.config(text=f"Sequence: {len(self.current_sequence)} keys")
            
            if gesture_name in self.gesture_labels:
                predicted_letter = self.gesture_labels[gesture_name]
                self.prediction_label.config(text=predicted_letter)
                self.confidence_label.config(text=f"Confidence: {confidence:.2f}")
                
                self.last_prediction = (gesture_name, predicted_letter)
                self.last_features = self.extract_features(self.current_sequence)
                
                # Show feedback
                self.waiting_for_feedback = True
                self.feedback_frame.pack(pady=5)
                self.status_label.config(text="Please provide feedback!")
            else:
                self.prediction_label.config(text="Unknown")
                self.status_label.config(text="Unknown gesture - try again")
            
            self.current_sequence = []
        
        # Update stats
        self.stats_label.config(text=f"Training examples: {len(self.training_data)}")
        
        self.root.after(100, self.update_display)
    
    def feedback_correct(self):
        """AI prediction was correct"""
        if self.last_prediction and self.last_features is not None:
            gesture_name, letter = self.last_prediction
            
            # Add positive training example
            self.add_training_data(self.last_features, gesture_name)
            
            # Type the letter
            self.type_char(letter)
            
            self.hide_feedback()
            self.status_label.config(text=f"AI learned! Typed '{letter}'")
    
    def feedback_wrong(self):
        """AI prediction was wrong"""
        self.hide_feedback()
        self.correction_frame.pack(pady=5)
        self.correction_entry.focus()
        self.status_label.config(text="Enter correct letter:")
    
    def learn_correction(self):
        """Learn from correction"""
        correct_letter = self.correction_entry.get().strip().lower()
        if correct_letter and self.last_features is not None:
            
            # Find the gesture that should produce this letter
            correct_gesture = None
            for gesture, letter in self.gesture_labels.items():
                if letter.lower() == correct_letter:
                    correct_gesture = gesture
                    break
            
            if correct_gesture:
                # Add corrected training example
                self.add_training_data(self.last_features, correct_gesture)
                
                # Type the correct letter
                self.type_char(correct_letter)
                
                self.hide_correction()
                self.status_label.config(text=f"AI corrected! Learned '{correct_letter}'")
            else:
                self.status_label.config(text="Letter not in gesture set")
    
    def hide_feedback(self):
        """Hide feedback interface"""
        self.feedback_frame.pack_forget()
        self.waiting_for_feedback = False
    
    def hide_correction(self):
        """Hide correction interface"""
        self.correction_frame.pack_forget()
        self.correction_entry.delete(0, tk.END)
    
    def type_char(self, char):
        """Type character"""
        if char == 'SPACE':
            self.kb.press(Key.space)
            self.kb.release(Key.space)
        elif char == 'BACKSPACE':
            self.kb.press(Key.backspace)
            self.kb.release(Key.backspace)
        else:
            self.kb.press(char)
            self.kb.release(char)
    
    def reset_ai(self):
        """Reset AI model"""
        self.training_data = []
        self.training_labels = []
        self.is_trained = False
        self.model = MLPClassifier(
            hidden_layer_sizes=(100, 50, 25),
            activation='relu',
            solver='adam',
            learning_rate='adaptive',
            max_iter=1000,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.status_label.config(text="AI reset - ready to learn!")
    
    def exit_app(self):
        """Exit app"""
        self.save_model()
        self.keyboard_listener.stop()
        self.root.quit()
    
    def on_key_press(self, key):
        """Handle key presses"""
        current_time = time.time()
        
        # Skip if waiting for feedback
        if self.waiting_for_feedback:
            return
        
        # Debounce
        if key == self.last_key and current_time - self.last_key_time < self.debounce_delay:
            return
        
        self.last_key = key
        self.last_key_time = current_time
        
        # Convert key to name
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
            self.exit_app()
            return
        
        if key_name:
            # Add to current sequence
            if not self.current_sequence:
                self.sequence_start_time = current_time
            
            self.current_sequence.append({
                'key': key_name,
                'time': current_time
            })
            
            self.status_label.config(text=f"Recording gesture... ({len(self.current_sequence)} keys)")
    
    def run(self):
        """Start AI system"""
        print("🤖 MUDRA AI LEARNING SYSTEM")
        print("Powered by Neural Networks on your Alienware!")
        print("\n=== AI FEATURES ===")
        print("• 3-layer neural network (100-50-25 neurons)")
        print("• 20 extracted features per gesture")
        print("• Adaptive learning from your feedback")
        print("• Persistent model storage")
        print("\n=== HOW IT WORKS ===")
        print("1. Make gesture sequences")
        print("2. AI analyzes timing, patterns, sequences")
        print("3. Provides prediction with confidence")
        print("4. You correct it, AI learns and improves")
        print("\nAI interface opening...")
        
        try:
            self.root.mainloop()
        except Exception as e:
            print(f"Error: {e}")
        finally:
            if hasattr(self, 'keyboard_listener'):
                self.keyboard_listener.stop()

if __name__ == "__main__":
    app = MudraAISystem()
    app.run()