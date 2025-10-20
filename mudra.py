#!/usr/bin/env python3
"""
Mudra Letter Recognition - Using $1 Unistroke Recognizer for actual letter shapes
"""

import subprocess
import sys
import time
import tkinter as tk
import math
from pynput import keyboard
from pynput.keyboard import Key, Listener as KeyboardListener

# Install pynput if needed
try:
    import pynput
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pynput"])

class DollarRecognizer:
    """Simplified $1 Unistroke Recognizer for letters"""
    
    def __init__(self):
        self.templates = self.create_letter_templates()
        self.num_points = 32  # Resample to this many points
        self.square_size = 250.0
    
    def create_letter_templates(self):
        """Create templates for common letters"""
        templates = {}
        
        # Simple letter templates (normalized point sequences)
        # These represent the shape of each letter
        templates['e'] = [(0,50), (100,50), (100,0), (50,0), (50,25), (75,25), (50,25), (50,50), (100,50), (100,100), (0,100)]
        templates['t'] = [(0,0), (100,0), (50,0), (50,100)]
        templates['a'] = [(0,100), (50,0), (100,100), (75,60), (25,60)]
        templates['o'] = [(50,0), (100,25), (100,75), (50,100), (0,75), (0,25), (50,0)]
        templates['i'] = [(50,25), (50,100), (50,0), (50,25)]
        templates['n'] = [(0,100), (0,0), (100,100)]
        templates['s'] = [(100,25), (0,25), (0,50), (100,50), (100,75), (0,75)]
        templates['h'] = [(0,0), (0,100), (0,50), (100,50), (100,0), (100,100)]
        templates['r'] = [(0,100), (0,0), (100,0), (100,50), (0,50)]
        templates['d'] = [(0,100), (0,0), (75,0), (100,25), (100,75), (75,100), (0,100)]
        templates['l'] = [(0,0), (0,100), (100,100)]
        templates['c'] = [(100,25), (0,50), (100,75)]
        
        # Normalize all templates
        for letter in templates:
            templates[letter] = self.normalize_template(templates[letter])
        
        return templates
    
    def normalize_template(self, points):
        """Normalize template points"""
        points = self.resample(points, self.num_points)
        points = self.rotate_to_zero(points)
        points = self.scale_to_square(points, self.square_size)
        points = self.translate_to_origin(points)
        return points
    
    def resample(self, points, n):
        """Resample points to n points"""
        if len(points) < 2:
            return points
            
        path_length = 0
        for i in range(1, len(points)):
            path_length += self.distance(points[i-1], points[i])
        
        interval = path_length / (n - 1)
        new_points = [points[0]]
        
        d = 0
        for i in range(1, len(points)):
            d += self.distance(points[i-1], points[i])
            while d >= interval and len(new_points) < n:
                new_points.append(points[i])
                d -= interval
        
        return new_points
    
    def distance(self, p1, p2):
        """Distance between two points"""
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
    
    def rotate_to_zero(self, points):
        """Rotate to zero angle"""
        centroid = self.centroid(points)
        angle = math.atan2(centroid[1] - points[0][1], centroid[0] - points[0][0])
        return self.rotate_by(points, -angle)
    
    def centroid(self, points):
        """Find centroid of points"""
        x = sum(p[0] for p in points) / len(points)
        y = sum(p[1] for p in points) / len(points)
        return (x, y)
    
    def rotate_by(self, points, angle):
        """Rotate points by angle"""
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        centroid = self.centroid(points)
        
        new_points = []
        for p in points:
            x = (p[0] - centroid[0]) * cos_a - (p[1] - centroid[1]) * sin_a + centroid[0]
            y = (p[0] - centroid[0]) * sin_a + (p[1] - centroid[1]) * cos_a + centroid[1]
            new_points.append((x, y))
        
        return new_points
    
    def scale_to_square(self, points, size):
        """Scale to square"""
        min_x = min(p[0] for p in points)
        max_x = max(p[0] for p in points)
        min_y = min(p[1] for p in points)
        max_y = max(p[1] for p in points)
        
        width = max_x - min_x
        height = max_y - min_y
        
        if width == 0 or height == 0:
            return points
        
        scale = size / max(width, height)
        
        new_points = []
        for p in points:
            x = p[0] * scale
            y = p[1] * scale
            new_points.append((x, y))
        
        return new_points
    
    def translate_to_origin(self, points):
        """Translate to origin"""
        centroid = self.centroid(points)
        new_points = []
        for p in points:
            x = p[0] - centroid[0]
            y = p[1] - centroid[1]
            new_points.append((x, y))
        return new_points
    
    def recognize(self, points):
        """Recognize gesture against templates"""
        if len(points) < 3:
            return None, 0
        
        # Normalize input
        points = self.normalize_template(points)
        
        best_distance = float('inf')
        best_match = None
        
        # Compare against all templates
        for letter, template in self.templates.items():
            distance = self.distance_at_best_angle(points, template)
            if distance < best_distance:
                best_distance = distance
                best_match = letter
        
        # Calculate score (lower distance = higher score)
        score = 1.0 - (best_distance / (0.5 * math.sqrt(self.square_size * self.square_size + self.square_size * self.square_size)))
        
        return best_match, score

    def distance_at_best_angle(self, points, template):
        """Find distance at best angle"""
        # Simplified - just compare directly
        if len(points) != len(template):
            return float('inf')
        
        total_distance = 0
        for i in range(len(points)):
            total_distance += self.distance(points[i], template[i])
        
        return total_distance / len(points)

