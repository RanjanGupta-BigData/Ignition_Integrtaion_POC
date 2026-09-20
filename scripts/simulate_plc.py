# ============================================================
# simulate_plc.py
# Purpose: Fake PLC/equipment data generator.
# This mimics what a real PLC or shop-floor sensor would send —
# we use it here because we don't have a real PLC connected yet.
# It publishes JSON messages to an MQTT broker (running in Docker)
# every 5 seconds, which Ignition will later subscribe to.
# ============================================================

import json, time, random
from datetime import datetime
import paho.mqtt.client as mqtt   # MQTT client library (installed via pip)

# --- Connect to the MQTT broker ---
# "localhost" + port 1883 = the Mosquitto broker running in our Docker container
client = mqtt.Client()
client.connect("localhost", 1883)

# --- List of fake equipment IDs ---
# In a real plant, these would be actual PLC/machine identifiers
equipment = ["PLC-101", "PLC-102", "PLC-203"]

# --- Infinite loop: keep generating and sending fake events ---
while True:

    # Build one fake event as a Python dictionary (like a JSON object)
    payload = {
        "equipmentId": random.choice(equipment),          # pick a random machine
        "eventType": random.choice(["Alarm", "Info", "Downtime"]),  # pick a random event type
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # current time, plain format
        "errors": [
            {"code": "E01", "desc": "Overheat"},
            {"code": "E02", "desc": "Pressure Low"}
        ] if random.random() > 0.5 else []   # 50% chance of including error details
    }

    # --- Publish the event to the MQTT topic "plant/line1/events" ---
    # Ignition (via MQTT Engine) will be subscribed to this same topic
    # json.dumps() converts our Python dict into a JSON string, since MQTT sends plain text/bytes
    client.publish("plant/line1/events", json.dumps(payload))

    # --- Print to terminal so we can see what was sent ---
    print("Published:", payload)

    # --- Wait 5 seconds before sending the next fake event ---
    time.sleep(5)
