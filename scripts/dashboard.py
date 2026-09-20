# ============================================================
# dashboard.py
# Purpose: Lightweight mock "Maximo" and "Axxos OEE" web servers
# for the demo. Each one:
#   - exposes a POST /post endpoint (so the pipeline scripts
#     don't need any changes to send data to it)
#   - stores every received event in memory
#   - shows a live, auto-refreshing table of received events
#     at its root URL, so we can visually "watch data arrive"
#     in the browser during a live demo/training.
# ============================================================

from flask import Flask, request, render_template_string
import threading
from datetime import datetime

# --- Simple HTML template shared by both dashboards ---
# Auto-refreshes every 3 seconds so new events appear without
# manually reloading the page.
TEMPLATE = """
<html>
<head>
    <title>{{ title }}</title>
    <meta http-equiv="refresh" content="3">
    <style>
        body { font-family: Arial, sans-serif; margin: 30px; background: #f4f7fe; }
        h1 { color: #1e2761; }
        table { border-collapse: collapse; width: 100%; background: white; }
        th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
        th { background: #1e2761; color: white; }
        tr:nth-child(even) { background: #f2f2f2; }
    </style>
</head>
<body>
    <h1>{{ title }}</h1>
    <p>Total events received: {{ events|length }}</p>
    <table>
        <tr>
            {% for key in headers %}
            <th>{{ key }}</th>
            {% endfor %}
        </tr>
        {% for event in events|reverse %}
        <tr>
            {% for key in headers %}
            <td>{{ event.get(key, "") }}</td>
            {% endfor %}
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

def make_app(title, headers):
    """Create a Flask app with its own event store."""
    app = Flask(title)
    events = []  # in-memory list of received events

    @app.route("/post", methods=["POST"])
    def receive_event():
        data = request.get_json()
        data["_received_at"] = datetime.now().strftime("%H:%M:%S")
        events.append(data)
        print("[%s] Received:" % title, data)
        return {"status": "received"}, 200

    @app.route("/")
    def show_dashboard():
        return render_template_string(
            TEMPLATE, title=title, events=events, headers=headers
        )

    return app

# --- Maximo dashboard (port 8083) ---
maximo_app = make_app(
    "Maximo - Received Work Order Events",
    ["_received_at", "EquipmentID", "EventType", "EventDate", "ProblemCode", "ProblemDescription"]
)

# --- Axxos OEE dashboard (port 8084) ---
axxos_app = make_app(
    "Axxos OEE - Received Alarm Events",
    ["_received_at", "AssetID", "AlarmType", "OccurredAt", "FaultCode", "FaultDescription"]
)

def run_maximo():
    maximo_app.run(host="0.0.0.0", port=8083)

def run_axxos():
    axxos_app.run(host="0.0.0.0", port=8084)

if __name__ == "__main__":
    print("Starting Maximo dashboard on http://localhost:8083")
    print("Starting Axxos OEE dashboard on http://localhost:8084")

    # Run both Flask apps at the same time, each on its own thread
    t1 = threading.Thread(target=run_maximo)
    t2 = threading.Thread(target=run_axxos)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
