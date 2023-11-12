from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import time
import board
import busio
import adafruit_vl6180x
import random
from threading import Thread

app = Flask(__name__)
socketio = SocketIO(app)

# 初始化 VL6180X 传感器
i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_vl6180x.VL6180X(i2c)

# 存储实时数据的列表
real_time_data = []

# 模拟 CPR 的线程
def simulate_cpr(duration_minutes=2):
    global real_time_data

    for _ in range(duration_minutes * 60):
        distance = random.uniform(5, 10)
        timestamp = time.strftime("%H:%M:%S")
        real_time_data.append((timestamp, distance))
        time.sleep(1)

# 启动模拟 CPR 的线程
simulate_thread = Thread(target=simulate_cpr)
simulate_thread.start()

# WebSocket 事件，用于将实时数据推送给客户端
@socketio.on('connect')
def handle_connect():
    emit('update_data', real_time_data)

# 路由，用于渲染 HTML 页面
@app.route('/')
def index():
    return render_template('index.html')

# 启动 Flask 应用
if __name__ == '__main__':
    socketio.run(app, debug=True)
