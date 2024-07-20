from machine import UART
import time
from tcp import *
ser=UART(2,115200)
ser.init(115200,bits=8,parity=None,stop=1) # 8N1
def lteInit():

    ser.write(b"AT+RESET\r\n")
    time.sleep(5)
    resp = ser.read()
    print(resp)

    ser.write(b"AT+QICSGP=1,1,\"cmnbiot\",\"\",\"\"\r\n")
    time.sleep(2)
    resp = ser.read()
    print(resp)

    ser.write(b"AT+NETOPEN\r\n")
    time.sleep(5)
    resp = ser.read()
    print(resp)
    
    ser.write(f"AT+MCONFIG=\"{CLIENT_ID}\",\"{USERNAME}\",\"{PASSWORD}\"\r\n".encode('ascii'))
    time.sleep(2)
    resp = ser.read()
    print(resp)
    
    ser.write(f"AT+MQTTSSL={ENABLE_SSL},0\r\n".encode('ascii'))
    time.sleep(2)
    resp = ser.read()
    print(resp)

    ser.write(f"AT+MIPSTART=\"{SERVER}\",{PORT},3\r\n".encode('ascii'))
    time.sleep(5)
    resp = ser.read()
    print(resp)
    
    
def mqttConnect():
    ser.write(b"AT+MCONNECT=0,60\r\n")
    time.sleep(5)
    resp = ser.read()
    print(resp)

    ser.write(b"AT+CEREG?\r\n")
    time.sleep(2)
    resp = ser.read()
    print(resp)
    for topic in TOPIC:
        ser.write(f"AT+MSUB=\"{topic}\",2\r\n".encode('ascii'))
        time.sleep(5)
        resp = ser.read()
        print(resp)


def check():
    ser.write(b"AT+MQTTSTATU\r\n")
    time.sleep(2)
    resp = ser.read()
    if resp != None:
        if b"1" not in resp:
            print("Client disconnected.Retrying...")
            lteInit()
            mqttConnect()
        else:
            print("MQTT Connection Established.")