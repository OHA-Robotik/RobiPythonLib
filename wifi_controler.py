import urequests
import network

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

ssid = "Sasnas"
password = "Carl1234"
wlan.connect(ssid, password)


print("1. Querying google.com:")
r = urequests.get("http://www.google.com")
print(r.content)
r.close()

print("\n\n2. Querying the current GMT+0 time:")
r = urequests.get("http://date.jsontest.com")
print(r.json())
