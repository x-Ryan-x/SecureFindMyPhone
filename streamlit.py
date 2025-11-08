import os
import json
import time
import requests
import streamlit as st

DATA_FILE = "devices.json"
FCM_URL = "https://fcm.googleapis.com/fcm/send"
SERVER_KEY = os.environ.get("FCM_SERVER_KEY")

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

def send_fcm_message(token: str, command: str):
    """Send a simple FCM data message"""
    if not SERVER_KEY:
        return {"error": "FCM_SERVER_KEY not set in environment variables."}

    payload = {
        "to": token,
        "priority": "high",
        "data": {"command": command, "timestamp": int(time.time())},
    }
    headers = {
        "Authorization": f"key={SERVER_KEY}",
        "Content-Type": "application/json",
    }
    try:
        resp = requests.post(FCM_URL, headers=headers, json=payload, timeout=10)
        return {"status_code": resp.status_code, "text": resp.text}
    except Exception as e:
        return {"error": str(e)}

# --- Streamlit UI ---
st.set_page_config(page_title="FCM Device Pinger", page_icon="📱", layout="centered")
st.title("📱 FCM Device Pinger")

devices = load_devices()

# Remove device
with st.expander("🗑️ Remove device"):
    user_to_remove = st.selectbox("Select user", list(devices.keys()) or [""])
    if st.button("Remove Selected"):
        if user_to_remove in devices:
            devices.pop(user_to_remove)
            save_devices(devices)
            st.success(f"Removed {user_to_remove}")

# Display list
st.subheader("📋 Registered Devices")

if not devices:
    st.info("No devices registered yet.")
else:
    for user, token in devices.items():
        col1, col2, col3 = st.columns([3, 5, 2])
        with col1:
            st.markdown(f"**{user}**")
        with col2:
            st.code(token[:40] + "..." if len(token) > 40 else token)
        with col3:
            if st.button("Ping", key=f"ping_{user}"):
                result = send_fcm_message(token, command="locate")
                if "error" in result:
                    st.error(result["error"])
                else:
                    st.info(f"Status {result['status_code']}: {result['text'][:200]}")

st.caption("Environment variable `FCM_SERVER_KEY` must be set before running.")
