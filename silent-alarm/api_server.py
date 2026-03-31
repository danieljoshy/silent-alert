"""
Silent Alarm – FastAPI Backend
  GET  /alert       → returns latest alert state
  POST /alert       → Python pipeline pushes new alert here
  GET  /history     → returns last 20 alerts
  GET  /            → serves the frontend dashboard
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from datetime import datetime
from collections import deque
import os

app = FastAPI(title="Silent Alarm API")

# ── CORS – allow the HTML frontend to call us ─────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-memory store ───────────────────────────────────────────────────────────
latest_alert = {
    "status": "Normal",
    "threat_type": "None",
    "confidence": 0,
    "recommended_action": "System online – monitoring active",
    "camera": "N/A",
    "timestamp": datetime.now().isoformat(),
}

history: deque = deque(maxlen=20)   # keep last 20 alerts


@app.get("/alert")
def get_alert():
    return latest_alert


@app.post("/alert")
def update_alert(data: dict):
    global latest_alert
    data["timestamp"] = datetime.now().isoformat()
    latest_alert = data
    if data.get("status", "").lower() == "critical":
        history.appendleft(data)
    return {"message": "Alert updated"}


@app.get("/history")
def get_history():
    return list(history)


@app.get("/")
def serve_frontend():
    frontend = os.path.join(os.path.dirname(__file__), "dashboard.html")
    return FileResponse(frontend)
