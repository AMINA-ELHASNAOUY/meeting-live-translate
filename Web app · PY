"""Browser version of the live captioner.

Runs the same pipeline as main.py, but streams captions to a web page
at http://localhost:7860 instead of the terminal, using Server-Sent
Events (no extra websocket dependency, works with plain Flask).
"""

import json
import queue
import threading

from flask import Flask, Response, render_template

from pipeline import listen, TARGET_LANGUAGE

app = Flask(__name__)

# Thread-safe queue: the background listener thread pushes events,
# the SSE route drains them to any connected browser tab.
event_queue: "queue.Queue[dict]" = queue.Queue()
listener_started = False
listener_lock = threading.Lock()


def run_listener():
    """Background thread: runs whisper-stream + translation, forever."""
    for event in listen():
        event_queue.put(event)


def ensure_listener_started():
    global listener_started
    with listener_lock:
        if not listener_started:
            thread = threading.Thread(target=run_listener, daemon=True)
            thread.start()
            listener_started = True


@app.route("/")
def index():
    return render_template("index.html", target_language=TARGET_LANGUAGE)


@app.route("/events")
def events():
    ensure_listener_started()

    def stream():
        # Tell the browser we're live as soon as it connects.
        yield f"data: {json.dumps({'type': 'status', 'message': 'listening'})}\n\n"
        while True:
            event = event_queue.get()  # blocks until the next caption
            yield f"data: {json.dumps(event)}\n\n"

    return Response(stream(), mimetype="text/event-stream")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=7860, threaded=True, debug=False)
