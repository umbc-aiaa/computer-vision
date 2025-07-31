# Training script for YOLOv8n on SUAS dataset
from ultralytics import YOLO
model = YOLO('yolov8n.pt')
model.train(data='suas16.yaml', epochs=50, imgsz=640, batch=16, name='yolo8n_suas')
