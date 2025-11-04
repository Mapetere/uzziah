import cv2
import threading
import time
from queue import Queue
from ultralytics import YOLO
from trackers import SORTTracker

__all__ = ['detection_engine']

# Initialize YOLO and SORT globally so both threads can use them
model = YOLO("weights.pt")
tracker = SORTTracker()

def camera_reader(frame_queue, src=0):
    """Continuously capture frames and push into frame_queue."""
    cap = cv2.VideoCapture(src)
    while True:
        ret, frame = cap.read()
        if ret:
            if not frame_queue.full():
                frame_queue.put(frame)
        time.sleep(0.01)  # slight delay to prevent CPU hogging

def sort_processor(frame_queue, result_queue):
    """Consume frames, run YOLO detection + SORT tracking, push results to result_queue."""
    while True:
        if not frame_queue.empty():
            frame = frame_queue.get()
            
            # Run YOLO inference
            results = model(frame)
            detections = []
            for det in results[0].boxes.xyxy:  # xyxy format
                x1, y1, x2, y2 = det.cpu().numpy()
                conf = det.conf.cpu().numpy()
                detections.append([x1, y1, x2, y2, conf])

            # Run SORT tracking
            tracks = tracker.update(detections)
            
            # Push processed frame + tracking info to result_queue
            result_queue.put((frame, tracks))
        else:
            time.sleep(0.005)  # prevent busy wait

def detection_engine(frame_queue: Queue, result_queue: Queue):
    """Start camera reader and SORT processor threads."""
    # Start camera reader thread
    cam_thread = threading.Thread(target=camera_reader, args=(frame_queue,), daemon=True)
    cam_thread.start()
    
    # Start SORT processor thread
    sort_thread = threading.Thread(target=sort_processor, args=(frame_queue, result_queue), daemon=True)
    sort_thread.start()

    while True:
        time.sleep(1)  # keep main alive
