import cv2
import time
import base64

def prediction_engine(result_queue, hmi_socket):
    """Consume (frame, tracks) tuples from detection_engine,
    apply projectile predictions or overlays, and emit frames via socket.
    """
    while True:
        if not result_queue.empty():
            frame, tracks = result_queue.get()

            # --- 1. Run prediction algorithm here ---
            # For now, we’ll just overlay bounding boxes + IDs
            for t in tracks:
                x1, y1, x2, y2, track_id = map(int, t[:5])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f'ID {track_id}', (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

            # --- 2. Encode to JPEG and base64 for web transmission ---
            _, buffer = cv2.imencode('.jpg', frame)
            jpg_as_text = base64.b64encode(buffer).decode('utf-8')

            # --- 3. Emit to frontend via socket ---
            hmi_socket.emit('video_frame', {'image': jpg_as_text})
        else:
            time.sleep(0.01)  # prevent busy-wait

        time.sleep(0.03)  # maintain ~30 FPS output
