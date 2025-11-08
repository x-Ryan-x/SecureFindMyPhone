#!/usr/bin/env python3
import json, os, requests, time
import firebase_admin
from firebase_admin import credentials, messaging

DATA_FILE = "/data/devices.json"
SERVICE_ACCOUNT_FILE =  "find-my-phone-74741-55902c5fc985.json"

try:
    cred = credentials.Certificate(SERVICE_ACCOUNT_FILE)
    firebase_admin.initialize_app(cred)
except Exception as e:
    print(f"Failed to initialize Firebase: {e}")


def load_devices():
    try:
        with open(DATA_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_devices(devices):
    with open(DATA_FILE, "w") as f:
        json.dump(devices, f, indent=2)

def add_user(user, token):
    devices = load_devices()
    devices[user] = token
    save_devices(devices)
    print(f"Added/updated {user}")

def remove_user(user):
    devices = load_devices()
    devices.pop(user, None)
    save_devices(devices)
    print(f"Removed {user}")

def list_users():
    devices = load_devices()
    for user, token in devices.items():
        print(f"{user}: {token[:10]}...")

def ping_user(token, command):
    """Send FCM message to a device token"""
    try:
        message = messaging.Message(
            data={
                "command": command,
                "timestamp": str(int(time.time()))
            },
            token=token,
            android=messaging.AndroidConfig(
                priority='high',
            ),
            apns=messaging.APNSConfig(
                headers={'apns-priority': '10'},
            ),
        )
        
        response = messaging.send(message)
        return {
            "status_code": 200,
            "text": f"Successfully sent message: {response}"
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print("Not intended to be run directly")
