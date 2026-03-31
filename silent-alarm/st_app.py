import streamlit as st
import cv2
import threading
import time
from datetime import datetime
from collections import deque
from motion_detector import detect_motion
from gemini_analyzer import analyze_frame
from config import MOTION_THRESHOLD

# ── App Configuration ──
st.set_page_config(page_title="Silent Alarm Command Center", page_icon="🏨", layout="wide")

# ── CSS Override for Flashing Threat Banner ──
# We use an empty container for the banner so it pushes down content when a crisis hits.
st.markdown("""
<style>
@keyframes flashRed {
    0%   { background-color: #ff1744; box-shadow: 0px 0px 30px #ff1744; }
    50%  { background-color: #d50000; box-shadow: 0px 0px 60px #d50000; }
    100% { background-color: #ff1744; box-shadow: 0px 0px 30px #ff1744; }
}
.critical-override {
    animation: flashRed 1s infinite;
    padding: 30px;
    border-radius: 12px;
    border: 3px solid #fff;
    color: white;
    text-align: center;
    margin-bottom: 25px;
}
.critical-override h1 {
    font-size: 3rem;
    font-weight: 900;
    margin-bottom: 5px;
    color: white !important;
    text-transform: uppercase;
    letter-spacing: 2px;
}
.critical-override h3 {
    font-size: 1.5rem;
    margin-bottom: 15px;
    color: #ffcccc !important;
}
.action-box {
    background-color: rgba(255,255,255,0.15);
    border-left: 5px solid #ffea00;
    padding: 15px;
    border-radius: 6px;
    font-size: 1.3rem;
    font-weight: 700;
    display: inline-block;
}
.good-status {
    background-color: rgba(0,230,118,0.1);
    border: 1px solid #00e676;
    color: #00e676;
    padding: 15px;
    border-radius: 8px;
    text-align: center;
    font-weight: 600;
    letter-spacing: 1px;
    margin-bottom: 20px;
}
.terminal-log {
    font-family: 'Consolas', monospace;
    font-size: 0.85rem;
    color: #00ff00;
    background-color: #0d1117;
    padding: 15px;
    border-radius: 8px;
    height: 300px;
    overflow-y: auto;
    border: 1px solid #30363d;
}
</style>
""", unsafe_allow_html=True)

# ── Global State (stored in session_state for Streamlit persistence) ──
if "system_active" not in st.session_state:
    st.session_state.system_active = False
if "latest_alert" not in st.session_state:
    st.session_state.latest_alert = None
if "logs" not in st.session_state:
    st.session_state.logs = deque(maxlen=30)
if "camera_frames" not in st.session_state:
    st.session_state.camera_frames = {"01": None, "02": None}

