"""
Vercel serverless function entry point
This wraps the FastAPI app for Vercel deployment
"""
from main import app

# Export the app for Vercel
handler = app

