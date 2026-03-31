"""
Silent Alarm – Multi-Camera Monitor
  Runs all 3 videos simultaneously in threads.
  Shows a combined OpenCV window with live threat overlays.
  Press Q to quit.
"""

import cv2
import threading
import time
import numpy as np

from motion_detector import detect_motion
from gemini_analyzer import analyze_frame
from config import MOTION_THRESHOLD

# ── Camera definitions ────────────────────────────────────────────────────────
CAMERAS = [
    {"id": 0, "label": "CAM-1  Normal Lobby",     "path": "sample_videos/normal.mp4"},
    {"id": 1, "label": "CAM-2  Kitchen",           "path": "sample_videos/fire.mp4"},
    {"id": 2, "label": "CAM-3  Lobby (Medical)",   "path": "sample_videos/heartattack.mp4"},
]

FRAME_INTERVAL = 3          # seconds between AI checks per camera
DISPLAY_W, DISPLAY_H = 640, 360   # size of each camera tile

# ── Shared state (written by worker threads, read by display thread) ──────────
states = {
    cam["id"]: {
        "frame":      np.zeros((DISPLAY_H, DISPLAY_W, 3), dtype=np.uint8),
        "label":      cam["label"],
        "status":     "Initialising…",
        "threat":     "None",
        "confidence": 0,
        "action":     "",
        "critical":   False,
        "motion_score": 0,
        "flash":      0,   # countdown for red-flash effect
    }
    for cam in CAMERAS
}
lock = threading.Lock()
stop_event = threading.Event()


# ─────────────────────────────────────────────────────────────────────────────
def camera_worker(cam):
    """Thread: reads video, runs motion gate + Gemini, updates shared state."""
    cid   = cam["id"]
    path  = cam["path"]

    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        with lock:
            states[cid]["status"] = "⚠ Cannot open video"
        return

    fps        = cap.get(cv2.CAP_PROP_FPS) or 30
    frame_skip = max(1, int(fps * FRAME_INTERVAL))

    ret, prev = cap.read()
    if not ret:
        return

    while not stop_event.is_set() and cap.isOpened():
        # Skip frames to match FRAME_INTERVAL without sleeping
        pos = cap.get(cv2.CAP_PROP_POS_FRAMES)
        cap.set(cv2.CAP_PROP_POS_FRAMES, pos + frame_skip - 1)

        ret, frame = cap.read()
        if not ret:
            # Loop the video for demo
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = cap.read()
            if not ret:
                break

        resized = cv2.resize(frame, (DISPLAY_W, DISPLAY_H))
        motion, score = detect_motion(prev, frame, MOTION_THRESHOLD)

        with lock:
            states[cid]["frame"]       = resized.copy()
            states[cid]["motion_score"] = score

        if motion:
            with lock:
                states[cid]["status"] = "⚡ Analysing…"

            result    = analyze_frame(frame)
            is_crit   = result.get("status", "").lower() == "critical"
            threat    = result.get("threat_type", "None")
            conf      = int(result.get("confidence", 0))
            action    = result.get("recommended_action", "")

            with lock:
                states[cid]["status"]     = "CRITICAL" if is_crit else "Normal"
                states[cid]["threat"]     = threat
                states[cid]["confidence"] = conf
                states[cid]["action"]     = action
                states[cid]["critical"]   = is_crit
                if is_crit:
                    states[cid]["flash"]  = 6   # flash 6 frames
                print(f"[{states[cid]['label']}] {result}")
        else:
            with lock:
                states[cid]["status"] = "Normal"
                states[cid]["critical"] = False

        prev = frame

    cap.release()


