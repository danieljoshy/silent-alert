import cv2
import base64
import json
import google.generativeai as genai
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")


def encode_image(frame):
    """Encode an OpenCV frame as a base64 JPEG string."""
    _, buffer = cv2.imencode(".jpg", frame)
    return base64.b64encode(buffer).decode("utf-8")


def analyze_frame(frame):
    """
    Send a CCTV frame to Gemini and return a structured threat assessment dict.
    Falls back to a safe 'Normal' result on any parsing error.
    """
    image_base64 = encode_image(frame)

    prompt = """
Analyze this CCTV surveillance frame and respond ONLY with valid JSON — no markdown, no extra text:

{
    "status": "Normal or Critical",
    "threat_type": "Fire, Medical, Weapon, Crowd, None",
    "confidence": "0-100",
    "recommended_action": "Clear step for staff"
}
"""

    try:
        response = model.generate_content([
            prompt,
            {"mime_type": "image/jpeg", "data": base64.b64decode(image_base64)}
        ])

        # Strip accidental markdown code fences if present
        raw = response.text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw.strip())

    except Exception as e:
        print(f"[Gemini] Parse error: {e}")
        return {
            "status": "Normal",
            "threat_type": "None",
            "confidence": "0",
            "recommended_action": "No action required"
        }
