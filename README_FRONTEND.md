# HTML Frontend - Stock Investment Recommendations

A modern, interactive HTML/CSS/JavaScript frontend for the Stock Investment Recommendations system.

## Features

- 🎨 **Modern Design**: Beautiful gradient UI with smooth animations
- 📊 **Interactive Dashboard**: Real-time stock recommendations with visual cards
- ⚡ **Fast & Responsive**: Optimized for all screen sizes
- 🎯 **User-Friendly**: Intuitive controls and clear visual feedback
- 📈 **Live Data**: Connects to FastAPI backend for real-time predictions

## Running the HTML Frontend

### Option 1: Using Python HTTP Server (Recommended)

1. **Make sure your API server is running:**
   ```powershell
   cd C:\Users\hamza\Desktop\ML_Proj
   .\venv\Scripts\python.exe -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start the frontend server:**
   ```powershell
   cd C:\Users\hamza\Desktop\ML_Proj\frontend
   ..\venv\Scripts\python.exe server.py
   ```

3. **Open your browser:**
   - The server will automatically open `http://localhost:8080`
   - Or manually navigate to `http://localhost:8080`

### Option 2: Using Python's Built-in Server

```powershell
cd C:\Users\hamza\Desktop\ML_Proj\frontend
python -m http.server 8080
```

Then open `http://localhost:8080` in your browser.

### Option 3: Open Directly in Browser

You can also open `frontend/index.html` directly in your browser, but you may need to:
- Update the API URL in `script.js` if your API is on a different address
- Handle CORS issues (the server.py method handles this automatically)

## Configuration

To change the API URL, edit `frontend/script.js`:

```javascript
const API_BASE_URL = 'http://192.168.0.202:8000';  // Change this to your API URL
```

## File Structure

```
frontend/
├── index.html      # Main HTML file
├── styles.css      # All styling
├── script.js       # JavaScript functionality
└── server.py       # Simple HTTP server
```

## Features Overview

### Control Panel
- **Number of Stocks Slider**: Choose how many stocks to analyze (5-30)
- **Custom Symbols Input**: Enter specific stock symbols (optional)
- **Time Estimate**: Shows estimated wait time based on selection
- **Get Recommendations Button**: Fetches and displays results

### Results Display
- **Top 3 Cards**: Beautiful gradient cards showing top opportunities
- **Full Table**: Detailed table with all recommendations
- **Ranking**: Stocks ranked by predicted price increase
- **Visual Indicators**: Color-coded changes (green for positive, red for negative)

### Status Indicators
- **API Status**: Shows connection status to backend
- **Loading Animation**: Progress bar and spinner during data fetch
- **Error Messages**: Clear error display if something goes wrong

## Browser Compatibility

Works on all modern browsers:
- Chrome/Edge (recommended)
- Firefox
- Safari
- Opera

## Notes

- The frontend connects to the FastAPI backend at the configured URL
- Make sure CORS is enabled on your API (FastAPI handles this by default)
- For best results, use the Python server method to avoid CORS issues


