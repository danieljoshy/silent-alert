import os
import datetime


LOG_FILE = "logs.txt"


def trigger_alert(result):
    """Print a critical alert to the console and log it to file."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("\n" + "=" * 46)
    print("🚨🚨🚨  C R I T I C A L   A L E R T  🚨🚨🚨")
    print("=" * 46)
    print(f"  Time      : {timestamp}")
    print(f"  Threat    : {result.get('threat_type', 'Unknown')}")
    print(f"  Confidence: {result.get('confidence', '?')}%")
    print(f"  Action    : {result.get('recommended_action', 'N/A')}")
    print("=" * 46 + "\n")

    # ── Log to file ──────────────────────────────────────────────────────────
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {result}\n")

    # ── Optional: Windows toast-style voice alert via PowerShell ─────────────
    threat = result.get("threat_type", "threat")
    _speak(f"Warning! {threat} detected. Immediate action required.")


def _speak(message: str):
    """Use Windows built-in TTS (no extra install needed)."""
    safe = message.replace("'", "")   # avoid quote injection
    try:
        os.system(
            f'powershell -Command "Add-Type -AssemblyName System.Speech; '
            f'(New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'{safe}\')"'
        )
    except Exception:
        pass  # TTS is optional – never crash the pipeline


def print_info(result):
    """Print a non-critical frame summary."""
    print(f"  ✅ Status: {result.get('status')} | "
          f"Threat: {result.get('threat_type')} | "
          f"Confidence: {result.get('confidence')}%")
