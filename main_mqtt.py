import network
import time
from machine import Pin
import dht
import ujson
from umqtt.simple import MQTTClient

# MQTT Server Parameters
MQTT_CLIENT_ID = "my_PC"
MQTT_BROKER = "io.adafruit.com"
MQTT_USER = "name" # Логин
MQTT_PASSWORD = "key_aio" # ключ
MQTT_TOPIC_TEMP = "name/feeds/temperature"
MQTT_TOPIC_COMMAND = "name/feeds/command" 

sensor1 = dht.DHT22(Pin(15))
sensor2 = dht.DHT22(Pin(2))

# WIFI Connection
print("Connecting to WiFi", end="")
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('Wokwi-GUEST', '')  # Убедитесь, что имя сети и пароль правильные
while not sta_if.isconnected():
    print(".", end="")
    time.sleep(0.1)
print(" Connected!")

# MQTT Server connection
print("Connecting to MQTT server... ", end="")
client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, user=MQTT_USER, password=MQTT_PASSWORD)
client.connect()
print("Connected!")

# Функция для обработки команд, пришедших с сайта
def on_message(topic, msg):
    print(f"Received message on topic {topic}: {msg}")
    # Пример команды: если получена команда "on", включаем какое-то устройство
    if msg == b"on":
        print("Turning on the device")
        # Например, включаем какой-то выход или выполняем действие
        # device_pin.value(1)  # если подключено к пину устройства
    elif msg == b"off":
        print("Turning off the device")
        # Отключаем устройство
        # device_pin.value(0)  # если подключено к пину устройства

# Подписка на тему команд с сайта
client.set_callback(on_message)
client.subscribe(MQTT_TOPIC_COMMAND)

# Build the message in JSON format and send the message only if there is a change
prev_weather = ""
while True:
    print("Measuring weather conditions... ", end="")
    sensor1.measure()  # Измерение температуры
    message = ujson.dumps(sensor1.temperature())
    
    if message != prev_weather:
        print("Updated!")
        print("Reporting to MQTT topic {}: {}".format(MQTT_TOPIC_TEMP, message))
        # Отправляем данные на сайт Adafruit IO (тема с температурой)
        client.publish(MQTT_TOPIC_TEMP, message)
        prev_weather = message
    else:
        print("No change")
    
    # Проверка на наличие новых сообщений (команд) с сайта
    client.check_msg()  # Необходимо вызывать, чтобы обрабатывать входящие сообщения

    time.sleep(1)