# ─────────────────────────────────────────────────────────────────────────────
def draw_tile(state, flash_on):
    """Overlay status info onto a camera tile."""
    img    = state["frame"].copy()
    crit   = state["critical"]
    status = state["status"]
    threat = state["threat"]
    conf   = state["confidence"]
    action = state["action"]
    label  = state["label"]
    score  = state["motion_score"]

    # ── Background tint for critical ──────────────────────────────────────────
    if crit and flash_on:
        overlay        = img.copy()
        overlay[:, :]  = (0, 0, 180)
        img            = cv2.addWeighted(overlay, 0.35, img, 0.65, 0)

    # ── Top bar ───────────────────────────────────────────────────────────────
    bar_color = (0, 0, 200) if crit else (30, 30, 30)
    cv2.rectangle(img, (0, 0), (DISPLAY_W, 32), bar_color, -1)
    cv2.putText(img, label, (8, 22),
                cv2.FONT_HERSHEY_SIMPLEX, 0.58, (255, 255, 255), 1, cv2.LINE_AA)

    # Motion score (top-right)
    cv2.putText(img, f"motion:{score:,.0f}", (DISPLAY_W - 130, 22),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1, cv2.LINE_AA)

    # ── Alert banner (critical only) ──────────────────────────────────────────
    if crit:
        banner_y = DISPLAY_H // 2 - 30
        cv2.rectangle(img, (0, banner_y), (DISPLAY_W, banner_y + 70), (0, 0, 180), -1)
        cv2.putText(img, f"🚨 {threat.upper()} DETECTED",
                    (20, banner_y + 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(img, f"Conf: {conf}%  |  {action}",
                    (20, banner_y + 56),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 220, 100), 1, cv2.LINE_AA)

    # ── Bottom status bar ─────────────────────────────────────────────────────
    sb_color = (0, 0, 180) if crit else (20, 100, 20)
    cv2.rectangle(img, (0, DISPLAY_H - 28), (DISPLAY_W, DISPLAY_H), sb_color, -1)
    status_text = f"STATUS: {status}" + (f"  |  {threat}  {conf}%" if crit else "")
    cv2.putText(img, status_text, (8, DISPLAY_H - 9),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

    return img


# ─────────────────────────────────────────────────────────────────────────────
def main():
    print("=" * 55)
    print("  🔒 Silent Alarm – Multi-Camera Live Monitor")
    print("  Press Q in the window to quit")
    print("=" * 55)

    # Start one worker thread per camera
    threads = []
    for cam in CAMERAS:
        t = threading.Thread(target=camera_worker, args=(cam,), daemon=True)
        t.start()
        threads.append(t)

    flash_tick = 0

    while True:
        flash_tick += 1
        flash_on = (flash_tick % 4) < 2   # flicker every ~2 frames

        with lock:
            tiles = []
            for cam in CAMERAS:
                s = states[cam["id"]]
                # Decrement flash counter
                if s["flash"] > 0:
                    s["flash"] -= 1
                tile = draw_tile(s, flash_on and s["flash"] > 0)
                tiles.append(tile)

        # Combine tiles: arrange as 1 row of 3 (or 2+1 if preferred)
        # Add a thin separator between tiles
        sep = np.zeros((DISPLAY_H, 4, 3), dtype=np.uint8)
        combined = np.hstack([tiles[0], sep, tiles[1], sep, tiles[2]])

        # ── Global header bar ─────────────────────────────────────────────────
        header = np.zeros((44, combined.shape[1], 3), dtype=np.uint8)
        cv2.putText(header, "  SILENT ALARM  |  AI Threat Detection  |  Multi-Camera View",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 200, 255), 2, cv2.LINE_AA)

        # Flash header red if any camera is critical
        any_critical = any(states[c["id"]]["critical"] for c in CAMERAS)
        if any_critical and flash_on:
            header[:, :] = cv2.addWeighted(header, 0.3,
                                           np.full_like(header, (0, 0, 180)), 0.7, 0)

        display = np.vstack([header, combined])
        cv2.imshow("Silent Alarm – Multi-Camera Monitor", display)

        # Resize window to fit screen nicely
        cv2.resizeWindow("Silent Alarm – Multi-Camera Monitor",
                         display.shape[1], display.shape[0])

        if cv2.waitKey(200) & 0xFF == ord('q'):
            break

    stop_event.set()
    cv2.destroyAllWindows()
    print("\n[INFO] Monitor closed.")


if __name__ == "__main__":
    main()
