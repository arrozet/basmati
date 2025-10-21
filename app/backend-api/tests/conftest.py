"""
Pytest configuration file
Adds parent directory to sys.path so tests can import app modules
"""
import sys
from pathlib import Path

# Add parent directory (backend-api) to Python path
backend_api_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_api_dir))
