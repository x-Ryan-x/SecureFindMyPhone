import os
import json
import streamlit as st
import main as m

DATA_FILE = "devices.json"


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

devices = load_devices()


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
                result = m.ping_user(token, command="locate")
                if result is None:
                    st.error("Ping failed - no response from server")
                elif "error" in result:
                    st.error(result["error"])
                else:
                    st.info(f"Status {result['status_code']}: {result['text'][:200]}")

st.caption("Environment variable `FCM_SERVER_KEY` must be set before running.")
