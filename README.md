# IoT Edge System + Thermostat Sensor logger

This project is a working prototype of an Azure IoT Edge deployment using a physical Ubuntu laptop as the edge device. It collects and routes telemetry from two sources:

    The laptop’s own system metrics (CPU, memory, disk)

    A custom-built ESP32 thermostat, which receives direct method calls and sends real-time temperature and humidity data over MQTT

Messages are routed through Dockerized modules and sent upstream to Azure IoT Hub, forming the basis for a remote-monitoring, real-time data platform.

You can check out more of the thermostat here: [ESP32 thermostat](./thermostat-prototype/)



🔧 Tech Stack

    Azure IoT Hub + IoT Edge Runtime
    For managing device communication and module orchestration

    Docker + Azure Container Registry (ACR)
    Containerized modules built and deployed via ACR

    Python 3.10-slim
    Lightweight base image for writing and running Edge modules

    ESP32 (MicroPython)
    Custom thermostat hardware that sends telemetry via MQTT and supports remote control through direct methods and REST endpoints.

    Host System: Ubuntu 22.04 (Laptop)
    Acts as the edge gateway device running all modules locally

##  Key Features

- system_reader module collects CPU, memory, and disk usage using psutil and timestamps each entry in UTC ISO format
- thermostat_reader module receives live data from an ESP32 over MQTT and forwards structured payloads
- cloud_publisher module forwards telemetry upstream to Azure IoT Hub using custom-defined routes
- All modules are containerized and deployed to a physical Ubuntu 22.04 host via the Azure IoT Edge runtime
- Images are built and stored in Azure Container Registry (ACR) for deployment

##  Sample Telemetry Payloads

from ESP32 thermostat:
```json
{
{"temperature": 25.8,
 "timestamp": "2025-07-04T00:13:36Z",
 "humidity": 44.9,
 "target_temp": 25,
 "device_id": "esp32c3-01",
 "heating": "OFF"}
}
```

from laptop system reader:
```json
{
  "timestamp": "2025-06-26T18:55:00.363867Z",
  "cpu_usage": 0.0,
  "memory_usage": 6.6,
  "disk_usage": 0.3
}
```

## Future Plans

- Logic separation into multiple modules with custom routes ✅
- Build a custom Wi-fi "thermostat" using an ESP32, temp sensor and a relay ✅
- Read live data from the ESP32 thermostat ✅
- Support direct method invocation from the cloud ✅
- Implement cloud-to-device (C2D) messaging
- Connecting data stream to Power BI (If I get Microsoft dev program access)
- LCD integration on ESP32





## Screenshots
![Event Stream](/screenshots/CLI-stream.png)

![Direct methods](/screenshots/direct-methods.png)

![Device Status](/screenshots/sensorLogger-device.png)

![Module Logs](/screenshots/reader-and-publisher-logs.png)

![thermostat_reader](/screenshots/thermostat_logger.png)

![system_reader](/screenshots/system_reader.png)

![cloud_publisher](/screenshots/cloud_publisher.png)
