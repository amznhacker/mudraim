# 🎯 Mudra Learning System

**Self-calibrating gesture typing that learns from your feedback!**

## 🧠 How It Works

**Machine Learning Approach:**
1. **Make a gesture** → System detects what it thinks you did
2. **System predicts** → Shows what letter it thinks you want
3. **You give feedback** → ✓ YES (correct) or ✗ NO (wrong)
4. **System learns** → Gets better at recognizing your specific gestures

## 🚀 Quick Start

**1. Setup Mudra keyboard mode:**
- Double-press Mudra button → keyboard mode
- Assign: Twist → F2, Double-twist → F3

**2. Run learning system:**
```bash
python3 mudra.py
```

**3. Train it with your gestures!**

## 🎓 Training Process

**Learning Interface:**
- **Detected:** Shows what gesture was detected
- **Predicted letter:** Shows what the system thinks you want
- **Feedback buttons:** ✓ YES or ✗ NO
- **Correction:** If wrong, type the correct letter

**Example Training Session:**
1. You do RIGHT gesture
2. System shows: "Detected: right, Predicted: e"
3. If correct → click ✓ YES (confidence increases)
4. If wrong → click ✗ NO, then type correct letter
5. System learns your specific gesture patterns

## 🔧 Adaptive Features

**Confidence System:**
- Correct feedback → increases confidence
- Wrong feedback → decreases confidence
- System adapts to your gesture style

**Pattern Storage:**
- Saves learned patterns to `mudra_learning.json`
- Remembers your corrections
- Gets more accurate over time

**Timing Calibration:**
- Learns your gesture timing
- Adapts to your Mudra band's sensitivity
- Reduces false positives

## 🎮 Supported Gestures

**Single gestures:**
- RIGHT, LEFT, UP, DOWN, ENTER

**Combo gestures:**
- F2 + direction (twist combinations)
- F3 + direction (double-twist combinations)

**Special functions:**
- F2 alone → space
- F3 alone → backspace

## 📊 Learning Data

**Automatically saves:**
- Gesture patterns
- Confidence scores
- Timing data
- Your corrections

**Reset option:** Clear all learning data to start fresh

## ⚡ Benefits

**Personalized:** Learns YOUR specific gesture style
**Adaptive:** Gets better with use
**Correctable:** Fix mistakes and teach correct mappings
**Persistent:** Remembers learning between sessions

---

**The first gesture typing system that learns and adapts to YOU!**