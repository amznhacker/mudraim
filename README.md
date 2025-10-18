# 🎯 Mudra - Gesture Control System

Complete mouse and keyboard control using hand gestures.

## 🚀 Quick Start

**One command to run everything:**

```bash
python3 mudra.py
```

That's it! The system will:
- Auto-install dependencies
- Set up permissions
- Start gesture control
- Show you how to use it

## 📋 Basic Usage

### Mouse Mode (Default)
- `tap` or `pinch` - Left click
- `rtap` - Right click  
- `move <x> <y>` - Move cursor
- `scroll up/down` - Scroll page
- `twist` - Switch to typing mode
- `dtwist` - Middle click

### Typing Mode
- `tap <0-8>` - Type character at position
- `rtap` - Backspace
- `twist` - Switch back to mouse mode
- `dtwist` - Switch layers (Letters → Numbers → Symbols)
- `mouse` - Back to mouse mode

### Training & Help
- `train` - Quick typing trainer
- `test` - Speed test
- `layout` - Show character positions
- `help` - Show all commands

## 🔹 Gesture Mapping

**Letters Layer (0):**
```
0:a  1:b  2:c
3:d  4:e  5:f  
6:g  7:h  8:i
```

**Numbers Layer (1):**
```
0:1  1:2  2:3
3:4  4:5  5:6
6:7  7:8  8:9
```

**Symbols Layer (2):**
```
0:!  1:@  2:#
3:$  4:%  5:^
6:&  7:*  8:(
```

## 🎯 Example Session

```bash
$ python3 mudra.py
🎯 MUDRA - Gesture Control System
✓ Mudra system ready!

[MOUSE]> move 500 300     # Move cursor
[MOUSE]> tap              # Click
[MOUSE]> twist            # Enter typing mode
[TYPING]> tap 7           # Type 'h'
[TYPING]> tap 4           # Type 'e'  
[TYPING]> tap 5           # Type 'l'
[TYPING]> tap 5           # Type 'l'
[TYPING]> tap 8           # Type 'o'
[TYPING]> dtwist          # Switch to Numbers layer
```

## 🖥️ GUI Interface

For visual testing and debugging:

```bash
python3 mudra_gui.py
```

Features:
- Visual character layout with clickable buttons
- Real-time mode and layer display
- Mouse position controls
- Activity log for debugging
- One-click testing of all functions

---

**Ready to control your computer with gestures?**
- Command line: `python3 mudra.py`
- Visual interface: `python3 mudra_gui.py`