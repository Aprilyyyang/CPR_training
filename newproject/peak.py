from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import time
import random
from collections import deque
from threading import Thread

app = Flask(__name__)
socketio = SocketIO(app)

# 存储实时数据的列表
real_time_data = []

def simulate_cpr(duration_seconds=120):
    global real_time_data

    compressions = 0
    last_compression_time = None
    data_window = deque(maxlen=3)  # 用于存储连续的三个数据点

    for time_step in range(duration_seconds):
        distance = simulate_distance(time_step)
        timestamp = time_step
        data_window.append((timestamp, distance))

        if len(data_window) == 3 and is_peak(data_window):
            compressions += 1
            if last_compression_time is not None:
                time_diff = timestamp - last_compression_time
                if time_diff > 0:
                    compressions_per_minute = compressions / time_diff * 60
                    real_time_data.append({'timestamp': timestamp, 'distance': distance, 'compression_per_minute': compressions_per_minute})
            last_compression_time = timestamp
        else:
            real_time_data.append({'timestamp': timestamp, 'distance': distance})

        socketio.emit('update_data', real_time_data)
        time.sleep(1)

def simulate_distance(time_step):
    # 这里的逻辑根据您的实际情况可能需要调整
    return random.uniform(50, 100)

def is_peak(data_window):
    # 检查中间点是否是峰值
    return data_window[1][1] > data_window[0][1] and data_window[1][1] > data_window[2][1]

# 启动模拟 CPR 的线程
simulate_thread = Thread(target=simulate_cpr)
simulate_thread.start()

# WebSocket 事件，用于将实时数据推送给客户端
@socketio.on('connect')
def handle_connect():
    emit('update_data', real_time_data)

@app.route('/')
def index():
    return render_template('index_gauge.html')
    #return render_template('gauge.html')

if __name__ == '__main__':
    socketio.run(app, debug=True)