class LetterRecognitionPad:
    def __init__(self):
        self.kb = keyboard.Controller()
        self.typing_mode = False
        self.recognizer = DollarRecognizer()
        
        self.current_stroke = []
        self.is_drawing = False
        
        # Create gesture pad window
        self.create_gesture_pad()
    
    def create_gesture_pad(self):
        """Create gesture pad with letter recognition"""
        self.root = tk.Tk()
        self.root.title("Mudra Letter Recognition")
        self.root.geometry("300x350+100+100")
        self.root.attributes("-topmost", True)
        self.root.configure(bg='lightblue')
        
        # Canvas for drawing letters
        self.canvas = tk.Canvas(self.root, width=280, height=200, bg='white', relief='sunken', bd=2)
        self.canvas.pack(pady=10)
        
        # Status label
        self.status_label = tk.Label(self.root, text="Mouse Mode", bg='lightblue', font=('Arial', 12, 'bold'))
        self.status_label.pack()
        
        # Recognition result
        self.result_label = tk.Label(self.root, text="Draw a letter...", bg='lightblue', font=('Arial', 10))
        self.result_label.pack()
        
        # Instructions
        instructions = tk.Label(self.root, text="F1: Toggle | Draw letter shapes in white area\nSupported: e,t,a,o,i,n,s,h,r,d,l,c", 
                              bg='lightblue', font=('Arial', 8), wraplength=280)
        instructions.pack()
        
        # Clear button
        clear_btn = tk.Button(self.root, text="Clear", command=self.clear_canvas)
        clear_btn.pack(pady=5)
        
        # Bind mouse events
        self.canvas.bind("<Button-1>", self.start_drawing)
        self.canvas.bind("<B1-Motion>", self.draw_stroke)
        self.canvas.bind("<ButtonRelease-1>", self.end_drawing)
        
        # Start keyboard listener
        self.keyboard_listener = KeyboardListener(on_press=self.on_key_press)
        self.keyboard_listener.start()
    
    def start_drawing(self, event):
        """Start drawing a letter"""
        if self.typing_mode:
            self.is_drawing = True
            self.current_stroke = [(event.x, event.y)]
            self.clear_canvas()
    
    def draw_stroke(self, event):
        """Continue drawing stroke"""
        if self.typing_mode and self.is_drawing:
            # Draw line from last point to current
            if len(self.current_stroke) > 0:
                last_point = self.current_stroke[-1]
                self.canvas.create_line(last_point[0], last_point[1], event.x, event.y, 
                                      fill='blue', width=3, capstyle=tk.ROUND)
            
            self.current_stroke.append((event.x, event.y))
    
    def end_drawing(self, event):
        """Finish drawing and recognize letter"""
        if self.typing_mode and self.is_drawing:
            self.is_drawing = False
            
            if len(self.current_stroke) > 3:
                # Recognize the letter
                letter, score = self.recognizer.recognize(self.current_stroke)
                
                if letter and score > 0.3:  # Confidence threshold
                    self.type_letter(letter)
                    self.result_label.config(text=f"Recognized: '{letter}' (confidence: {score:.2f})")
                else:
                    self.result_label.config(text="Letter not recognized - try again")
            
            self.current_stroke = []
    
    def clear_canvas(self):
        """Clear the drawing canvas"""
        self.canvas.delete("all")
    
    def type_letter(self, letter):
        """Type the recognized letter"""
        self.kb.press(letter)
        self.kb.release(letter)
    
    def on_key_press(self, key):
        """Handle keyboard input"""
        if key == Key.f1:
            self.typing_mode = not self.typing_mode
            mode = "Letter Recognition Mode" if self.typing_mode else "Mouse Mode"
            self.status_label.config(text=mode)
            
            # Change canvas color
            color = 'lightyellow' if self.typing_mode else 'white'
            self.canvas.config(bg=color)
            
            if self.typing_mode:
                self.result_label.config(text="Draw letter shapes to type!")
            else:
                self.result_label.config(text="Mouse mode - normal mouse usage")
            return
        
        if not self.typing_mode:
            return
        
        if key == Key.space:
            self.result_label.config(text="Space typed")
        elif key == Key.backspace:
            self.result_label.config(text="Backspace")
    
    def run(self):
        """Start the letter recognition pad"""
        print("🎯 MUDRA LETTER RECOGNITION")
        print("Draw actual letter shapes - powered by $1 Unistroke Recognizer!")
        print("\n=== FEATURES ===")
        print("✓ Recognizes actual letter shapes (e,t,a,o,i,n,s,h,r,d,l,c)")
        print("✓ Based on proven $1 algorithm used in many apps")
        print("✓ Confidence scoring for accurate recognition")
        print("✓ Visual feedback while drawing")
        print("\n=== USAGE ===")
        print("1. F1 → Toggle letter recognition mode")
        print("2. Draw letter shapes in the yellow area")
        print("3. Letters are typed where your cursor is")
        print("4. Clear button to erase and try again")
        print("\nLetter recognition window will open...")
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nLetter recognition stopped")
        finally:
            self.keyboard_listener.stop()

if __name__ == "__main__":
    pad = LetterRecognitionPad()
    pad.run()