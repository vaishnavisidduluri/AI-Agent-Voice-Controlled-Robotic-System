# =========================================================
# 🤖 AI ROBOTIC CONTROL SYSTEM - REALTIME DASHBOARD
# =========================================================
# FILE: dashboard.py
# =========================================================

import streamlit as st
import cv2
import time
from datetime import datetime

from agents.master_agent import MasterAgent

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="AI Robotic Control",
    page_icon="🤖",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown("""
<style>

html, body, [class*="css"] {
    background-color: #040B1C;
    color: white;
    font-family: 'Segoe UI', sans-serif;
}

/* REMOVE DEFAULT */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* TITLE */
.main-title {
    text-align: center;
    font-size: 42px;
    font-weight: bold;
    color: #00E5FF;
    margin-bottom: 5px;
}

.sub-title {
    text-align: center;
    color: #8b949e;
    margin-bottom: 25px;
}

/* CARD */
.card {
    background: linear-gradient(145deg, #0D1528, #111827);
    border-radius: 18px;
    padding: 20px;
    margin-bottom: 20px;
    border: 1px solid #1E293B;
    box-shadow: 0px 0px 20px rgba(0,229,255,0.08);
}

/* CARD TITLE */
.card-title {
    color: #00E5FF;
    font-size: 22px;
    font-weight: bold;
    margin-bottom: 15px;
}

/* BUTTON */
.stButton>button {
    width: 100%;
    height: 50px;
    border-radius: 12px;
    border: none;
    font-size: 16px;
    font-weight: bold;
    background: linear-gradient(90deg, #00E5FF, #007CF0);
    color: white;
}

/* TEXT INPUT */
.stTextInput>div>div>input {
    background-color: #0F172A;
    color: white;
    border-radius: 10px;
    border: 1px solid #334155;
}

/* LOGS */
.log-box {
    background-color: #0B1220;
    border-left: 4px solid #00E5FF;
    padding: 10px;
    border-radius: 8px;
    margin-bottom: 8px;
    font-size: 14px;
}

/* STATUS */
.green {
    color: #00FF99;
    font-weight: bold;
}

.red {
    color: #FF4B4B;
    font-weight: bold;
}

/* METRIC */
.metric {
    font-size: 18px;
    margin-bottom: 8px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# SESSION STATE
# =========================================================
if "agent" not in st.session_state:
    st.session_state.agent = MasterAgent()

if "running" not in st.session_state:
    st.session_state.running = False

if "logs" not in st.session_state:
    st.session_state.logs = []

if "camera" not in st.session_state:

    # -----------------------------------------------------
    # RASPBERRY PI CAMERA
    # -----------------------------------------------------
    st.session_state.camera = cv2.VideoCapture(0)

# =========================================================
# LOG FUNCTION
# =========================================================
def add_log(message):

    st.session_state.logs.insert(0, {
        "time": datetime.now().strftime("%H:%M:%S"),
        "message": message
    })

# =========================================================
# HEADER
# =========================================================
st.markdown(
    '<div class="main-title">🤖 AI ROBOTIC CONTROL SYSTEM</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">Vision • Navigation • Servo Control • IK • Grasping</div>',
    unsafe_allow_html=True
)

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title("⚙ CONTROL PANEL")

user_input = st.sidebar.text_input(
    "Command Input",
    placeholder="pick bottle"
)

start_btn = st.sidebar.button("▶ START ROBOT")
stop_btn = st.sidebar.button("⛔ STOP ROBOT")

# =========================================================
# BUTTON ACTIONS
# =========================================================
if start_btn:
    st.session_state.running = True
    add_log("🟢 Robot Started")

if stop_btn:
    st.session_state.running = False
    add_log("🔴 Robot Stopped")

# =========================================================
# MAIN LAYOUT
# =========================================================
left, right = st.columns([2.2, 1])

# =========================================================
# CAMERA FEED
# =========================================================
with left:

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown(
        '<div class="card-title">📷 LIVE CAMERA FEED</div>',
        unsafe_allow_html=True
    )

    frame_placeholder = st.empty()

    ret, frame = st.session_state.camera.read()

    if ret:

        # -------------------------------------------------
        # REALTIME OBJECT DETECTION
        # -------------------------------------------------
        try:

            detections = st.session_state.agent.vision.get_detections()

            if detections["status"] != "no_object":

                for det in detections["detections"]:

                    x1, y1, x2, y2 = det["bbox"]

                    label = det["label"]
                    conf = det["confidence"]

                    # BOUNDING BOX
                    cv2.rectangle(
                        frame,
                        (x1, y1),
                        (x2, y2),
                        (0, 255, 255),
                        2
                    )

                    # LABEL
                    cv2.putText(
                        frame,
                        f"{label} {conf:.2f}",
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0, 255, 255),
                        2
                    )

        except Exception as e:
            add_log(f"❌ Vision Error: {e}")

        # RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        frame_placeholder.image(
            frame,
            channels="RGB",
            use_container_width=True
        )

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# RIGHT SIDE
# =========================================================
with right:

    # =====================================================
    # STATUS
    # =====================================================
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown(
        '<div class="card-title">🧠 SYSTEM STATUS</div>',
        unsafe_allow_html=True
    )

    if st.session_state.running:
        st.markdown('<p class="green">🟢 ACTIVE</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="red">🔴 STOPPED</p>', unsafe_allow_html=True)

    st.write("Mode: Autonomous")
    st.write("Hardware: Raspberry Pi")
    st.write("Servos: 7")
    st.write("Camera: Pi Camera")

    st.markdown('</div>', unsafe_allow_html=True)

    # =====================================================
    # COMMAND
    # =====================================================
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown(
        '<div class="card-title">🎯 CURRENT COMMAND</div>',
        unsafe_allow_html=True
    )

    if user_input:
        st.write(user_input)
    else:
        st.write("Waiting for command...")

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# PROCESS COMMAND
# =========================================================
result = None

if st.session_state.running and user_input:

    try:

        # -------------------------------------------------
        # CONVERT TEXT → COMMAND
        # -------------------------------------------------
        words = user_input.lower().split()

        action = words[0] if len(words) > 0 else None
        obj = words[-1] if len(words) > 1 else None

        command = {
            "action": action,
            "object": obj
        }

        # -------------------------------------------------
        # MASTER AGENT EXECUTION
        # -------------------------------------------------
        result = st.session_state.agent.process_cycle(command)

        if result:

            for log in result["logs"]:
                add_log(log)

    except Exception as e:
        add_log(f"❌ Error: {e}")

# =========================================================
# LOWER SECTION
# =========================================================
col1, col2 = st.columns(2)

# =========================================================
# VISION
# =========================================================
with col1:

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown(
        '<div class="card-title">👁️ VISION + NAVIGATION</div>',
        unsafe_allow_html=True
    )

    if result:

        st.write(f"Action → {result['command']['action']}")
        st.write(f"Object → {result['command']['object']}")
        st.write(f"State → {result['state']}")
        st.write(f"Holding → {result['holding']}")

    else:
        st.info("Waiting for robot execution...")

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# SERVO EXECUTION
# =========================================================
with col2:

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown(
        '<div class="card-title">⚙️ SERVO EXECUTION</div>',
        unsafe_allow_html=True
    )

    if result:

        for log in result["logs"]:

            if "Servo" in log:
                st.write(log)

            if "Gripper" in log:
                st.write(log)

    else:
        st.info("Waiting for servo activity...")

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# LIVE LOGS
# =========================================================
st.markdown('<div class="card">', unsafe_allow_html=True)

st.markdown(
    '<div class="card-title">📜 LIVE SYSTEM LOGS</div>',
    unsafe_allow_html=True
)

for log in st.session_state.logs[:25]:

    st.markdown(f"""
    <div class="log-box">
        <b>{log['time']}</b> → {log['message']}
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# AUTO REFRESH
# =========================================================
time.sleep(0.1)
st.rerun()