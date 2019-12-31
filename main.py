import time
from machine import UART
import adafruit_gps


uart = UART(1, 9600) 
uart.init(38400, bits=8, parity=None, stop=1)

gps = adafruit_gps.GPS(uart, debug=False)

gps.send_command(b'PMTK314,1,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')

gps.send_command(b'PMTK220,1000')

last_print = time.time()
while True:

    gps.update()

    current = time.time()
    if current - last_print >= 1.0:
        last_print = current
        if not gps.has_fix:
            print('Waiting for fix...')
            continue
        print('=' * 40)  # Print a separator line.
        print('Latitude: {0:.6f} degrees'.format(gps.latitude))
        print('Longitude: {0:.6f} degrees'.format(gps.longitude))