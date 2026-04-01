# 🚨 Silent Alarm

## Problem Statement
Human monitoring of CCTV security feeds in large venues (hostels, hospitals, lobbies) is exhausting, expensive, and error-prone. When a crisis occurs, seconds matter. Traditional systems rely entirely on an operator happening to look at the right screen at the right time, causing critical delays in dispatching help. Standard AI systems attempt to solve this by blindly identifying objects (like a knife), which leads to massive false-positive fatigue when someone is simply eating lunch.

## Project Description
**Silent Alarm** upgrades existing "dumb" security cameras and webcams into active, real-time crisis response units by detecting **behavioral intent**, not just objects. 

Our pipeline uses a custom-built OpenCV **"Motion Gate"** that physically filters out static video frames. The heavy AI only wakes up when significant movement is detected, **reducing API costs and bandwidth by over 90%**. When the gate triggers, the frame undergoes behavioral analysis. If a critical threat is verified (e.g. tracking a weapon being raised aggressively or someone collapsing), the system instantly hijacks the operator's live dashboard with a massive, flashing red **CRISIS DETECTED** banner, an exact bounding box on the live stream, and immediate, 1-sentence action steps so staff can respond without confusion.

---

## Google AI Usage
### Tools / Models Used
- **Google Gemini 1.5 Flash (Vision)**
- Google Generative AI Python SDK

### How Google AI Was Used
Gemini 1.5 Flash serves as the core real-time behavioral intent engine. 
When the physical OpenCV motion gate is triggered, the raw video frame is encoded to base64, stamped with spatial context (e.g. *"[LIVE SECURITY FEED] Camera: Indoor Corridor"*), and sent asynchronously to Gemini. 

We used highly constrained prompting to mandate a strict JSON response. Gemini analyzes the pixel data in real-time not just for objects, but for intent (e.g. evaluating if a knife is idle vs. being brandished as a threat), assigns a confidence score, provides a 1-sentence justification, and synthesizes a recommended action for the operators. **Flash** was chosen specifically because sub-second latency is mandatory for emergency systems. To ensure enterprise reliability, the system strictly requires multi-frame AI consensus before escalating to a Critical alarm, completely eliminating flickering false positives.

---

## Proof of Google AI Usage
*(Attach screenshots of the Gemini API dashboard or code execution in a `/proof` folder here)*

![AI Proof](./proof/Screenshot 2026-04-01 070705.png)

---

## Screenshots 
*(Add project screenshots here)*

![Dashboard Normal State](./assets/screenshot1.png)  
![Dashboard Crisis Detected with Bounding Box](./assets/screenshot2.png)

---

## Demo Video
*(Upload your demo video to Google Drive and paste the shareable link here - max 3 minutes).*
[Watch Demo](#)

---

## Installation Steps

```bash
# Clone the repository
git clone <your-repo-link>

# Go to project folder
cd silent-alarm

# Create a virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate

# Install dependencies (FastAPI, OpenCV, Gemini API SDK)
pip install -r requirements.txt

# Create your .env file
echo "GEMINI_API_KEY=your_api_key_here" > .env

# Run the live webcam backend server
uvicorn webcam_server:app --port 8000
```
**(Then open `http://127.0.0.1:8000` in your web browser to view the live AI dashboard!)**
