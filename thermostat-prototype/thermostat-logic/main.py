import machine
import time
import dht
import network
import socket
import json
import uselect
import ntptime
from umqtt.simple import MQTTClient

def load_wifi_credentials():
    try:
        with open("wifi.json") as f:
            creds = json.load(f)
            print("Loaded Wi-Fi config:", creds)
            return creds["ssid"], creds["password"]
    except Exception as e:
        print("Failed to load wifi.json, using fallback:", e)
        return "your-wifi-SSID", "your-password" # Add fallback credentials

SSID, PASSWORD = load_wifi_credentials()

# MQTT settings
MQTT_BROKER = ""  
MQTT_PORT = 1883
MQTT_TOPIC = "iot/esp32c3/status"
MQTT_CMD_TOPIC = "iot/esp32c3/cmd"
DEVICE_ID = "esp32c3-01"

# Sensor and control setup
sensor = dht.DHT22(machine.Pin(4))
relay = machine.Pin(10, machine.Pin.OUT)

def load_config():
    try:
        with open("config.json") as f:
            config = json.load(f)
            return config.get("target_temp", 28)
    except Exception as e:
        print("Failed to load config.json, using default:", e)
        return 22

def save_config(target_temp):
    try:
        with open("config.json", "w") as f:
            json.dump({"target_temp": target_temp}, f)
    except Exception as e:
        print("Failed to save config:", e)

TARGET_TEMP = load_config()

heating_state = "OFF"
last_read_time = 0
READ_INTERVAL = 30
MIN_TEMP = 10
MAX_TEMP = 35

def connect_wifi(ssid, password, timeout=60):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.config(dhcp_hostname='esp32c3')

    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(ssid, password)
        for i in range(timeout):
            if wlan.isconnected():
                break
            print(f"Waiting for connection... ({i+1}/{timeout})")
            time.sleep(1)

    if wlan.isconnected():
        print("Connected! IP:", wlan.ifconfig()[0])
        return True
    else:
        print("Failed to connect.")
        return False

def sync_time():
    try:
        ntptime.settime()
        print("Time synced from NTP.")
    except Exception as e:
        print("⚠️ NTP sync failed:", e)


def on_mqtt_message(topic, msg):
    global TARGET_TEMP
    try:
        data = json.loads(msg)
        cmd = data.get("cmd")
        print("MQTT command received:", cmd)

        if cmd == "increase" and TARGET_TEMP < MAX_TEMP:
            TARGET_TEMP += 1
            save_config(TARGET_TEMP)
            print("Increased target temp to", TARGET_TEMP)

        elif cmd == "decrease" and TARGET_TEMP > MIN_TEMP:
            TARGET_TEMP -= 1
            save_config(TARGET_TEMP)
            print("Decreased target temp to", TARGET_TEMP)

        elif cmd == "set":
            value = int(data.get("value", 0))
            if MIN_TEMP <= value <= MAX_TEMP:
                TARGET_TEMP = value
                save_config(TARGET_TEMP)
                print("Set target temp to", TARGET_TEMP)
            else:
                print("Invalid temp value:", value)

        else:
            print("Unknown command:", cmd)

    except Exception as e:
        print("Error in MQTT message:", e)

def setup_mqtt():
    try:
        client = MQTTClient(DEVICE_ID, MQTT_BROKER, port=MQTT_PORT)
        client.set_callback(on_mqtt_message)
        client.connect()
        client.subscribe(MQTT_CMD_TOPIC.encode())
        print("MQTT connected and subscribed.")
        return client
    except Exception as e:
        print("MQTT connection failed:", e)
        return None

def publish_mqtt(client, topic, payload):
    try:
        if client:
            client.publish(topic, payload)
    except Exception as e:
        print("MQTT publish error:", e)

def get_status_payload(temp, humidity, heating_state):
    timestamp = time.localtime()
    return json.dumps({
        "device_id": DEVICE_ID,
        "timestamp": "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}Z".format(*timestamp[:6]),
        "temperature": temp,
        "humidity": humidity,
        "heating": heating_state,
        "target_temp": TARGET_TEMP
    })

def json_response(data, status="200 OK"):
    return (
        f"HTTP/1.1 {status}\r\n"
        "Content-Type: application/json; charset=utf-8\r\n\r\n" +
        json.dumps(data)
    )

# ---- Start execution ----
if not connect_wifi(SSID, PASSWORD):
    raise RuntimeError("Wi-Fi connection failed.")

sync_time()

mqtt = setup_mqtt()

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
server = socket.socket()
server.bind(addr)
server.listen(1)
server.setblocking(False)
poller = uselect.poll()
poller.register(server, uselect.POLLIN)
print("Web server running on http://{}".format(addr))

temp = None
humidity = None

while True:
    try:
        now = time.time()

        if now - last_read_time >= READ_INTERVAL:
            sensor.measure()
            temp = sensor.temperature()
            humidity = sensor.humidity()

            heating_state = "ON" if temp < TARGET_TEMP else "OFF"
            relay.value(1 if heating_state == "ON" else 0)

            print("Temp:", temp, "| Humidity:", humidity, "| Heating:", heating_state)

            payload = get_status_payload(temp, humidity, heating_state)
            publish_mqtt(mqtt, MQTT_TOPIC, payload)
            last_read_time = now

        if mqtt:
            mqtt.check_msg()

        events = poller.poll(0)
        for sock, _ in events:
            conn, addr = server.accept()
            request = conn.recv(1024).decode("utf-8")
            print("Request:", request.split("\r\n")[0])

            if "GET /status" in request:
                response = json_response(json.loads(get_status_payload(temp, humidity, heating_state)))

            elif "GET /increase" in request:
                if TARGET_TEMP < MAX_TEMP:
                    TARGET_TEMP += 1
                    save_config(TARGET_TEMP)
                    response = json_response({"status": "ok", "message": "Target increased", "target_temp": TARGET_TEMP})
                else:
                    response = json_response({"status": "error", "message": f"Max temperature is {MAX_TEMP}°C"}, "400 Bad Request")

            elif "GET /decrease" in request:
                if TARGET_TEMP > MIN_TEMP:
                    TARGET_TEMP -= 1
                    save_config(TARGET_TEMP)
                    response = json_response({"status": "ok", "message": "Target decreased", "target_temp": TARGET_TEMP})
                else:
                    response = json_response({"status": "error", "message": f"Min temperature is {MIN_TEMP}°C"}, "400 Bad Request")

            elif "GET /set" in request and "temp=" in request:
                try:
                    query = request.split(' ')[1]
                    temp_part = query.split('temp=')[1].split('&')[0]
                    new_temp = int(temp_part)
                    if MIN_TEMP <= new_temp <= MAX_TEMP:
                        TARGET_TEMP = new_temp
                        save_config(TARGET_TEMP)
                        response = json_response({"status": "ok", "message": "Target set", "target_temp": TARGET_TEMP})
                    else:
                        response = json_response({"status": "error", "message": f"Temperature must be between {MIN_TEMP} and {MAX_TEMP}°C"}, "400 Bad Request")
                except:
                    response = json_response({"status": "error", "message": "Invalid temperature format"}, "400 Bad Request")

            else:
                response = json_response({"status": "error", "message": "Unknown command"}, "404 Not Found")

            conn.send(response)
            conn.close()

    except Exception as e:
        print("Loop error:", e)
        time.sleep(5)



