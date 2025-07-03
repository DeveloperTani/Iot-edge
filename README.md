# IoT Edge System Telemetry Module

The current version of this project deploys two IoT Edge modules (system_reader) and (cloud_publisher) to a physical Ubuntu 22.04 laptop accessed via SSH. The modules collect local system telemetry and forward it to Azure IoT Hub in real time.

 As a next phase, I plan to integrate my home-built Wi-fi "thermostat" into this project to act as a physical data source.

## 📌 Overview
🔧 Tech Stack

    Azure IoT Hub + IoT Edge runtime

    Docker + Azure Container Registry

    Python 3.10-slim

    Host system: Ubuntu 22.04 (Laptop)

## 🔧 Key Features

- Gathers telemetry (CPU, memory, disk usage) using psutil
- Sends JSON-formatted messages every 5 seconds
- Clean separation of logic between system_reader and cloud_publisher

## 🔁 Sample Telemetry Payload
```json
{
  "timestamp": "2025-06-26T18:55:00.363867Z",
  "cpu_usage": 0.0,
  "memory_usage": 6.6,
  "disk_usage": 0.3
}
```
## 🚧 Future Plans

- Logic separation into multiple modules with custom routes ✅
- Build a custom Wi-fi "thermostat" using an ESP32, temp sensor and a relay ✅
- Read and process live data from the ESP32 thermostat
- Implement cloud-to-device (C2D) messaging
- Support direct method invocation from the cloud
- Connecting data stream to Power BI (If I get Microsoft dev program access)





📸 Screenshots
![Event Stream](/screenshots/azure-cli-stream.png)

![Device Status](/screenshots/sensorLogger-device.png)

![Module Logs](/screenshots/reader-and-publisher-logs.png)

![system_reader](/screenshots/system_reader.png)

![cloud_publisher](/screenshots/cloud_publisher.png)
