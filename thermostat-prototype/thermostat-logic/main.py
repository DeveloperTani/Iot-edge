from machine import Pin, SPI
import machine
import time
import dht
import network
import socket
import json
import uselect
import ntptime
import ssd1306
from umqtt.robust import MQTTClient


# ----------------- CONFIG -----------------
def load_config():
    try:
        with open("config.json") as f:
            return json.load(f)
    except Exception as e:
        print("Failed to load config.json:", e)
        raise

def save_config(cfg):
    try:
        with open("config.json", "w") as f:
            json.dump(cfg, f)
    except Exception as e:
        print("Failed to save config:", e)

config = load_config()

# WiFi & MQTT setup
SSID = config["wifi"]["ssid"]
PASSWORD = config["wifi"]["password"]
MQTT_BROKER = config["mqtt"]["broker"]
MQTT_PORT = config["mqtt"]["port"]
MQTT_TOPIC = config["mqtt"]["topic_status"]
MQTT_CMD_TOPIC = config["mqtt"]["topic_cmd"]
DEVICE_ID = config["mqtt"]["device_id"]

# Thermostat settings
TARGET_TEMP = config.get("target_temp", 22)
READ_INTERVAL = config.get("read_interval", 5)
MIN_TEMP = config.get("min_temp", 10)
MAX_TEMP = config.get("max_temp", 35)

# ----------------- SENSOR + RELAY SETUP -----------------
sensor = dht.DHT22(Pin(2))
relay = Pin(4, Pin.OUT)

heating_state = "OFF"
last_read_time = 0
temp = 0.0
humidity = 0.0

# ----------------- OLED DISPLAY SETUP (SPI) -----------------
spi = SPI(1, baudrate=1000000, polarity=0, phase=0, sck=Pin(0), mosi=Pin(1))
dc = Pin(6)    # Data/Command
res = Pin(10)  # Reset
cs = Pin(7)    # Chip Select

oled = ssd1306.SSD1306_SPI(128, 64, spi, dc, res, cs)

# ----------------- DISPLAY FUNCTION -----------------
def update_display(current_temp, target_temp, heating):
    oled.fill(0)
    oled.text("Temp:      {:.1f}C".format(current_temp), 0, 0)
    oled.text("Target:      {}C".format(target_temp), 0, 12)
    oled.text("Heating:     {}".format(heating), 0, 24)

    t = time.localtime()
    oled.text("      {:02}:{:02}".format(t[3], t[4]), 0, 48)
    oled.show()

# ----------------- NETWORK -----------------
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
        print("NTP sync failed:", e)

# ----------------- MQTT -----------------
def on_mqtt_message(topic, msg):
    global TARGET_TEMP
    try:
        data = json.loads(msg)
        cmd = data.get("cmd")
        print("MQTT command received:", cmd)

        if cmd == "increase" and TARGET_TEMP < MAX_TEMP:
            TARGET_TEMP += 1
        elif cmd == "decrease" and TARGET_TEMP > MIN_TEMP:
            TARGET_TEMP -= 1
        elif cmd == "set":
            value = int(data.get("value", 0))
            if MIN_TEMP <= value <= MAX_TEMP:
                TARGET_TEMP = value
            else:
                print("Invalid temp value:", value)
                return
        else:
            print("Unknown command:", cmd)
            return

        config["target_temp"] = TARGET_TEMP
        save_config(config)
        print("Updated target temp:", TARGET_TEMP)

    except Exception as e:
        print("Error in MQTT message:", e)

def setup_mqtt():
    try:
        mqtt_cfg = config["mqtt"]
        broker = mqtt_cfg["broker"]
        port = mqtt_cfg.get("port", 8883 if mqtt_cfg.get("tls") else 1883)
        use_tls = mqtt_cfg.get("tls", False)
        username = mqtt_cfg.get("username", None)
        password = mqtt_cfg.get("password", None)

        ssl_params = {"server_hostname": broker} if use_tls else None

        client = MQTTClient(
            client_id=DEVICE_ID,
            server=broker,
            port=port,
            user=username,
            password=password,
            ssl=use_tls,
            ssl_params=ssl_params
        )

        client.set_callback(on_mqtt_message)
        client.connect()
        client.subscribe(MQTT_CMD_TOPIC.encode())
        print("MQTT connected with{} TLS on port {}".format("" if use_tls else "out", port))
        return client

    except Exception as e:
        print("MQTT setup failed:", e)
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

# ----------------- MAIN -----------------
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

while True:
    try:
        now = time.time()

        if now - last_read_time >= READ_INTERVAL:
            sensor.measure()
            temp = sensor.temperature()
            humidity = sensor.humidity()

            if temp < TARGET_TEMP:
                relay.value(1)
                heating_state = "ON"
            else:
                relay.value(0)
                heating_state = "OFF"

            print("Temp:", temp, "| Humidity:", humidity, "| Heating:", heating_state)
            update_display(temp, TARGET_TEMP, heating_state)

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
                    config["target_temp"] = TARGET_TEMP
                    save_config(config)
                    response = json_response({"status": "ok", "message": "Target increased", "target_temp": TARGET_TEMP})
                else:
                    response = json_response({"status": "error", "message": f"Max temperature is {MAX_TEMP}°C"}, "400 Bad Request")

            elif "GET /decrease" in request:
                if TARGET_TEMP > MIN_TEMP:
                    TARGET_TEMP -= 1
                    config["target_temp"] = TARGET_TEMP
                    save_config(config)
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
                        config["target_temp"] = TARGET_TEMP
                        save_config(config)
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
        time.sleep(10)



