from machine import Pin, ADC, I2C
from I2C_LCD import I2CLcd
import time
import math
import network
import urequests
import secrets

activeBuzzer = Pin(15, Pin.OUT)
activeBuzzer.value(0)

adc = ADC(26)  # Pin to thermistor
trig = Pin(19, Pin.OUT)
echo = Pin(18, Pin.IN)

tenK = 10000  # 10k resistor
betaC = 3950  # Beta coefficient
KT = 25 + 273.15  # Kelvin temp reference
VCC = 3.3  # 3.3 Volt
soundVelocity = 340  # m/s

# I2C LCD
i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=400000)
devices = i2c.scan()

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secrets.ssid, secrets.password)

while not wlan.isconnected():
    time.sleep(1)

if not devices:
    print("No I2C address found")
    lcd = None
else:
    lcd = I2CLcd(i2c, devices[0], 2, 16)
    lcd.putstr("Init OK...")

def getDistance():
    trig.value(0)
    time.sleep_us(2)
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)
    while echo.value() == 0:
        pass
    pingStart = time.ticks_us()
    while echo.value() == 1:
        pass
    pingStop = time.ticks_us()
    duration = time.ticks_diff(pingStop, pingStart)
    # Convert to cm (speed of sound is 0.0343 cm/us)
    distance = (duration * 0.0343) / 2
    return distance

def getTemp():
    adcValue = adc.read_u16()
    voltage = adcValue / 65535.0 * VCC
    if (VCC - voltage) == 0:
        Rt = tenK
    else:
        Rt = tenK * voltage / (VCC - voltage)
    tempK = 1 / (1 / KT + (math.log(Rt / tenK)) / betaC)
    tempC = tempK - 273.15
    return adcValue, voltage, tempC

def sendData(data):
    url = "http://192.168.50.154:5000/api/data"
    try:
        response = urequests.post(url, json=data)
        print(response.text)
    except Exception as e:
        print("Error: ", e)

time.sleep(2)

while True:
    distance = getDistance()
    adcValue, voltage, tempC = getTemp()
    print("Distance: %.2f cm | ADC value: %d | Voltage: %.2f V | Temperature: %.2f C" %
          (distance, adcValue, voltage, tempC))
    if lcd:
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr("Dist: %.1fcm" % distance)
        lcd.move_to(0, 1)
        lcd.putstr("Temp: %.1fC" % tempC)
    data = {
        "distance": distance,
        "adc_value": adcValue,
        "voltage": voltage,
        "temperature": tempC
    }
    sendData(data)
    time.sleep(10)
