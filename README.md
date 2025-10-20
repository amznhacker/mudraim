# 🎯 Mudra System-Wide Typing

**Type anywhere on Ubuntu with Mudra gestures!**

## 🚀 Quick Start

**1. Setup Mudra keyboard mode:**
- Double-press Mudra button → keyboard mode
- Assign: Twist → F2, Double-twist → F3

**2. Run:**
```bash
python3 mudra.py
```

**3. Type anywhere!** Browser, terminal, any app.

## 🎮 Gestures

**Single gestures (most common letters):**
- RIGHT → e
- LEFT → t  
- UP → a
- DOWN → o
- ENTER → i

**F2 combinations:**
- F2+RIGHT → n
- F2+LEFT → s
- F2+UP → h
- F2+DOWN → r
- F2+ENTER → d
- F2 alone → space

**F3 combinations:**
- F3+RIGHT → l
- F3+LEFT → c
- F3+UP → u
- F3+DOWN → m
- F3+ENTER → w
- F3 alone → backspace

## ⚡ How It Works

**System-wide:** Python script captures Mudra gestures and types letters anywhere
**Visual feedback:** Small window shows current status
**Hardware debouncing:** Prevents Mudra spam
**Always on top:** Status window stays visible

## 📝 Examples

**"the"** = LEFT + (F2+UP) + RIGHT (t-h-e)
**"hello"** = (F2+UP) + RIGHT + (F3+RIGHT) + (F3+RIGHT) + DOWN (h-e-l-l-o)

## 🔧 Testing

**Test in:**
- Browser address bar
- Terminal
- Text editor
- Any Ubuntu application

**Status window shows:**
- "Ready" → waiting for gesture
- "F2+?" → twist pressed, waiting for direction
- "→ H" → letter typed

---

**Complete gesture typing system that works everywhere on Ubuntu!**