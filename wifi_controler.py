# Simple HTTP Server Example
# Control an LED and read a Button using a web browser

import time
import network
import socket
from Robi42Lib.robi42 import Robi42


with Robi42() as r:

    ssid = "Sasnas"
    password = "Carl1234"

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    r.lcd.on()

    # Wait for connect or fail
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        r.lcd.clear()
        r.lcd.putstr(f"Waiting for connection {max_wait}")
        time.sleep(1)

    # Handle connection error
    if wlan.status() != 3:
        r.lcd.clear()
        r.lcd.putstr("Connection failed")
        exit()

    r.lcd.clear()
    r.lcd.putstr("Connected")
    status = wlan.ifconfig()
    r.lcd.clear()
    r.lcd.putstr(str(status[0]))

    # Open socket
    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)
    r.lcd.clear()
    r.lcd.putstr(f"IP: {addr}")

    while True:

        try:
            cl, addr = s.accept()
            r.lcd.clear()
            r.lcd.putstr(f"Cnctd: {addr[0]}")
            request = cl.recv(1024)
            print("--------request---------")
            print(request.decode("utf-8"))
            print("-----end of request-----")
            
            try:
                request = str(request)
                command = request[7: request.index(" HTTP")].replace("%5C", "\n")
            except Exception:
                continue

            # Create and send response
            exec(f"{command}", globals(), locals())
            cl.send("HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n")
            cl.close()

        except OSError as e:
            cl.close()
            print("connection closed")
