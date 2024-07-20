from  esp32 import NVS

config=NVS('PAGERCONFIG') # spacename是命名空间，也就是实例化的开辟了一个叫spacename的存储空间
confList = ['BOOT_MODE','debug_ssid','debug_passwd','wifi_ssid','wifi_passwd','mqtt_server',"mqtt_username",'mqtt_passwd','mqtt_topic','freq','addr','mqtt_tls','mqtt_port','callsign']

for conf in confList:
    config.set_blob(conf,'-')
        