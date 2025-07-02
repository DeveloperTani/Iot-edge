# IoT Edge System Telemetry Module

The current version of this project deploys two IoT Edge modules (system_reader) and (cloud_publisher) to a physical Ubuntu 22.04 laptop accessed via SSH. The modules collect local system telemetry and forward it to Azure IoT Hub in real time.

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
- Built without Microsoft IoT SDK base images


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
- Implement cloud-to-device (C2D) messaging
- Support direct method invocation from the cloud
- Build a custom "thermostat" using an ESP32 with a temperature sensor + 5v relay
- Read and process live data from the ESP32 thermostat
- Connecting data stream to Power BI (If I get Microsoft dev program access)





📸 Screenshots
![Event Stream](/screenshots/azure-cli-stream.png)

![Device Status](/screenshots/sensorLogger-device.png)

![Module Logs](/screenshots/reader-and-publisher-logs.png)

![system_reader](/screenshots/system-reader.png)

![cloud_publisher](/screenshots/cloud-publisher.png)