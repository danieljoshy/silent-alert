import os
import datetime
import requests

LOG_FILE = "logs.txt"
API_URL  = "http://127.0.0.1:8000/alert"


def trigger_alert(result, camera="Unknown"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result["camera"]    = camera
    result["timestamp"] = timestamp

    print("\n" + "=" * 46)
    print("🚨🚨🚨  C R I T I C A L   A L E R T  🚨🚨🚨")
    print("=" * 46)
    print(f"  Time      : {timestamp}")
    print(f"  Camera    : {camera}")
    print(f"  Threat    : {result.get('threat_type', 'Unknown')}")
    print(f"  Confidence: {result.get('confidence', '?')}%")
    print(f"  Action    : {result.get('recommended_action', 'N/A')}")
    print("=" * 46 + "\n")

    # ── Log to file ──────────────────────────────────────────────────────────
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {result}\n")

    # ── Push to FastAPI dashboard ─────────────────────────────────────────────
    try:
        requests.post(API_URL, json=result, timeout=2)
        print("[API] Alert pushed to dashboard ✅")
    except Exception:
        print("[API] Dashboard not running – skipping push")

    # ── Windows TTS voice alert ───────────────────────────────────────────────
    threat = result.get("threat_type", "threat")
    _speak(f"Warning! {threat} detected. Immediate action required.")


def print_info(result, camera="Unknown"):
    """Print a non-critical frame summary and update dashboard to Normal."""
    print(f"  ✅ [{camera}] Status: {result.get('status')} | "
          f"Threat: {result.get('threat_type')} | "
          f"Confidence: {result.get('confidence')}%")
    try:
        requests.post(API_URL, json={**result, "camera": camera}, timeout=2)
    except Exception:
        pass


def _speak(message: str):
    safe = message.replace("'", "")
    try:
        os.system(
            f'powershell -Command "Add-Type -AssemblyName System.Speech; '
            f'(New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'{safe}\')"'
        )
    except Exception:
        pass
