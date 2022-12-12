import socket
import network
import time
import _thread


class HttpServer:
    def __init__(self, ssid, pswd):

        self.request_response = {"": "Default interface"}

        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(ssid, pswd)

        # Wait for connect or fail
        for _ in range(5):
            if wlan.status() < 0 or wlan.status() >= 3:
                break
            time.sleep(1)

        # Handle connection error
        if wlan.status() != 3:
            raise RuntimeError("wifi connection failed")

        self.ip = wlan.ifconfig()[0]

    def _open_socket(self):
        address = (self.ip, 80)
        connection = socket.socket()
        connection.bind(address)
        connection.listen(1)
        self.connection = connection

    def edit_response_html(self, request, response):
        self.request_response[request] = response

    def start_serving(self):
        _thread.start_new_thread(self._serve, ())

    def _serve(self):
        self._open_socket()
        while True:
            print("1")
            client = self.connection.accept()[0]
            request = client.recv(1024)
            request = str(request)
            try:
                request = request.split()[1]
            except IndexError:
                pass

            if request in self.request_response:
                html = self.request_response[request]
            else:
                html = self.request_response[""]

            client.send(html)
            client.close()
