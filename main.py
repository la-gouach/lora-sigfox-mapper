import pycom
import time
from machine import Pin, UART, SD
import os
from machine import WDT

pycom.heartbeat(False)
wdt = WDT(timeout=15*60*1000)

button = Pin('P10', mode=Pin.IN, pull=Pin.PULL_UP)
time.sleep(0.1)

import adafruit_gps
from network import Sigfox, LoRa
import socket
import ubinascii
from PRIVATE import LORA_APP_EEUI, LORA_APP_KEY

uart = UART(1, 38400, bits=8, parity=None, stop=1, pins=('P20', 'P21')) 
uart.init(38400, bits=8, parity=None, stop=1, pins=('P20', 'P21'))
sigfox = Sigfox(mode=Sigfox.SIGFOX, rcz=Sigfox.RCZ1)
lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)
sd = SD()
os.mount(sd, '/')
print(os.listdir('/'))

LOG_FILE = '/log.txt'

BLACK = 0x000000
RED = 0x7f0000
GREEN = 0x007f00
BLUE = 0x00007f
YELLOW = RED | GREEN
PURPLE = BLUE | RED
WHITE = RED | BLUE | GREEN

def emit_sigfox_downlink():
    pycom.rgbled(PURPLE)
    sigfox_socket = socket.socket(socket.AF_SIGFOX, socket.SOCK_RAW)
    sigfox_socket.setblocking(True)
    sigfox_socket.setsockopt(socket.SOL_SIGFOX, socket.SO_RX, True)

    print('Sending sigfox packet...')
    tx_success = False
    rx_success = False
    rssi = 0
    try:
        sigfox_socket.send(bytes([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]))
        print('Success !')
        tx_success = True
        pycom.rgbled(GREEN)
        time.sleep(1)
        print('Receiving downlink...')
        pycom.rgbled(PURPLE)
        received = sigfox_socket.recv(8)
        
        if received:
            print('Success !')
            rx_success = True
            pycom.rgbled(GREEN) # green
        else:
            print('Failure...')
            pycom.rgbled(RED) # red
        rssi = sigfox.rssi()
    except Exception as e:
        print('Failure...')
        print(e)
        pycom.rgbled(RED) 
        time.sleep(1)
        pycom.rgbled(BLACK)
    time.sleep(1)
    pycom.rgbled(BLACK)
    sigfox_socket.close()
    return tx_success, rx_success, int(rssi)

def emit_lora_packet():
    # create an OTAA authentication parameters
    app_eui = ubinascii.unhexlify(LORA_APP_EEUI)
    app_key = ubinascii.unhexlify(LORA_APP_KEY)

    print('Joining the LoRaWan network')
    pycom.rgbled(BLUE)
    # join a network using OTAA (Over the Air Activation)
    tx_success = False
    rx_success = False
    rssi = 0
    try:
        lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=5*60*1000, dr=1)
        while not lora.has_joined(): # TODO: Add timeout
            time.sleep(1)
        print('Joined')
        lora_socket = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

        # set the LoRaWAN data rate
        lora_socket.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)

        def lora_cb(lora):
            events = lora.events()
            if events & LoRa.RX_PACKET_EVENT:
                print('Lora packet received')
            if events & LoRa.TX_PACKET_EVENT:
                print('Lora packet sent')

        lora.callback(trigger=(LoRa.RX_PACKET_EVENT | LoRa.TX_PACKET_EVENT), handler=lora_cb)
        lora_socket.setblocking(True)

        print('Sending packet...')
        pycom.rgbled(BLUE)
        
        try:
            lora_socket.send(bytes([0x01, 0x02, 0x03]))
            tx_success = True
            pycom.rgbled(GREEN)
            print('Success !')
            time.sleep(1)
        except Exception as e:
            pycom.rgbled(RED)
            time.sleep(1)
            print('Failure...')
            prin(e)
        finally:
            pycom.rgbled(BLACK)

        rssi = lora.stats().rssi
        lora_socket.setblocking(False)

        time.sleep(5)
        print('Receiving packet...')
        pycom.rgbled(BLUE)
        # get any data received (if any...)
        data = lora_socket.recv(64)
        if data:
            rx_success = True
            pycom.rgbled(GREEN)
            print('Success !')
            print('Packet received:', data)
        else:
            pycom.rgbled(RED)
            print('Failure...')
        lora_socket.close()

    except Exception as e:
        print(e)
        pass
    time.sleep(1)
    pycom.rgbled(BLACK)

    return tx_success, rx_success, rssi

try:
    with open(LOG_FILE, 'r') as f:
        print(f.read())
except Exception as read_exception:
    print('Error while opening /log.txt in read mode:', read_exception)
    try:
        print('Initializing /log.txt with the CSV header')
        with open(LOG_FILE, 'w') as f:
            f.write('time,longitude,latitude,packet_type,sigfox_tx_success,sigfox_rx_success,sigfox_rssi,lora_tx_success,lora_rx_success,lora_rssi\n')
    except Exception as write_exception:
        print('Error while opening /log.txt in write mode:', write_exception)

while True:
    pycom.rgbled(WHITE)
    wdt.feed()
    print('Connecting to the GPS')
    gps = adafruit_gps.GPS(uart, debug=False)
    gps.send_command(b'PMTK314,1,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
    gps.send_command(b'PMTK220,1000')
    while gps.latitude is None or gps.longitude is None or not gps.datetime.is_set:
        gps.update()
    wdt.feed()
    print('GPS found.')
    print('Position: ', gps.longitude, ', ', gps.latitude)
    time.sleep(1)

    wdt.feed()
    sigfox_tx_success, sigfox_rx_success, sigfox_rssi = emit_sigfox_downlink()
    wdt.feed()
    lora_tx_success, lora_rx_success, lora_rssi = emit_lora_packet()
    wdt.feed()

    # Logging to the SD card
    csv_line = '{},{},{},{},{},{},{},{},{},{}\n'.format(gps.datetime.to_iso(), gps.longitude, gps.latitude,
                                               'downlink',
                                               sigfox_tx_success, sigfox_rx_success, sigfox_rssi,
                                               lora_tx_success,   lora_rx_success,   lora_rssi)
    print('Writing into the log file:', csv_line)
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(csv_line)
    except Exception as e:
        print('Error while opening/writing /log.txt in append mode:', e)
    
    pycom.rgbled(BLACK)
    for i in range(10):
        wdt.feed()
        time.sleep(60)

