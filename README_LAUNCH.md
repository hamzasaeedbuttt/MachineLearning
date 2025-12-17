# 🚀 One-Click Launch Guide

## Quick Start - Three Easy Ways

### Option 1: Double-Click LAUNCH.bat (Easiest!)
Just double-click **`LAUNCH.bat`** in the project folder. That's it!

### Option 2: Create Desktop Shortcut (Best for Daily Use)
1. Double-click **`SETUP_SHORTCUT.bat`**
2. A shortcut will appear on your desktop
3. Double-click the desktop shortcut anytime to launch!

### Option 3: Pin to Taskbar
1. Right-click on `LAUNCH.bat`
2. Select "Pin to taskbar"
3. Click the icon anytime to launch!

## What Happens When You Launch?

When you run the launcher:
1. ✅ **FastAPI Server** starts automatically (hidden window)
2. ✅ **Frontend Server** starts automatically (hidden window)
3. ✅ **Your browser opens** to the application
4. ✅ **Everything is ready** - no terminal commands needed!

The servers run in minimized windows in the background. You don't need to see them or interact with them.

## 🛑 Stopping the Application

### Easy Method:
- Press `Ctrl + Shift + Esc` to open Task Manager
- Look for Python processes
- End the processes (optional - they'll close when you close the browser)

### Alternative:
- The servers will stop automatically when you close your computer
- Or close the minimized server windows if you see them

## ⚡ First Time Setup

If this is your first time:
1. Make sure Python is installed
2. Run these commands once:
   ```powershell
   python -m venv venv
   .\venv\Scripts\python.exe -m pip install -r requirements.txt
   .\venv\Scripts\python.exe feature_pipeline\build_features.py
   .\venv\Scripts\python.exe training_pipeline\train_model.py
   ```
3. Then use `LAUNCH.bat` anytime!

## 💡 Tips

- The launcher opens your browser automatically
- Servers start in the background (you won't see terminal windows)
- Everything is automatic - just click and go!
- The shortcut on your desktop makes it super convenient

Enjoy using your Stock Investment Recommendations system! 📈

