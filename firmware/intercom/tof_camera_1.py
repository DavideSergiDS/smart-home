import sensor
import time
import network
import socket

SSID = "FRITZ!BOX 7530 VZ"  # Network SSID
KEY = "ciaociao1"  # Network key
HOST = ""  # Use first available interface
PORT = 8080  # Arbitrary non-privileged port

### Host
PORT = 443
HOST = "api.telegram.org"
TELEGRAM_BOT_TOKEN = "7441382040:AAG-cv8xOXzhyCfS8AqgbiA0P2xyueuWvds"
TELEGRAM_CHANNEL_ID = "AriglianoHomeChannelId"

# Init wlan module and connect to network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, KEY)

while not wlan.isconnected():
    print('Trying to connect to "{:s}"...'.format(SSID))
    time.sleep_ms(1000)

# We should have a valid IP now via DHCP
print("WiFi Connected ", wlan.ifconfig())



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


# Init sensor
sensor.reset()
sensor.set_framesize(sensor.QVGA)
sensor.set_pixformat(sensor.RGB565)

def start_streaming(s):
    print("Waiting for connections..")
    client, addr = s.accept()
    # set client socket timeout to 5s
    client.settimeout(5.0)
    print("Connected to " + addr[0] + ":" + str(addr[1]))

    # Read request from client
    data = client.recv(1024)
    # Should parse client request here

    # Send multipart header
    client.sendall(
        "HTTP/1.1 200 OK\r\n"
        "Server: OpenMV\r\n"
        "Content-Type: multipart/x-mixed-replace;boundary=openmv\r\n"
        "Cache-Control: no-cache\r\n"
        "Pragma: no-cache\r\n\r\n"
    )

    # FPS clock
    clock = time.clock()

    # Start streaming images
    # NOTE: Disable IDE preview to increase streaming FPS.
    while True:
        clock.tick()  # Track elapsed milliseconds between snapshots().
        frame = sensor.snapshot()
        cframe = frame.to_jpeg(quality=35, copy=True)
        header = (
            "\r\n--openmv\r\n"
            "Content-Type: image/jpeg\r\n"
            "Content-Length:" + str(cframe.size()) + "\r\n\r\n"
        )
        client.sendall(header)
        client.sendall(cframe)
        print(clock.fps())


while True:
    try:
        start_streaming(s)
    except OSError as e:
        print("socket error: ", e)
        # sys.print_exception(e)
