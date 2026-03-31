import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

FRAME_INTERVAL = 3        # seconds between sampled frames
MOTION_THRESHOLD = 5000   # pixel-area threshold; lower = more sensitive