def log_activity(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.appendleft(f"[{ts}] {msg}")

# ── 1. Global Status Header ──
st.title("🏨 Silent Alarm Command Center")

# 4. Threat Alert Override Placeholder (top of page)
alert_placeholder = st.empty()

# ── 2. The Engineer’s Sidebar ──
with st.sidebar:
    st.header("⚙️ Control Panel")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ Start System", type="primary", use_container_width=True):
            st.session_state.system_active = True
            log_activity("SYSTEM BOOT: Initialising motion gates...")
            st.rerun()
    with col2:
        if st.button("🛑 Stop", type="secondary", use_container_width=True):
            st.session_state.system_active = False
            st.session_state.latest_alert = None
            log_activity("SYSTEM HALTED: All cameras disengaged.")
            st.rerun()

    st.markdown("---")
    st.subheader("🛠️ AI Calibration")
    # THE JUDGE FLEX: Expose OpenCV minimum area threshold
    sensitivity = st.slider(
        "Motion Gate Sensitivity", 
        min_value=500, max_value=8000, value=2500, step=100,
        help="Lower = more sensitive (catches fans). Higher = strictly human/large movement."
    )
    if st.button("Apply Calibration"):
        log_activity(f"CALIBRATION: Motion threshold updated to {sensitivity}")

# Render the normal status badge ONLY if there's no active alert
if not st.session_state.latest_alert:
    if st.session_state.system_active:
        st.markdown('<div class="good-status">🟢 VENUE SECURE - AI MONITORING ACTIVE</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="good-status" style="color:#aaa; border-color:#555; background:rgba(255,255,255,0.05);">⚪ SYSTEM OFFLINE - PRESS START IN SIDEBAR</div>', unsafe_allow_html=True)

# ── Trigger the Override UI if Alert exists ──
if st.session_state.latest_alert:
    alert = st.session_state.latest_alert
    header_html = f"""
    <div class="critical-override">
        <h1>🚨 CRISIS DETECTED: {alert['threat_type']} 🚨</h1>
        <h3>Location: {alert['camera']} | AI Confidence: {alert['confidence']}%</h3>
        <div class="action-box">
            ACTION REQUIRED:<br/>{alert['recommended_action']}
        </div>
    </div>
    """
    alert_placeholder.markdown(header_html, unsafe_allow_html=True)

# ── 3. The Live Monitor Grid ──
st.subheader("Live Feed Monitoring")
cam_col1, cam_col2 = st.columns(2)

with cam_col1:
    st.markdown("**Camera 01: Main Lobby** (Normal behavior)")
    vid_placeholder_1 = st.empty()
with cam_col2:
    st.markdown("**Camera 02: Kitchen Staff** (Fire test)")
    vid_placeholder_2 = st.empty()

# ── 5. AI Terminal / Activity Log ──
st.markdown("---")
with st.expander("System Logs (AI Engine Activity)", expanded=True):
    log_container = st.empty()

def update_logs_ui():
    logs_html = "<br/>".join(st.session_state.logs)
    log_container.markdown(f'<div class="terminal-log">{logs_html}</div>', unsafe_allow_html=True)

update_logs_ui()

# ── Simulation Logic (To run the videos live in Streamlit) ──
# Streamlit re-runs script top-to-bottom. To stream video smoothly without blocking the UI, 
# we read frames in a tight loop below, occasionally running the motion detector block.

if st.session_state.system_active:
    
    # We open caps here. Note: in a true production app, caps would be held in a background thread.
    cap1 = cv2.VideoCapture("sample_videos/normal.mp4")
    cap2 = cv2.VideoCapture("sample_videos/fire.mp4")
    
    ret1, prev_frame1 = cap1.read()
    ret2, prev_frame2 = cap2.read()
    
    frame_count = 0
    
    # Run the loop to simulate live footage
    while cap1.isOpened() and cap2.isOpened() and st.session_state.system_active:
        ret1, frame1 = cap1.read()
        ret2, frame2 = cap2.read()
        
        if not ret1 or not ret2:
            # loop videos for continuous demo
            cap1.set(cv2.CAP_PROP_POS_FRAMES, 0)
            cap2.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
            
        frame_count += 1
        
        # Add timestamp watermark (Live Camera feel)
        ts_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame1, f"LOBBY {ts_str}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
        cv2.putText(frame2, f"KITCHEN {ts_str}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
        
        # Update UI placeholders smoothly (convert BGR to RGB for Streamlit)
        vid_placeholder_1.image(cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB), channels="RGB", use_container_width=True)
        vid_placeholder_2.image(cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB), channels="RGB", use_container_width=True)
        
        # MOTION GATE: Only run motion check every 30 frames to simulate interval
        if frame_count % 30 == 0:
            # Check Cam 1
            motion1, _ = detect_motion(prev_frame1, frame1, sensitivity)
            if motion1:
                log_activity("Motion Gate triggered on Camera 01. Sending to Gemini API...")
                update_logs_ui()
                # Run Gemini (in a real app, this blocks UI, so we only simulate or do it fast here)
                res = analyze_frame(frame1)
                log_activity(f"Cam 01 Analysis: {res.get('status')} | {res.get('threat_type')}")
                if res.get("status", "").lower() == "critical":
                    res["camera"] = "Camera 01: Main Lobby"
                    st.session_state.latest_alert = res
                    st.rerun() # Force UI refresh to blast the red banner
            
            # Check Cam 2
            motion2, _ = detect_motion(prev_frame2, frame2, sensitivity)
            if motion2:
                log_activity("Motion Gate triggered on Camera 02. Sending to Gemini API...")
                update_logs_ui()
                res = analyze_frame(frame2)
                log_activity(f"Cam 02 Analysis: {res.get('status')} | {res.get('threat_type')}")
                if res.get("status", "").lower() == "critical":
                    res["camera"] = "Camera 02: Kitchen Staff"
                    st.session_state.latest_alert = res
                    st.rerun() # Force UI refresh to blast the red banner

            prev_frame1 = frame1
            prev_frame2 = frame2
            update_logs_ui()
            
        time.sleep(0.03) # roughly 30fps pacing
