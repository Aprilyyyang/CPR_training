#include <Wire.h>
#include "Adafruit_VL6180X.h"

Adafruit_VL6180X vl = Adafruit_VL6180X();
uint8_t prevRange = 0;
unsigned long prevTime = 0;

const int numReadings = 5; // 增加数据点数量
int readings[numReadings];
int index = 0;
int total = 0;

const int maxDataPoints = 100; // 增加最大数据点数
int distanceData[maxDataPoints];
int speedData[maxDataPoints]; // 用于保存速度数据
unsigned long timeStamps[maxDataPoints];
int dataCount = 0;

void setup() {
  Serial.begin(115200);

  while (!Serial) {
    delay(1);
  }
  
  Serial.println("Adafruit VL6180x test!");
  if (!vl.begin()) {
    Serial.println("Failed to find sensor");
    while (1);
  }
  Serial.println("Sensor found!");
}

void sendDataToComputer() {
  Serial.println("Data:");
  for (int i = 0; i < dataCount; i++) {
    Serial.print("Distance (mm): ");
    Serial.print(distanceData[i]);

    Serial.print("  Speed (mm/s): ");
    Serial.print(speedData[i]);
    Serial.println(); 

    //Serial.print("  Time (ms): ");
    //Serial.println(timeStamps[i]);
  }
  Serial.println("EndData");
}

void loop() {
  float lux = vl.readLux(VL6180X_ALS_GAIN_5);
  
  uint8_t range = vl.readRange();
  uint8_t status = vl.readRangeStatus();

  if (status == VL6180X_ERROR_NONE) {
    total -= readings[index];
    readings[index] = range;
    total += range;
    index = (index + 1) % numReadings;

    float averageRange = (float)total / numReadings;

    if (dataCount < maxDataPoints) {
      distanceData[dataCount] = averageRange;
      timeStamps[dataCount] = millis();

      Serial.print("Time (ms): ");
      Serial.println(timeStamps[dataCount]);

      float deltaTime = (timeStamps[dataCount] - prevTime) / 1000.0; // 计算时间间隔
      float speed = (averageRange - prevRange) / deltaTime; // 计算速度
      speedData[dataCount] = speed; // 保存速度数据

      Serial.print("AvgRange (mm): ");
      Serial.println(distanceData[dataCount]);

      Serial.print("Speed (mm/s): ");
      Serial.println(speedData[dataCount]);
      Serial.println();

      dataCount++;

      delay(10);
    }

    prevRange = averageRange;
    prevTime = timeStamps[dataCount - 1];

    if (dataCount >= maxDataPoints) {
      //sendDataToComputer();
      while (1);
    }
  }
}
