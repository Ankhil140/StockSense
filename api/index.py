import sys
# Vercel entry point - Optimized for TFLite
import os

# Add the project root to the path so src can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.app import app

# This is required for Vercel
handler = app
