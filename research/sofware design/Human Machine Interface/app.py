from flask import Flask, render_template, jsonify
from queue import Queue
from utils import detection_engine, prediction_engine
from flask_socketio import SocketIO
import threading
import time
import sys



# QUEUES ALLOW FOR INTERTHREAD COMMUNICATION
camera_reader_frame_queue = Queue(maxsize=5)
detection_engine_result_queue = Queue(maxsize=5)
# the above is necessary so that:
# 1) the detection engine itself can be multi threaded (for efficiency) with smooth frame reading from camera
# 2) detection engine can communicate results safely with prediction engine 


app = Flask(__name__)
hmi_socket = SocketIO(app, cors_allowed_origins="*")  # allow connections from frontend

@app.route('/')
def index():
    # Render front-end. The live feed area will show placeholder text.
    return render_template('index.html')

@app.route('/neutralize', methods=['POST'])
def neutralize():
    # This is where we will add the neutralize command. For now we print.
    print('neutralize', file=sys.stdout)
    sys.stdout.flush()
    return jsonify({"status": "ok", "action": "neutralize"})

def run_flask():
    # Note: use debug=False in production
    hmi_socket.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False)























if __name__ == '__main__':
    # Start background video thread (daemon so it exits with main process)
    detection_engine_thread = threading.Thread(
        target=detection_engine, 
        kwargs= {
            "frame_queue":camera_reader_frame_queue, 
            "result_queue":detection_engine_result_queue
        },
        daemon=True
    )
    detection_engine_thread.start()

    predection_engine_thread = threading.Thread(
    target=prediction_engine,
    kwargs={
        "hmi_socket":hmi_socket,
        "result_queue":detection_engine_result_queue
    }, 
    daemon=True
    )
    predection_engine_thread.start()

    # Start HMI in its own thread
    hmi_thread = threading.Thread(target=run_flask, daemon=True)
    hmi_thread.start()

    try:
        while True:
            time.sleep(1) # we do this to keep the main thread alive, without this, when the main thread exits, the daemon threads will also exit immediately
    except KeyboardInterrupt:
        print("Shutting Down Uzziah...")


