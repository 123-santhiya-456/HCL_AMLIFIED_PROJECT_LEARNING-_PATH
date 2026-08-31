"""
api/index.py — Vercel serverless entry point for LearnPath AI FastAPI backend.
Vercel's Python runtime looks for an ASGI app exported from this file.
"""
import sys
import os

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app  # re-export the FastAPI app for Vercel
