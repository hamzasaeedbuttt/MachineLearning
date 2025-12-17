# Quick Start Guide

## 🚀 One-Click Launch

Simply double-click **`LAUNCH.bat`** to start the entire application!

The launcher will:
1. ✅ Start the FastAPI backend server
2. ✅ Start the frontend web server  
3. ✅ Open your browser automatically
4. ✅ Display all connection URLs

## 📋 What Happens

When you run `LAUNCH.bat`:
- Two server windows will open (minimized)
- Your browser will automatically open to `http://localhost:8080`
- The API will be available at `http://localhost:8000`
- You can start using the application immediately!

## 🛑 To Stop the Application

Simply close the two minimized server windows:
1. **Stock API Server** window
2. **Stock Frontend Server** window

Or press `Ctrl+C` in each window to stop them gracefully.

## 🎯 First Time Setup

If this is your first time running the project:

1. Make sure you have Python installed
2. Create the virtual environment:
   ```powershell
   python -m venv venv
   ```
3. Install dependencies:
   ```powershell
   .\venv\Scripts\python.exe -m pip install -r requirements.txt
   ```
4. Train the models (if needed):
   ```powershell
   .\venv\Scripts\python.exe feature_pipeline\build_features.py
   .\venv\Scripts\python.exe training_pipeline\train_model.py
   ```

Then you can use `LAUNCH.bat` anytime!

## 💡 Tips

- The first launch may take a few seconds for servers to start
- Keep the server windows open while using the application
- You can access API documentation at `http://localhost:8000/docs`

