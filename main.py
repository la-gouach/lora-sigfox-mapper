import pycom
import time
import adafruit_gps
from machine import Pin, UART, SD
import os

pycom.heartbeat(False)

button = Pin('P10', mode=Pin.IN, pull=Pin.PULL_UP)
uart = UART(1, 38400, bits=8, parity=None, stop=1, pins=('P20', 'P21')) 
uart.init(38400, bits=8, parity=None, stop=1, pins=('P20', 'P21'))
sd = SD()
os.mount(sd, '/')
print(os.listdir('/'))

BLACK = 0x000000
RED = 0x7f0000
GREEN = 0x007f00
BLUE = 0x00007f
YELLOW = RED | GREEN

try:
    with open('/log.txt', 'r') as f:
        print(f.read())
except Exception as read_exception:
    print('Error while opening /log.txt in read mode:', read_exception)
    try:
        print('Initializing /log.txt with the CSV header')
        with open('/log.txt', 'w') as f:
            f.write('time,longitude,latitude\n')
    except Exception as write_exception:
        print('Error while opening /log.txt in write mode:', write_exception)        



while True:

    gps = adafruit_gps.GPS(uart, debug=False)
    print('Waiting for button')
    while button():
        time.sleep(0.1)
    print('Button has been pressed. Connecting to the GPS')
    pycom.rgbled(YELLOW)
    gps.send_command(b'PMTK314,1,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
    gps.send_command(b'PMTK220,1000')
    while gps.latitude is None or gps.longitude is None or not gps.datetime.is_set:
        gps.update()
    pycom.rgbled(GREEN)
    print('GPS found.')
    print('Position: ', gps.longitude, ', ', gps.latitude)
    time.sleep(1)
    pycom.rgbled(BLACK)
    try:
        with open('/log.txt', 'a') as f:
            f.write('{},{},{}\n'.format(gps.datetime.to_iso(), gps.longitude, gps.latitude))
    except Exception as e:
        print('Error while opening/writing /log.txt in append mode:', e)

