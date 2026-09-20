# ============================================================
# ignition_tag_change_script.py
#
# NOTE: This file is a REFERENCE COPY of the script that lives
# inside Ignition itself (Project Browser > Scripting > Gateway
# Events > Tag Change > Tag_Change_Script). It cannot be "run"
# standalone — paste its contents into that script editor inside
# Ignition Designer.
#
# Tag Path configured on this script: [MQTT Engine]plant/line1/events
#
# Trigger: fires whenever the "plant/line1/events" tag value changes
# Purpose: parse and transform the raw JSON, then:
#   1. store the processed result in a tag (for live visibility
#      inside Ignition during a demo)
#   2. append each processed message as one line to a shared file,
#      which is the handoff point to the external Python pipelines
#      (pipeline_axxos.py and pipeline_maximo.py)
#
# IMPORTANT: In Ignition 8.3.x the entry-point function Ignition
# calls is `onTagChange(...)`, NOT `valueChanged(...)`. Using the
# wrong function name means the script silently never runs.
# ============================================================

def onTagChange(initialChange, newValue, previousValue, event, executionCount):
    import json
    from datetime import datetime

    raw = newValue.value
    if raw is None:
        return

    # --- Convert the raw JSON string into a Python dictionary ---
    try:
        data = system.util.jsonDecode(raw)
    except Exception as e:
        return  # skip if it's not valid JSON

    # --- FILTER: only process "Alarm" events, drop everything else ---
    if data.get("eventType") != "Alarm":
        return

    # --- TIMESTAMP REFORMAT: convert plain string to ISO 8601 ---
    dt = datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S")
    iso_timestamp = dt.strftime("%Y-%m-%dT%H:%M:%S")

    # --- FIELD RENAME/MAP: apply a neutral, normalized naming ---
    # (Axxos OEE and Maximo each apply their own specific field
    #  mapping inside their own Python pipeline script)
    base_record = {
        "EquipmentID": data["equipmentId"],
        "EventType": data["eventType"],
        "EventTimestamp": iso_timestamp
    }

    # --- SPLIT NESTED ARRAY: turn each error into its own message ---
    errors = data.get("errors", [])
    messages = []
    if errors:
        for err in errors:
            msg = dict(base_record)
            msg["ErrorCode"] = err["code"]
            msg["ErrorDescription"] = err["desc"]
            messages.append(msg)
    else:
        messages.append(base_record)

    # --- Store locally so we can see it live in Designer (for the demo) ---
    system.tag.write("[default]ProcessedBatch", system.util.jsonEncode(messages))

    # --- Write each processed message as one line to a shared file ---
    # This file acts as the handoff point between Ignition and the
    # external Python pipelines (Axxos OEE + Maximo), so we don't need
    # to install extra REST/MQTT publish modules for this POC.
    for msg in messages:
        line = system.util.jsonEncode(msg) + "\n"
        system.file.writeFile("C:\\poc\\processed_events.jsonl", line, True)  # True = append mode

    system.util.getLogger("POC").info(
        "Processed %d message(s), written to file" % len(messages)
    )
