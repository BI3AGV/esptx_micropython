import socket
import json
from  esp32 import NVS
import random
import machine
# 创建套接字对象
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
config=NVS('PAGERCONFIG') # spacename是命名空间，也就是实例化的开辟了一个叫spacename的存储空间
confList = ['BOOT_MODE','debug_ssid','debug_passwd','wifi_ssid','wifi_passwd','mqtt_server',"mqtt_username",'mqtt_passwd','mqtt_topic','freq','addr','mqtt_tls','mqtt_port','callsign']
#寻呼机相位，默认为负可呼响大顾问，如果没反应改为0
phrase = 1
#MQTT客户端名称，默认生成随机数代替，可不修改
CLIENT_ID = 'micropython-client-{id}'.format(id = random.getrandbits(8))
#检查NVS中的键值对,如果不存在就设置为-
for conf in confList:
    buf = bytearray(128)
    try:
        config.get_blob(conf,buf)
    except Exception as e:
        config.set_blob(conf,'-')
def getConfig(con):
    buf = bytearray(128)
    config.get_blob(con,buf)
    return buf.decode('utf-8').replace(u'\u0000','')

callsign = getConfig('callsign')
freqList = getConfig('freq').split(",")
if "-" in freqList:
    freqList.clear()
addrList = getConfig('addr').split(",")
if '-' in addrList:
    addrList.clear()
TOPIC = getConfig('mqtt_topic').split(",")
if "-" in TOPIC:
    TOPIC.clear()
SERVER = getConfig('mqtt_server')
p = getConfig('mqtt_port')
if p != '-':
    PORT = eval(p)
else:
    PORT = 0
USERNAME = getConfig('mqtt_username')
PASSWORD = getConfig('mqtt_passwd')
if getConfig('mqtt_tls') != '1':
    ENABLE_SSL = 0
else:
    ENABLE_SSL = 1
ssid = getConfig('wifi_ssid')
configSSID = getConfig('debug_ssid')

password = getConfig('wifi_passwd')
if password == '-':
    password = '12345678'
s = getConfig('debug_passwd')
if s != "-":
    configPasswd = s
else:
    configPasswd = "12345678"
    
def startTCPServer():
    # 服务器的IP地址和端口号
    server_ip = "0.0.0.0"
    server_port = 5050
    # 绑定IP地址和端口号
    sock.bind((server_ip, server_port))

def startTCPListen():
    global config
    while True:
        # 监听连接
        sock.listen(1)
        print("等待客户端连接...")

        # 接受客户端连接
        client_sock, client_addr = sock.accept()
        print("客户端已连接:", client_addr)

        # 接收客户端发送的数据
        data = client_sock.recv(1024).decode()
        conf_dict = json.loads(data)
        if conf_dict['type'] == 'config':
            for con in conf_dict['content'].keys():
                if con != 'BOOT_MODE':
                    config.set_blob(con,conf_dict['content'][con])
            client_sock.sendall(b'CONFIG OK')
            config.set_blob('BOOT_MODE','STA')
            machine.reset()
        elif conf_dict['type'] == 'get':
            content = {}
            for con in confList:
                buf = bytearray(128)
                config.get_blob(con,buf)
                content[con] = buf.decode('utf-8').replace(u'\u0000','')
            result = json.dumps(content)
            client_sock.sendall(result.encode('utf-8'))
        elif conf_dict['type'] == 'esp32_shakehands':
            client_sock.sendall(b'HEADER OK')
        else:
            client_sock.sendall(b'UNKNOW COMMAND')
        # 关闭客户端套接字
        client_sock.close() 
