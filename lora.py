from network import LoRa
import socket
import time
import ubinascii
import pycom
from PRIVATE import LORA_APP_EEUI, LORA_APP_KEY

# setup led
pycom.heartbeat(False)
pycom.rgbled(0x007f00)

lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)

# create an OTAA authentication parameters
app_eui = ubinascii.unhexlify(LORA_APP_EEUI)
app_key = ubinascii.unhexlify(LORA_APP_KEY)

# join a network using OTAA (Over the Air Activation)
lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)

# wait until the module has joined the network
while not lora.has_joined():
    time.sleep(2.5)
    print('Not yet joined...')

print(joined)
# create a LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

# set the LoRaWAN data rate
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)

def lora_cb(lora):
    events = lora.events()
    if events & LoRa.RX_PACKET_EVENT:
        print('Lora packet received')
    if events & LoRa.TX_PACKET_EVENT:
        print('Lora packet sent')

lora.callback(trigger=(LoRa.RX_PACKET_EVENT | LoRa.TX_PACKET_EVENT), handler=lora_cb)

# make the socket blocking
# (waits for the data to be sent and for the 2 receive windows to expire)
s.setblocking(True)
# send some bytes
pycom.rgbled(0x7f7f00) # yellow
try:
    s.send(bytes([0x01, 0x02, 0x03]))
    pycom.rgbled(0x007f00) # green
    time.sleep(1)
except:
    pycom.rgbled(0x7f0000) # red
    time.sleep(1)

s.setblocking(False)

# get any data received (if any...)
data = s.recv(64)
print(data)
if data:
    pycom.rgbled(0x007f00) # green
else:
    pycom.rgbled(0x7f0000) # red
print(sigfox.rssi())

s.close()