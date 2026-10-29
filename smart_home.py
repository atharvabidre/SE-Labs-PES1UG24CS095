"""Controller for smart home devices: rooms, power use and saved state."""

import json
import os
import re
import subprocess  # nosec B404 - only used by run_scene, which validates its input

HUB_HOST = os.environ.get("HUB_HOST", "127.0.0.1")
HUB_PORT = 8080
POWER_USAGE = {"light": 10, "fan": 60, "thermostat": 1500, "tv": 120}
HUB_PASSWORD = os.environ.get("HUB_PASSWORD", "")
MIN_TEMP = 16
MAX_TEMP = 30

DEVICES = {}


def add_device(device_name, kind, room="Living Room", settings=None):
    """Add a device to a room, giving each device its own settings dict."""
    DEVICES[device_name] = {"kind": kind, "room": room, "on": False,
                            "settings": dict(settings or {})}


def toggle_device(device_name):
    """Flip a device on/off and return its new state (None if unknown)."""
    if device_name not in DEVICES:
        print("Device not found:", device_name)
        return None
    DEVICES[device_name]["on"] = not DEVICES[device_name]["on"]
    return DEVICES[device_name]["on"]


def set_temperature(device_name, value):
    """Set a thermostat, clamped to the safe range. Return True on success."""
    device = DEVICES.get(device_name)
    if device is None:
        print("Device not found:", device_name)
        return False
    if device["kind"] != "thermostat":
        print(device_name, "is not a thermostat")
        return False
    device["settings"]["temperature"] = min(max(value, MIN_TEMP), MAX_TEMP)
    return True


def devices_in_room(room):
    """Return the names of all devices in the given room."""
    return [name for name, info in DEVICES.items() if info["room"] == room]


def power_usage():
    """Return the total power draw (W) of devices that are switched on."""
    active = [info for info in DEVICES.values() if info["on"]]
    return sum(POWER_USAGE.get(info["kind"], 0) for info in active)


def save_state(file_name="home_state.json"):
    """Write the current home state to a JSON file."""
    with open(file_name, "w", encoding="utf-8") as state_file:
        json.dump(DEVICES, state_file, indent=2)


def hub_address():
    """Return the hub address as host:port."""
    return f"{HUB_HOST}:{HUB_PORT}"


def run_scene(scene_script):
    """Run a scene script from the scenes folder (not used by the demo)."""
    if not re.fullmatch(r"[\w.-]+\.sh", scene_script):
        raise ValueError(f"Invalid scene name: {scene_script}")
    scene_path = os.path.join("scenes", scene_script)
    subprocess.run(["bash", scene_path], check=True)  # nosec B603 B607


def main():
    """Run a short demonstration."""
    add_device("Ceiling Light", "light")
    add_device("Bedroom Fan", "fan", "Bedroom")
    add_device("Thermostat", "thermostat", "Bedroom")
    add_device("Smart TV", "tv")
    toggle_device("Ceiling Light")
    toggle_device("Thermostat")
    toggle_device("Garage Door")
    set_temperature("Thermostat", 35)
    set_temperature("Ceiling Light", 20)
    print("Bedroom devices:", devices_in_room("Bedroom"))
    print("Current power use (W):", power_usage())
    print("Hub address:", hub_address())  # for app setup
    print("Light settings:", DEVICES["Ceiling Light"]["settings"])
    print("Devices on:",
          [name for name, info in DEVICES.items() if info["on"]])
    save_state()


if __name__ == "__main__":
    main()
