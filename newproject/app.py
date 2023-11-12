from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import time
import random
from threading import Thread

app = Flask(__name__)
socketio = SocketIO(app)

# 存储实时数据的列表
real_time_data = []

# 正确的应该是100-120
compressions_per_minute = random.uniform(80, 130)

def simulate_cpr(duration_seconds=120):
    global real_time_data

    for time_step in range(duration_seconds):
        distance = simulate_distance(time_step)
        timestamp = time_step  # Use elapsed time in seconds
        real_time_data.append({'timestamp': timestamp, 'distance': distance})
        #socketio.emit('update_data', {'timestamp': timestamp, 'distance': distance})
        socketio.emit('update_data', real_time_data)  # 实时推送数据给客户端
        time.sleep(1)


# 模拟距离数据的函数，可以根据需要修改
# 模拟距离数据的函数，产生在50到100之间的值
def simulate_distance(time_step):
    #return random.uniform(5, 10)
    # Generate a random peak value every minute
    if time_step % (60 * compressions_per_minute) == 0:
        return random.uniform(90, 100)
    else:
        return random.uniform(50, 90)

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
    #return render_template('index_app.html')
    #return render_template('index_2chart.html')
    return render_template('index_gauge.html')
# 启动 Flask 应用
if __name__ == '__main__':
    socketio.run(app, debug=True)
