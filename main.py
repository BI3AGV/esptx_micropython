
from pocsag import *
from CMT2300A import *
from uart import *
import time
from encode import *
import machine
from machine import Timer
import network
import random
import ssl
from umqtt.simple import MQTTClient
from config import *
from tcp import *
import _thread

baseBand = []

WLAN_MODE = getConfig('BOOT_MODE')
if WLAN_MODE == '-':
    config.set_blob('BOOT_MODE','STA')

def DCLK_INT(pin):
    global GPIO2
    global codeCounter
    global bitCounter
    global baseBand
    if codeCounter < len(baseBand):
        byte = baseBand[codeCounter]
        GPIO2.value((byte >> bitCounter) & 0x01)
        if bitCounter == 0:
            bitCounter = 31
            codeCounter += 1
        else:
            bitCounter -= 1
    else:
        codeCounter = 0
        bitCounter = 31
        CMT2300A_Go_IDLE()
        TX.value(0)
        
def callPager(msg):
    global baseBand
    for i in range(len(freqList)):
        CMT2300A_SetFREQ(eval(freqList[i]))
        baseBand = genSignal(eval(addrList[i]),fontbyte.strs(msg))
        CMT2300A_GoTX()
        TX.value(1)
        time.sleep(2+len(baseBand)*16/1200)
        
def startAP():
    ap = network.WLAN(network.AP_IF)
    ap.config(essid=configSSID,password=configPasswd,authmode=network.AUTH_WPA_WPA2_PSK)
    ap.active(True)
    time.sleep(1)
    startTCPServer()
    _thread.start_new_thread(startTCPListen, ())

CMT2300A_Init()
time.sleep(1)
DCLK.irq(trigger=Pin.IRQ_RISING, handler=DCLK_INT)

fontbyte = gb2312()



#使用板载WiFi连接时启用如下代码
'''
#------------------------------------------------------------------------------
def on_message(topic, msg):
    print("Received '{payload}' from topic '{topic}'\n".format(
        payload = msg.decode(), topic = topic.decode()))
    callPager(msg.decode())

def mqtt_connect():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.verify_mode = ssl.CERT_NONE
    if ENABLE_SSL == 1:
        client = MQTTClient(CLIENT_ID, SERVER, PORT, USERNAME, PASSWORD, ssl = context)
        print("SSL/TLS ENABLED")
    else:
        client = MQTTClient(CLIENT_ID, SERVER, PORT, USERNAME, PASSWORD)
    try:
        client.connect()
        config.set_blob('BOOT_MODE','STA')
    except:
        print("Configuration error!We will reset to AP mode")
        config.set_blob('BOOT_MODE','AP')
        machine.reset()
    print('Connected to MQTT Broker "{server}"'.format(server = SERVER))
    return client

def subscribe(client):
    client.set_callback(on_message)
    for topic in TOPIC:
        client.subscribe(topic)

def loop_publish(client):
    while True:
        try:
            client.wait_msg()
        except OSError as e:
            print(f"{e},Try reconnecting...")
            time.sleep(5)
            client = mqtt_connect()
            subscribe(client)
        time.sleep(1)

    
def wifi_connect():
    counter = 0
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while True:
        print('Waiting for connection...')
        time.sleep(1)
        if wlan.isconnected():
            break
        counter += 1
        if counter > 60:
            config.set_blob('BOOT_MODE','AP')
            machine.reset()
    print('Connected on {ip}'.format(ip = wlan.ifconfig()[0]))
    #callPager(f"CONNECT SUCCESS ON:{wlan.ifconfig()[0]}")
    

if WLAN_MODE == 'AP':
    startAP()
else:
    wifi_connect()
    client = mqtt_connect()
    subscribe(client)
    loop_publish(client)
#----------------------------------------------------------------
'''



#如果使用4G模块启用以下代码

startAP()
lteInit()
mqttConnect()
timer = Timer(0)
timer.init(period=300000, mode=Timer.PERIODIC, callback=lambda t: check())
while True:
    time.sleep(2)
    resp = ser.read()
    if(resp != None):
        try:
            result = resp.decode('utf-8').split("\"")
            if "+MSUB: " in result:
                callPager(result[3])
        except Exception as ex:
            print(ex)
