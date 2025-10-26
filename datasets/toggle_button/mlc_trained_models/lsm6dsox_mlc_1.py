# This work is licensed under the MIT license.
# Copyright (c) 2013-2023 OpenMV LLC. All rights reserved.
# https://github.com/openmv/openmv/blob/master/LICENSE
#
# LSM6DSOX IMU MLC (Machine Learning Core) Example.
# Download the raw UCF file, copy to storage and reset.

# NOTE: The pre-trained models (UCF files) for the examples can be found here:
# https://github.com/STMicroelectronics/STMems_Machine_Learning_Core/tree/master/application_examples/lsm6dsox
import network
import urequests
from machine import Pin
from machine import SPI
from lsm6dsox import LSM6DSOX
import sensor
import time
import machine

# Leds
led_blue = machine.LED("LED_BLUE")
led_red = machine.LED("LED_RED")
led_green = machine.LED("LED_GREEN")

# Network and Telegram settings

### AP info
SSID = "iPhone (2)"  # Network SSID
KEY = "ciaociao"  # Network key
#SSID = "FRITZ!Box 7530 VZ"
#KEY = "ciaociao1"

### Host
PORT = 443
HOST = "api.telegram.org"
TELEGRAM_BOT_TOKEN = "7441382040:AAG-cv8xOXzhyCfS8AqgbiA0P2xyueuWvds"
TELEGRAM_CHANNEL_ID = "AriglianoHomeChannelId"

### Initialize Wi-Fi connection
wifi = network.WLAN(network.STA_IF)
wifi.active(True)

### Wait for connection
while not wifi.isconnected():
    res = wifi.connect(SSID, KEY, channel=6)
    print(res)
    led_red.toggle()
    time.sleep(1)

led_red.off()
led_green.on()

# Set camera sensor settings
sensor.reset()  # Reset and initialize the sensor.
sensor.set_pixformat(sensor.RGB565)  # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.QVGA)  # Set frame size to QVGA (320x240)
sensor.skip_frames(time=2000)  # Wait for settings take effect.

INT_MODE = True  # Run in interrupt mode.
INT_FLAG = False  # Set True on interrupt.

def imu_int_handler(pin):
    global INT_FLAG
    INT_FLAG = True


if INT_MODE is True:
    int_pin = Pin("PA1", mode=Pin.IN, pull=Pin.PULL_UP)
    int_pin.irq(handler=imu_int_handler, trigger=Pin.IRQ_RISING)

# Vibration detection example
UCF_FILE = "mlc_experiments_toggle_button_LSM6DSV16X_mlc.ucf"
UCF_LABELS = {0: "idle", 4: "toggle"}
# NOTE: Selected data rate and scale must match the MLC data rate and scale.
lsm = LSM6DSOX(
    SPI(5),
    cs=Pin("PF6", Pin.OUT_PP, Pin.PULL_UP),
    gyro_odr=26,
    accel_odr=26,
    gyro_scale=2000,
    accel_scale=4,
    ucf=UCF_FILE,
)

def sendMessage():
    global TELEGRAM_CHANNEL_ID
    global TELEGRAM_BOT_TOKEN

    led_green.on()
    # Prepare the multipart form data
    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
    multipart_data = (
        '--' + boundary + '\r\n' +
        'Content-Disposition: form-data; name="chat_id"\r\n\r\n' +
        TELEGRAM_CHANNEL_ID + '\r\n' +
        '--' + boundary + '\r\n' +
        'Content-Disposition: form-data; name="caption"\r\n\r\n' +
        'Nicla Vision\r\n' +
        '--' + boundary + '\r\n' +
        'Content-Disposition: form-data; name="photo"; filename="snapshot.jpg"\r\n' +
        'Content-Type: image/jpeg\r\n\r\n' +
        open('/snapshot.jpg', 'rb').read() + '\r\n' +
        '--' + boundary + '--\r\n'
    )

    # Send the HTTP POST request
    url = 'https://api.telegram.org/bot'+TELEGRAM_BOT_TOKEN+'/sendPhoto'
    headers = {
        'Content-Type': 'multipart/form-data; boundary=' + boundary
    }
    response = urequests.post(url, headers=headers, data=multipart_data)

    # Print the response
    print(response.text)

    # Close the response
    response.close()

    led_green.off()


print("MLC configured...")

while True:
    if INT_MODE:
        if INT_FLAG:
            INT_FLAG = False
            print(UCF_LABELS[lsm.mlc_output()[0]])
            if(lsm.mlc_output()[0] == 4):
                i = 0;
                while(i < 3):
                    led.toggle()
                    time.sleep(1)
                    i = i + 1
                led.off()
                # Capture an image
                img = sensor.snapshot()
                img.save("/snapshot.jpg")
                # sendMessage()
    else:
        buf = lsm.mlc_output()
        if buf is not None:
            print(UCF_LABELS[buf[0]])
            if(buf[0] == 4):
                i = 0;
                while(i < 3):
                    led.toggle()
                    time.sleep(1)
                    i = i + 1
                led.off()
                # Capture an image
                img = sensor.snapshot()
                img.save("/snapshot.jpg")
                # sendMessage()
