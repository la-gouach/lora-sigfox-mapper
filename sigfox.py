from network import Sigfox
import socket
import pycom
import time

# setup led
pycom.heartbeat(False)
pycom.rgbled(0x007f00)

# init Sigfox for RCZ1 (Europe)
sigfox = Sigfox(mode=Sigfox.SIGFOX, rcz=Sigfox.RCZ1)

# create a Sigfox socket
s = socket.socket(socket.AF_SIGFOX, socket.SOCK_RAW)

# make the socket blocking
s.setblocking(True)

# wait for a downlink after sending the uplink packet
s.setsockopt(socket.SOL_SIGFOX, socket.SO_RX, True)

# send some bytes
pycom.rgbled(0x7f7f00) # yellow
try:
    s.send(bytes([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]))
    pycom.rgbled(0x007f00) # green
    time.sleep(1)
except:
    pycom.rgbled(0x7f0000) # red
    time.sleep(1)

received = s.recv(8)
print(received)
if received:
    pycom.rgbled(0x007f00) # green
else:
    pycom.rgbled(0x7f0000) # red
print(sigfox.rssi())
time.sleep(4)


s.close()