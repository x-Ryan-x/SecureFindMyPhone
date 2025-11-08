from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import json, os
from typing import Optional
from datetime import datetime
import main as m
DATA_FILE = "devices.json"

app = FastAPI(title="FCM Device Registry", version="1.0")

# ---------- Pydantic model ----------
class DeviceRegistration(BaseModel):
    user: str
    token: str

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

def load_locations():
    if not os.path.exists(LOC_FILE):
        with open(LOC_FILE, "w") as f:
            json.dump({}, f)
    with open(LOC_FILE) as f:
        return json.load(f)

def save_locations(locations):
    with open(LOC_FILE, "w") as f:
        json.dump(locations, f, indent=2)

# --- Pydantic model ---
class LocationReport(BaseModel):
    user: str
    latitude: float
    longitude: float
    timestamp: Optional[int] = Field(default_factory=lambda: int(datetime.utcnow().timestamp()))


@app.post("/location")
def report_location(loc: LocationReport):
    """
    Receive location data from a phone.
    Example body:
    {
        "user": "alice",
        "latitude": 37.422,
        "longitude": -122.084,
        "timestamp": 1731100000
    }
    """
    locations = load_locations()
    # Store latest location for user
    locations[loc.user] = {
        "latitude": loc.latitude,
        "longitude": loc.longitude,
        "timestamp": loc.timestamp
    }
    save_locations(locations)
    return {"message": f"Location for {loc.user} received."}