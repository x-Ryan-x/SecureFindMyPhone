import os
import json
import streamlit as st
import main as m
import traceback

DATA_FILE = "./data/devices.json"

# Cache the Firebase initialization
@st.cache_resource
def init_firebase():
    try:
        m.initialize_firebase()
        st.write("✅ Firebase initialized")
        return True
    except Exception as e:
        st.error(f"❌ Firebase initialization failed: {e}")
        st.error(traceback.format_exc())
        return False
# Utility: Load or create file
def load_devices():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)
    with open(DATA_FILE) as f:
        return json.load(f)

def save_devices(devices):
    with open(DATA_FILE, "w") as f:
        json.dump(devices, f, indent=2)

# --- Streamlit UI ---
st.set_page_config(page_title="FCM Device Pinger", page_icon="📱", layout="centered")
st.title("📱 FCM Device Pinger")

firebase_ready = init_firebase()

if not firebase_ready:
    st.stop()

devices = load_devices()

# Display list
st.subheader("📋 Registered Devices")

if not devices:
    st.info("No devices registered yet.")
else:
    for user, token in devices.items():
        col1, col2, col3, col4 = st.columns([3, 5, 2, 2])
        with col1:
            st.markdown(f"**{user}**")
        with col2:
            st.code(token[:40] + "..." if len(token) > 40 else token)
        with col3:
            if st.button("Locate", key=f"locate_{user}"):
                result = m.ping_user(token, command="locate")
                if result is None:
                    st.error("Ping failed - no response from server")
                elif "error" in result:
                    st.error(result["error"])
                else:
                    st.info(f"Status {result['status_code']}: {result['text'][:200]}")
        with col4:
            if st.button("Alarm", key=f"alarm_{user}"):
                result = m.ping_user(token, command="alarm")
                if result is None:
                    st.error("Ping failed - no response from server")
                elif "error" in result:
                    st.error(result["error"])
                else:
                    st.info(f"Status {result['status_code']}: {result['text'][:200]}")

st.caption("Environment variable `FCM_SERVER_KEY` must be set before running.")
