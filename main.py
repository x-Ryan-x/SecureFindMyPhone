#!/usr/bin/env python3
import json, os, requests, time

DATA_FILE = "devices.json"
FCM_URL = "https://fcm.googleapis.com/fcm/send"

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

def ping_user(user, command):
    devices = load_devices()
    if user not in devices:
        print("User not found.")
        return
    payload = {
        "to": devices[user],
        "priority": "high",
        "data": {"command": command, "timestamp": int(time.time())}
    }
    headers = {
        "Content-Type": "application/json"
    }
    r = requests.post(FCM_URL, headers=headers, json=payload)
    print(f"FCM status {r.status_code}: {r.text}")

if __name__ == "__main__":
    print("Not intended to be run directly")
