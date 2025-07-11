# IoT Edge System + Thermostat Sensor Logger

This project features a physical ESP32-based thermostat (running MicroPython), Azure IoT Edge modules (on Linux Ubuntu 22.04), a FastAPI backend connected to Azure IoT Hub, and a React frontend dashboard for easy control.

I have scaled this project up from a single edge module that read system data using psutil to a full scale pipeline from wiring and flashing + programming up my own thermostat to hooking it up to my edge runtime environment to building an api and frontend to support it.

More detailed documentation of each component is coming soon!

**Status (2025-07-11):**  
Both frontend and backend are deployed on Azure.
The backend cloud-based endpoints are not currently in use and data/commands are routed straight API --> MQTT broker --> device and vice versa.

See [ESP32 thermostat](./thermostat-prototype/) for device details.

---
## Data Flow Diagram


![dataflow-diagram](/screenshots/dataflow-diagram.png)

## 🔧 Tech Stack

- Azure IoT Hub + IoT Edge Runtime: Device communication and module orchestration

- Docker + Azure Container Registry (ACR): Containerized modules, built and deployed via ACR

- Python 3.10-slim: Base image for Edge modules

- FastAPI: API backend (secured with OAuth2, connects to Azure IoT Hub, handles device commands & telemetry)

- React + Vite: Frontend dashboard for device status and control

- @azure/msal-browser / @azure/msal-react: MSAL authentication in frontend

- ESP32 (MicroPython): Custom thermostat hardware (MQTT telemetry, direct methods)

- paho-mqtt: MQTT client in Edge modules

- Ubuntu 22.04 (Laptop): Edge host
---

##  Key Features

- `system_reader`: (not in use) Collects system stats using psutil, timestamps in UTC
- `thermostat_reader`: Receives live ESP32 MQTT data, structures payloads
- `cloud_publisher`: Forwards telemetry to IoT Hub using custom routes
- **All modules containerized & deployed to physical Ubuntu host via IoT Edge runtime**
- **API**: Connects to IoT Hub, exposes direct methods as endpoints
- **Images**: Built & stored in Azure Container Registry (ACR)

---

##  Sample Telemetry Payloads

**From ESP32 Thermostat:**
```json
{
  "temperature": 25.8,
  "timestamp": "2025-07-04T00:13:36Z",
  "humidity": 44.9,
  "target_temp": 25,
  "device_id": "esp32c3-01",
  "heating": "OFF"
}

From laptop system reader:

{
  "timestamp": "2025-06-26T18:55:00.363867Z",
  "cpu_usage": 0.0,
  "memory_usage": 6.6,
  "disk_usage": 0.3
}
```


 Future Plans

- ✅Logic separation into multiple modules with custom routes

- ✅Custom ESP32 thermostat (temp sensor + relay)

- ✅Live data from ESP32

- ✅Direct method invocation from the cloud

- API and frontend dashboard for easy control (in progress)

- Power BI integration (if MS dev access comes through)

- ESP32 LCD integration




## Screenshots


![iot-dashboard](/screenshots/iot-dashboard.png)

![Event Stream](/screenshots/CLI-stream.png)

![Direct methods](/screenshots/direct-methods.png)

![Device Status](/screenshots/sensorLogger-device.png)

![Module Logs](/screenshots/reader-and-publisher-logs.png)

![thermostat_reader](/screenshots/thermostat_logger.png)

![system_reader](/screenshots/system_reader.png)

![cloud_publisher](/screenshots/cloud_publisher.png)
