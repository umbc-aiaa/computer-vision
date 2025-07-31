import cv2
import numpy as np
import threading
import time
from flask import Flask, Response, render_template_string
from ultralytics import YOLO

app = Flask(__name__)

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise IOError("Cannot open camera")

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

model = YOLO("best.pt")  # Replace with your actual trained model file

SUAS_OBJECTS = [
    "person", "car", "motorcycle", "airplane", "bus", "boat",
    "stop sign", "snowboard", "umbrella", "sports ball",
    "baseball bat", "bed", "tennis racket", "suitcase", "skis"
]

latest_detections = []
full_detection_log = []
lock = threading.Lock()

def get_current_gps():
    return 38.315300, -76.550800  # Replace with actual GPS if available

def update_detections():
    global latest_detections, full_detection_log
    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(1)
            continue

        results = model.predict(frame, conf=0.25, verbose=False)[0]

        detections = []
        with lock:
            for box in results.boxes:
                class_id = int(box.cls[0])
                label = model.names[class_id]
                if label in SUAS_OBJECTS:
                    lat, lon = get_current_gps()
                    entry = {"object": label, "lat": lat, "lon": lon}
                    full_detection_log.append(entry)
                    detections.append(f"{label}: {lat:.5f}, {lon:.5f}")
                    print(f"DETECTED: {entry}")
            latest_detections = detections

        time.sleep(1)

HTML_PAGE = '''
<html>
<head><title>SUAS Detection</title></head>
<body style="background:#111; color:#fff; text-align:center;">
<h1>SUAS Object Detection</h1>
<p>Detected: <span id="detections">Loading...</span></p>
<script>
setInterval(() => {
    fetch("/detections")
        .then(r => r.text())
        .then(d => document.getElementById("detections").innerText = d);
}, 1000);
</script>
<img src="/video_feed" style="width:640px;">
</body>
</html>
'''

@app.route("/")
def index():
    return render_template_string(HTML_PAGE)

@app.route("/video_feed")
def video_feed():
    return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/detections")
def detections():
    with lock:
        return ', '.join(latest_detections) if latest_detections else "None"

def generate_frames():
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        _, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

threading.Thread(target=update_detections, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)