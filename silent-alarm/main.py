"""
Silent Alarm – Main Pipeline
  Video → Frame Sampling → Motion Gate → Gemini AI → Alert
"""

import cv2
import time
import sys

from motion_detector import detect_motion
from gemini_analyzer import analyze_frame
from alert_system import trigger_alert, print_info
from config import FRAME_INTERVAL, MOTION_THRESHOLD

# ── Choose your video ────────────────────────────────────────────────────────
VIDEOS = {
    "1": ("sample_videos/normal.mp4",      "Normal Lobby Footage"),
    "2": ("sample_videos/fire.mp4",        "Fire in Kitchen"),
    "3": ("sample_videos/heartattack.mp4", "Heart Attack in Lobby"),
}

print("\n  Select video to analyse:")
for key, (_, label) in VIDEOS.items():
    print(f"    [{key}] {label}")

choice = input("\n  Enter 1 / 2 / 3: ").strip()
VIDEO_PATH, VIDEO_LABEL = VIDEOS.get(choice, ("sample_videos/normal.mp4", "Normal"))
print(f"\n  ▶ Running: {VIDEO_LABEL}\n")

# ── Open capture ─────────────────────────────────────────────────────────────
cap = cv2.VideoCapture(VIDEO_PATH)

if not cap.isOpened():
    print(f"[ERROR] Cannot open video source: {VIDEO_PATH}")
    sys.exit(1)

fps = cap.get(cv2.CAP_PROP_FPS) or 30
frame_skip = max(1, int(fps * FRAME_INTERVAL))   # frames to jump per interval

print("=" * 50)
print("  🔒 Silent Alarm – AI Threat Detection Pipeline")
print("=" * 50)
print(f"  Source          : {VIDEO_PATH}")
print(f"  Frame interval  : {FRAME_INTERVAL}s  (~{frame_skip} frames)")
print(f"  Motion threshold: {MOTION_THRESHOLD}")
print("=" * 50 + "\n")

ret, prev_frame = cap.read()
if not ret:
    print("[ERROR] Could not read first frame from video.")
    cap.release()
    sys.exit(1)

frame_count = 0
analyzed_count = 0
alert_count = 0

try:
    while cap.isOpened():
        # Skip frames to respect FRAME_INTERVAL without sleeping
        cap.set(cv2.CAP_PROP_POS_FRAMES, cap.get(cv2.CAP_PROP_POS_FRAMES) + frame_skip - 1)

        ret, frame = cap.read()
        if not ret:
            print("\n[INFO] End of video stream. Pipeline finished.")
            break

        frame_count += 1
        motion, score = detect_motion(prev_frame, frame, MOTION_THRESHOLD)

        print(f"[Frame {frame_count:>4}] Motion score: {score:>8,.0f}", end="")

        if motion:
            print("  ⚡ Motion detected → AI analysis...")
            analyzed_count += 1

            result = analyze_frame(frame)
            print(f"           AI → {result}")

            if result.get("status", "").lower() == "critical":
                alert_count += 1
                trigger_alert(result)
            else:
                print_info(result)
        else:
            print("  — No motion")

        prev_frame = frame

except KeyboardInterrupt:
    print("\n[INFO] Interrupted by user.")

finally:
    cap.release()
    print("\n" + "=" * 50)
    print(f"  Frames sampled : {frame_count}")
    print(f"  AI calls made  : {analyzed_count}  (motion-gated)")
    print(f"  Alerts fired   : {alert_count}")
    print("=" * 50)
