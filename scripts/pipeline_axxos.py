# ============================================================
# pipeline_axxos.py
# Purpose: Independent integration pipeline for Axxos OEE.
# Watches the shared file that Ignition writes processed alarm
# events to, applies Axxos-specific field mapping, and sends
# each event to the Axxos OEE (mock) dashboard.
# ============================================================

import json
import time
import requests

FILE_PATH = "C:\\poc\\processed_events.jsonl"
AXXOS_API_URL = "http://localhost:8084/post"  # mock Axxos OEE dashboard endpoint

def map_to_axxos_format(event):
    """
    Translate the generic event coming from Ignition into the
    field names/structure that Axxos OEE expects.
    (In a real integration, this mapping would match Axxos's
    actual API schema.)
    """
    return {
        "AssetID": event["EquipmentID"],       # Axxos calls equipment "Asset"
        "AlarmType": event["EventType"],
        "OccurredAt": event["EventTimestamp"],
        "FaultCode": event.get("ErrorCode"),
        "FaultDescription": event.get("ErrorDescription")
    }

def send_to_axxos(payload):
    try:
        response = requests.post(AXXOS_API_URL, json=payload, timeout=5)
        print("[Axxos] Sent:", payload, "-> Status:", response.status_code)
    except Exception as e:
        print("[Axxos] ERROR sending data:", e)

def main():
    print("Axxos pipeline started. Watching:", FILE_PATH)

    # Track how many lines we've already processed, so we don't
    # resend the same event every time we poll the file.
    last_line_count = 0

    while True:
        try:
            with open(FILE_PATH, "r") as f:
                lines = f.readlines()
        except FileNotFoundError:
            # File doesn't exist yet (Ignition hasn't written anything yet)
            time.sleep(2)
            continue

        # Only process lines that are new since our last check
        new_lines = lines[last_line_count:]

        for line in new_lines:
            line = line.strip()
            if not line:
                continue
            event = json.loads(line)
            axxos_payload = map_to_axxos_format(event)
            send_to_axxos(axxos_payload)

        last_line_count = len(lines)

        time.sleep(2)  # check for new events every 2 seconds

if __name__ == "__main__":
    main()
