from ultralytics import YOLO
import os

# Load pre-trained model
model = YOLO('/Path/to/pretrained/weights.pt')  # example: yolov10n.pt

# Config file
data_config = '/Path/to/config/file.yaml'

# Train model
model.train(
    data=data_config,      
    epochs=50,               
    batch=16,                
    imgsz=640,               
    project='runs/train',    # path where weights will be saved
    name='yolo_insect_detection', 
    exist_ok=True,           
    save=True,
    save_period=1,
)

# Save model
model.save('/Path/to/saved/model.pt')
