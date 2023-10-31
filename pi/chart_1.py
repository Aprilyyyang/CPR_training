import time
import board
import busio
import adafruit_vl6180x
import matplotlib.pyplot as plt
from flask import Flask, render_template, Response
import threading

app = Flask(__name__)

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_vl6180x.VL6180X(i2c)

num_readings = 5
readings = [0] * num_readings
i = 0
total = 0

max_data_points = 100
distance_data = [0] * max_data_points
speed_data = [0] * max_data_points
time_stamps = [0] * max_data_points
#relative_time = [0] * max_data_points
data_count = 0




def send_data_to_computer():
    print("Data:")
    
    for i in range(data_count):
        print("Distance (mm):", distance_data[i])
        print("Speed (mm/s):", speed_data[i])
        print("Time (s):", time_stamps[i])
    print("EndData")

def update_chart():
    global data_count
    while True:
        if data_count > 1:
            plt.clf()
            #relative_time = [time_stamps[i] - currenttime for i in time_stamps[:data_count]]  # 计算相对时间
            plt.plot(time_stamps[:data_count], distance_data[:data_count], label="Distance (mm)")
            plt.plot(time_stamps[:data_count], speed_data[:data_count], label="Speed (mm/s)")
            plt.xlabel('Time (s)')  # x轴显示为秒
            plt.ylabel('Values')
            plt.legend()
            plt.grid()
            plt.pause(1.0)
        time.sleep(1)

@app.route('/')
def index():
    return render_template('chart_1.html')

@app.route('/data')
def get_data():
    global data_count
    #global relative_time
    if data_count > 1:
        data = "\n".join([f"{time_stamps[i]},{distance_data[i]},{speed_data[i]}" for i in range(data_count)])
        return data
    return "0,0,0"


def collect_sensor_data():
    global total
    global i
    global data_count
    start_time = time.time()
    while True:
        range_mm = sensor.range

        total -= readings[i]
        readings[i] = range_mm
        total += range_mm
        i = (i + 1) % num_readings

        average_range = total / num_readings

        if data_count < max_data_points:
            distance_data[data_count] = average_range
            time_stamps[data_count] = int((time.time() - start_time) * 1000)

            delta_time = (time_stamps[data_count] - time_stamps[data_count - 1]) / 1000.0
            speed = (average_range - distance_data[data_count - 1]) / delta_time
            speed_data[data_count] = speed
            data_count += 1

        if data_count >= max_data_points:
            send_data_to_computer()
            break

        time.sleep(0.1)

filename = "sensordata.txt"

def save_data_to_file(filename):
    with open(filename, 'w') as file:
        file.write("Data:\n")
        for i in range(data_count):
            file.write(f"Distance (mm): {distance_data[i]}\n")
            file.write(f"Speed (mm/s): {speed_data[i]}\n")
            file.write(f"Time (s): {time_stamps[i]}\n")  # 以秒为单位
        file.write("EndData")

    


# 启动数据更新线程
sensor_data_thread = threading.Thread(target=collect_sensor_data)
save_data_thread = threading.Thread(target=save_data_to_file, args=(filename,))
sensor_data_thread.daemon = True
save_data_thread.start()
sensor_data_thread.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
