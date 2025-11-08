#!/usr/bin/env python3
import json, os, requests, time
from google.oauth2 import service_account
from google.auth.transport.requests import Request

DATA_FILE = "devices.json"
SERVICE_ACCOUNT_FILE =  "service-account.json"

def get_access_token():
    """Get OAuth2 access token from service account"""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=["https://www.googleapis.com/auth/firebase.messaging"]
        )
        credentials.refresh(Request())
        return credentials.token
    except Exception as e:
        return None
    
def get_project_id():
    """Extract project ID from service account file"""
    try:
        if not os.path.exists(SERVICE_ACCOUNT_FILE):
            print(f"Service account file not found: {SERVICE_ACCOUNT_FILE}")
            return None
        
        with open(SERVICE_ACCOUNT_FILE) as f:
            service_account_info = json.load(f)
            project_id = service_account_info.get("project_id")
            
            if not project_id:
                print(f"No 'project_id' field in {SERVICE_ACCOUNT_FILE}")
                print(f"Available keys: {list(service_account_info.keys())}")
                return None
                
            return project_id
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in service account file: {e}")
        return None
    except Exception as e:
        print(f"Error reading service account: {e}")
        return None

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
    """Send FCM message to a device token using HTTP v1 API"""
    try:
        project_id = get_project_id()
        if not project_id:
            return {"error": "Failed to get project ID from service account"}
        
        access_token = get_access_token()
        if not access_token:
            return {"error": "Failed to get OAuth2 access token"}
        
        fcm_url = f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"
        
        payload = {
            "message": {
                "token": token,
                "data": {
                    "command": command,
                    "timestamp": str(int(time.time()))
                },
                "android": {
                    "priority": "high"
                },
                "apns": {
                    "headers": {
                        "apns-priority": "10"
                    }
                }
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
        r = requests.post(fcm_url, headers=headers, json=payload)
        return {
            "status_code": r.status_code,
            "text": r.text
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print("Not intended to be run directly")
