# ============================================================
# pipeline_maximo.py
# Purpose: Independent integration pipeline for Maximo.
# Watches the same shared file, applies Maximo-specific field
# mapping, and sends each event to the Maximo (mock) dashboard.
# ============================================================

import json
import time
import requests

FILE_PATH = "C:\\poc\\processed_events.jsonl"
MAXIMO_API_URL = "http://localhost:8083/post"  # mock Maximo dashboard endpoint

def map_to_maximo_format(event):
    """
    Translate the generic event into the field names/structure
    Maximo expects for a work-order-relevant record.
    (In a real integration, this would match Maximo's actual
    REST API / work order schema.)
    """
    return {
        "EquipmentID": event["EquipmentID"],
        "EventType": event["EventType"],
        "EventDate": event["EventTimestamp"],
        "ProblemCode": event.get("ErrorCode"),
        "ProblemDescription": event.get("ErrorDescription")
    }

def send_to_maximo(payload):
    try:
        response = requests.post(MAXIMO_API_URL, json=payload, timeout=5)
        print("[Maximo] Sent:", payload, "-> Status:", response.status_code)
    except Exception as e:
        print("[Maximo] ERROR sending data:", e)

def main():
    print("Maximo pipeline started. Watching:", FILE_PATH)

    last_line_count = 0

    while True:
        try:
            with open(FILE_PATH, "r") as f:
                lines = f.readlines()
        except FileNotFoundError:
            time.sleep(2)
            continue

        new_lines = lines[last_line_count:]

        for line in new_lines:
            line = line.strip()
            if not line:
                continue
            event = json.loads(line)
            maximo_payload = map_to_maximo_format(event)
            send_to_maximo(maximo_payload)

        last_line_count = len(lines)

        time.sleep(2)

if __name__ == "__main__":
    main()
