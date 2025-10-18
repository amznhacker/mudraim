# 🔍 Mudra Debug Mode

We're debugging your Mudra band to understand what gestures send to Ubuntu.

## 🚀 Run Debug Tool

```bash
python3 debug_mudra.py
```

## 📋 Test Each Gesture

Connect your Mudra band and perform these actions **one at a time**:

1. **Move hand** - cursor movement
2. **Pinch** - left click  
3. **Reverse tap** - right click
4. **Scroll** - up/down scroll
5. **Single twist** - ???
6. **Double twist** - ???
7. **Any other gestures**

## 📊 What We're Capturing

- Mouse movements, clicks, scrolls
- Keyboard key presses/releases  
- Timestamps for everything
- Complete event log saved to file

## 🎯 Next Steps

After testing, tell me:
- What happens when you twist?
- What shows up in the debug log?
- Any special key combinations?

Then we'll build the perfect keyboard system for your Mudra band!

---

**Press ESC to stop debugging**