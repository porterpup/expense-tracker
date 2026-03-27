import sys
import os

# Ensure the ingestion_service directory is on the path so `main` can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app  # noqa: E402

handler = app
