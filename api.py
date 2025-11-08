from fastapi import FastAPI
from pydantic import BaseModel, Field
import json
import os
import sys
from typing import Optional
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import main as m

DATA_FILE = "./data/devices.json"
location_directory = "/data/"

app = FastAPI(title="FCM Device Registry", version="1.0")

# ---------- Pydantic model ----------
class DeviceRegistration(BaseModel):
    user: str
    token: str

# --- Pydantic model ---
class LocationReport(BaseModel):
    token: str
    latitude: float
    longitude: float
    timestamp: Optional[int] = Field(default_factory=lambda: int(datetime.utcnow().timestamp()))


# ---------- Helper functions ----------

def get_location_file(token: str) -> str:    
    return os.path.join(location_directory, f"{token}.json")

def load_token_locations(filepath: str) -> list:
    """Load location history from a file"""
    if not os.path.exists(filepath):
        return []
    
    try:
        with open(filepath) as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def append_location(user: str, location_data: dict):
    """Append a new location to token's history file"""
    filepath = get_location_file(user)
    locations = load_token_locations(filepath)
    locations.append(location_data)
    
    with open(filepath, "w") as f:
        json.dump(locations, f, indent=2)


# ---------- API endpoints ----------

@app.post("/register")
def register_device(device: DeviceRegistration):
    """
    Register or update a device token for a user.
    Example body:
    {
        "user": "alice",
        "token": "fcm_device_token_here"
    }
    """
    m.add_user(device.user, device.token)
    return {"message": f"Registered {device.user}"}


@app.post("/location")
def report_location(loc: LocationReport):
    """
    Receive and store location data from a phone.
    Example body:
    {
        "user": "alice",
        "latitude": 37.422,
        "longitude": -122.084,
        "timestamp": 1731100000
    }
    """
    location_data = {
        "token": loc.token,
        "latitude": loc.latitude,
        "longitude": loc.longitude,
        "timestamp": loc.timestamp,
        "received_at": datetime.utcnow().isoformat()
    }
    
    append_location(loc.token, location_data)
    
    return {
        "message": f"Location for {loc.user} saved",
        "file": get_location_file(loc.user)
    }