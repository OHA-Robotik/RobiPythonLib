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

        assert wlan.isconnected(), "Failed to connect to wifi"

        sta_if = network.WLAN(network.STA_IF)

        self.ip = sta_if.ifconfig()[0]

    def _open_socket(self):
        address = socket.getaddrinfo(self.ip, 80)[0][-1]
        connection = socket.socket()
        connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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


if __name__ == "__main__":
    h = HttpServer("Sasnas", "Carl1234")
    h.start_serving()
    h.edit_response_html("hello", "HELLO")
