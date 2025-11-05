# welcome to our final project

| Project Members | Department |
| --------------- | ---------- |
| C21147354M      |            |
| C21145681W      |            |
| C21147799W      |            |
| C21145989W      |            |
| C21147067J      |            |
| C21145793S      |            |
| C21146707O      |            |
| C21146057T      |            |

## Overview

This repository contains research artifacts and a prototype Human-Machine Interface (HMI) for a computer vision system codenamed "Uzziah". The HMI is a Flask + Socket.IO app that displays a live video feed and overlays tracking/prediction results streamed from a backend detection/prediction pipeline.

Key components:
- Human Machine Interface (HMI): Flask server with a web UI, receives processed frames over Socket.IO and renders them in the browser.
- Detection/Prediction Engines: Background threads that read camera frames, run object detection + tracking, and emit processed frames to the HMI.
- Research materials: Design docs, tutorials, and resources used during development.

Note: The `Detection Engine` folder under `research/sofware design/Detection Engine/` includes a README indicating it was cleared at some point. The HMI side still references a detection pipeline and a `resources/weights.pt` file under `research/sofware design/resources/`. See Caveats below.

## Repository Structure

```
uzziah/
├─ projectproposal.pdf
├─ ReadMe.md  (this file)
└─ research/
   ├─ algorithm design/
   ├─ documentation/
   ├─ hardware design/
   │  └─ sketches/
   └─ sofware design/
      ├─ Detection Engine/
      │  ├─ README.md
      │  └─ requirements.txt
      ├─ Human Machine Interface/
      │  ├─ app.py
      │  ├─ requirements.txt
      │  ├─ templates/
      │  │  └─ index.html
      │  └─ static/
      │     ├─ style.css
      │     └─ script.js
      │  └─ utils/
      │     ├─ detection_engine.py
      │     └─ prediction_engine.py
      ├─ ReadMe.MD
      ├─ resources/
      │  └─ weights.pt
      └─ tutorials/
         ├─ SORT.ipynb
         ├─ fronted_streaming_connection.ipynb
         └─ how_to_track_objects_with_sort_tracker.ipynb
```

## HMI (Flask) — Quick Start (Windows PowerShell)

1. Navigate to the HMI directory:
   ```powershell
   cd "research/sofware design/Human Machine Interface"
   ```

2. Create and activate a virtual environment (recommended):
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install dependencies:
   ```powershell
   python -m pip install -r requirements.txt
   ```

4. Run the app:
   ```powershell
   python app.py
   ```

5. Open the UI in your browser at:
   - http://localhost:5000

The UI shows a tactical HUD-style page. A background thread starts the detection engine and another thread emits frames to the frontend via Socket.IO. Use the "NEUTRALIZE" button to test a POST action to `/neutralize`.

## Detection & Prediction Engines (Threads)

- Entry point: `research/sofware design/Human Machine Interface/app.py`
  - Spawns two daemon threads:
    - `utils.detection_engine.detection_engine(frame_queue, result_queue)`
    - `utils.prediction_engine.prediction_engine(result_queue, hmi_socket)`

- Detection engine (`utils/detection_engine.py`):
  - Reads frames from a camera, runs YOLO for detection, then SORT for tracking.
  - Publishes `(frame, tracks)` tuples into `result_queue`.

- Prediction engine (`utils/prediction_engine.py`):
  - Consumes `(frame, tracks)`, applies overlays, encodes frames as JPEG base64.
  - Emits frames to the web client via Socket.IO (`video_frame` event).

## Dependencies

HMI (`research/sofware design/Human Machine Interface/requirements.txt`):
- Flask, Flask-SocketIO, OpenCV, inference-gpu, trackers, supervision==0.27.0rc1

Detection Engine (`research/sofware design/Detection Engine/requirements.txt`):
- Currently a placeholder; see that README for restoration instructions if needed.

Additional libraries referenced by code:
- `ultralytics` (YOLO) and a `SORTTracker` implementation are imported in `utils/detection_engine.py` but are not listed in the HMI requirements. You may need to install them manually:
  ```powershell
  python -m pip install ultralytics
  ```
  For SORT, install your chosen implementation (e.g., a `trackers` package providing `SORTTracker`).

## Caveats & Notes

- The `Detection Engine` README states that pipeline code was cleared. However, the HMI `utils/detection_engine.py` is present and expects a YOLO model at `weights.pt` and a `SORTTracker` from a `trackers` module. If these are unavailable, the HMI background threads may fail at runtime.
- The model weights file `resources/weights.pt` exists under `research/sofware design/resources/`. Ensure the path used by `ultralytics.YOLO` matches where your weights actually are, or adjust the code accordingly.
- For GPU acceleration, configure the correct CUDA runtime and install compatible versions of PyTorch/Ultralytics as needed.

## Development Tips

- Use a virtual environment to isolate dependencies.
- If Socket.IO events are not reaching the browser, verify the app is started via `SocketIO.run` (already configured in `app.py`) and that the client loads the correct Socket.IO script.
- Check the console output for background thread exceptions.

## Contributing

- Open issues or PRs for improvements.
- If you want the original detection pipeline restored (model loading, SORT tracking, Flask/SocketIO frontend integration), specify the features required and we can re-implement them.