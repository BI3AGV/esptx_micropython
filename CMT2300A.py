from machine import Pin
import time
from tcp import phrase

GPIO2 = Pin(25,Pin.OUT)
CS = Pin(27, Pin.OUT)
DCLK = Pin(26, Pin.IN)
TX = Pin(13,Pin.OUT)
CLK = Pin(14,Pin.OUT)
CLK.value(0)
DIO = Pin(12,Pin.OUT)
CS.value(1)
codeCounter = 0
bitCounter = 31
TX_ON = 0


        
def SPI_WriteREG(addr,value):
    CS.value(0)
    time.sleep(0.00001)
    DIO = Pin(12,Pin.OUT)
    for i in range(8):
        DIO.value((addr >> (7-i)) & 0x01)
        time.sleep(0.00001)
        CLK.value(1)
        time.sleep(0.00001)
        CLK.value(0)
    for i in range(8):
        DIO.value((value >> (7-i)) & 0x01)
        time.sleep(0.00001)
        CLK.value(1)
        time.sleep(0.00001)
        CLK.value(0)
    DIO.value(0)
    time.sleep(0.00001)
    CS.value(1)
        
def SPI_ReadREG(addr):
    CS.value(0)
    time.sleep(0.00001)
    DIO = Pin(12,Pin.OUT)
    addr = addr | 0b10000000
    for i in range(8):
        DIO.value((addr >> (7-i)) & 0x01)
        time.sleep(0.00001)
        CLK.value(1)
        time.sleep(0.00001)
        if i == 7:
            DIO = Pin(12,Pin.IN)
        CLK.value(0)
    result = 0x00
    for i in range(8):
        CLK.value(1)
        result = result | DIO.value()
        if i != 7:
            result = result << 1
        time.sleep(0.00001)
        CLK.value(0)
        time.sleep(0.00001)
    CS.value(1)
    DIO = Pin(12,Pin.OUT)
    return result



def CMT2300A_Init():
    #复位
    SPI_WriteREG(0x7F,0xFF)
    while SPI_ReadREG(0x61) & 0b00001111 != 0x01:
        pass
        #进入stby模式
    SPI_WriteREG(0x60,0x02)
    while SPI_ReadREG(0x61) & 0b00001111 != 0x02:
        pass
    #
    
    
    #CMT寄存器
    SPI_WriteREG(0x00,0x00)
    SPI_WriteREG(0x01,0x66)
    SPI_WriteREG(0x02,0xec)
    SPI_WriteREG(0x03,0x1c)
    SPI_WriteREG(0x04,0xf0)
    SPI_WriteREG(0x05,0x80)
    SPI_WriteREG(0x06,0x14)
    SPI_WriteREG(0x07,0x08)
    SPI_WriteREG(0x08,0x91)
    SPI_WriteREG(0x09,0x02)
    SPI_WriteREG(0x0a,0x02)
    SPI_WriteREG(0x0b,0xd0)
    
    #系统区寄存器
    SPI_WriteREG(0x0c,0xae)
    SPI_WriteREG(0x0d,0xe0)
    SPI_WriteREG(0x0e,0x35)
    SPI_WriteREG(0x0f,0x00)
    SPI_WriteREG(0x10,0x00)
    SPI_WriteREG(0x11,0xf4)
    SPI_WriteREG(0x12,0x10)
    SPI_WriteREG(0x13,0xe2)
    SPI_WriteREG(0x14,0x42)
    SPI_WriteREG(0x15,0x20)
    SPI_WriteREG(0x16,0x00)
    SPI_WriteREG(0x17,0x81) 
    
    #频率区寄存器
    SPI_WriteREG(0x18,0x00)
    SPI_WriteREG(0x19,0x00)
    SPI_WriteREG(0x1A,0x00)
    SPI_WriteREG(0x1B,0x00)
    SPI_WriteREG(0x1C,0x00)
    SPI_WriteREG(0x1D,0x00)
    SPI_WriteREG(0x1E,0x00)
    SPI_WriteREG(0x1F,0x00)
    
    #数据率寄存器
    SPI_WriteREG(0x20,0x19)
    SPI_WriteREG(0x21,0x0c)
    SPI_WriteREG(0x22,0x00)
    SPI_WriteREG(0x23,0xbb)
    SPI_WriteREG(0x24,0xD0)
    SPI_WriteREG(0x25,0x9b)
    SPI_WriteREG(0x26,0x0B)
    SPI_WriteREG(0x27,0x0a)
    SPI_WriteREG(0x28,0x9f)
    SPI_WriteREG(0x29,0x39)
    SPI_WriteREG(0x2a,0x29)
    SPI_WriteREG(0x2b,0x29)
    SPI_WriteREG(0x2c,0xc0)
    SPI_WriteREG(0x2d,0xa2)
    SPI_WriteREG(0x2e,0x54)
    SPI_WriteREG(0x2f,0x53)
    SPI_WriteREG(0x30,0x00)
    SPI_WriteREG(0x31,0x00)
    SPI_WriteREG(0x32,0xb4)
    SPI_WriteREG(0x33,0x00)
    SPI_WriteREG(0x34,0x00)
    SPI_WriteREG(0x35,0x01)
    SPI_WriteREG(0x36,0x00)
    SPI_WriteREG(0x37,0x00)
    
    #基带寄存器
    SPI_WriteREG(0x38,0x10)
    SPI_WriteREG(0x39,0x08)
    SPI_WriteREG(0x3a,0x00)
    SPI_WriteREG(0x3b,0xaa)
    SPI_WriteREG(0x3c,0x02)
    SPI_WriteREG(0x3d,0x00)
    SPI_WriteREG(0x3e,0x00)
    SPI_WriteREG(0x3f,0x00)
    SPI_WriteREG(0x40,0x00)
    SPI_WriteREG(0x41,0x00)
    SPI_WriteREG(0x42,0x00)
    SPI_WriteREG(0x43,0xd4)
    SPI_WriteREG(0x44,0x2d)
    SPI_WriteREG(0x45,0x00)
    SPI_WriteREG(0x46,0x1F)
    SPI_WriteREG(0x47,0x00)
    SPI_WriteREG(0x48,0x00)
    SPI_WriteREG(0x49,0x00)
    SPI_WriteREG(0x4a,0x00)
    SPI_WriteREG(0x4b,0x00)
    SPI_WriteREG(0x4c,0x00)
    SPI_WriteREG(0x4d,0x00)
    SPI_WriteREG(0x4e,0x00)
    SPI_WriteREG(0x4f,0x60)
    SPI_WriteREG(0x50,0xff)
    SPI_WriteREG(0x51,0x00)
    SPI_WriteREG(0x52,0x00)
    SPI_WriteREG(0x53,0x1f)
    #FIFO缓冲区待发送长度阈值
    SPI_WriteREG(0x54,0x10)
    
    #TX配置
    SPI_WriteREG(0x55,0x54)
    SPI_WriteREG(0x56,0x81)
    SPI_WriteREG(0x57,0x08)
    SPI_WriteREG(0x58,0x00)
    SPI_WriteREG(0x59,0x86)
    SPI_WriteREG(0x5a,0xd0)
    SPI_WriteREG(0x5b,0x00)
    SPI_WriteREG(0x5c,0x49)
    SPI_WriteREG(0x5d,0x12)
    SPI_WriteREG(0x5e,0x3f)
    SPI_WriteREG(0x5f,0x7f)
    
    
    SPI_WriteREG(0x61,0x02)
    SPI_WriteREG(0x62,0xFF)
    SPI_WriteREG(0x63,0x00)
    SPI_WriteREG(0x64,0x00)
    SPI_WriteREG(0x65,0x39)
    SPI_WriteREG(0x66,0x00)
    if phrase == 1:
        SPI_WriteREG(0x67,0x20)
    else:
        SPI_WriteREG(0x67,0x00)
    SPI_WriteREG(0x68,0x00)
    SPI_WriteREG(0x69,0xA0)
    SPI_WriteREG(0x6A,0x00)
    #进入sleep模式
    SPI_WriteREG(0x60,0x10)
    while SPI_ReadREG(0x61) & 0b00001111 != 0x01:
        pass

def CMT2300A_SetFREQ(freq):
    baseFreq = -1
    SPI_WriteREG(0x60,0x02)
    while SPI_ReadREG(0x61) & 0b00001111 != 0x02:
        pass
    
    if 135.0 <= freq < 140.0:
        SPI_WriteREG(0x18,0x3e)
        SPI_WriteREG(0x19,0x91)
        SPI_WriteREG(0x1A,0x02)
        SPI_WriteREG(0x1B,0x37)
        SPI_WriteREG(0x1C,0x3e)
        SPI_WriteREG(0x1D,0x4e)
        SPI_WriteREG(0x1E,0xec)
        SPI_WriteREG(0x1F,0xe4)
        SPI_WriteREG(0x27,0x0a)
        baseFreq = 135.0
    elif 140.0 <= freq < 145.0:
        SPI_WriteREG(0x18,0x40)
        SPI_WriteREG(0x19,0xdf)
        SPI_WriteREG(0x1A,0xee)
        SPI_WriteREG(0x1B,0x3b)
        SPI_WriteREG(0x1C,0x40)
        SPI_WriteREG(0x1D,0x9d)
        SPI_WriteREG(0x1E,0xd8)
        SPI_WriteREG(0x1F,0xe9)
        SPI_WriteREG(0x27,0x0a)
        baseFreq = 140.0
    elif 145.0 <= freq < 150:
        SPI_WriteREG(0x18,0x43)
        SPI_WriteREG(0x19,0x2e)
        SPI_WriteREG(0x1A,0xd8)
        SPI_WriteREG(0x1B,0x30)
        SPI_WriteREG(0x1C,0x42)
        SPI_WriteREG(0x1D,0xec)
        SPI_WriteREG(0x1E,0xc4)
        SPI_WriteREG(0x1F,0x9e)
        SPI_WriteREG(0x27,0x0a)
        baseFreq = 145.0
    elif 150.0 <= freq < 155:
        SPI_WriteREG(0x18,0x45)
        SPI_WriteREG(0x19,0x7d)
        SPI_WriteREG(0x1A,0xc7)
        SPI_WriteREG(0x1B,0x35)
        SPI_WriteREG(0x1C,0x45)
        SPI_WriteREG(0x1D,0x3b)
        SPI_WriteREG(0x1E,0xb1)
        SPI_WriteREG(0x1F,0x93)
        SPI_WriteREG(0x27,0x0b)
        baseFreq = 150.0
    elif 155.0 <= freq < 160:
        SPI_WriteREG(0x18,0x47)
        SPI_WriteREG(0x19,0xcc)
        SPI_WriteREG(0x1A,0xb3)
        SPI_WriteREG(0x1B,0x3a)
        SPI_WriteREG(0x1C,0x47)
        SPI_WriteREG(0x1D,0x89)
        SPI_WriteREG(0x1E,0x9d)
        SPI_WriteREG(0x1F,0x98)
        SPI_WriteREG(0x27,0x0b)
        baseFreq = 155.0
    elif 160.0 <= freq < 165:
        SPI_WriteREG(0x18,0x49)
        SPI_WriteREG(0x19,0x1b)
        SPI_WriteREG(0x1A,0xa0)
        SPI_WriteREG(0x1B,0x3f)
        SPI_WriteREG(0x1C,0x49)
        SPI_WriteREG(0x1D,0xd8)
        SPI_WriteREG(0x1E,0x89)
        SPI_WriteREG(0x1F,0x9d)
        SPI_WriteREG(0x27,0x0c)
        baseFreq = 160.0
    elif 165.0 <= freq <= 170:
        SPI_WriteREG(0x18,0x4c)
        SPI_WriteREG(0x19,0x69)
        SPI_WriteREG(0x1A,0x8c)
        SPI_WriteREG(0x1B,0x34)
        SPI_WriteREG(0x1C,0x4c)
        SPI_WriteREG(0x1D,0x27)
        SPI_WriteREG(0x1E,0x76)
        SPI_WriteREG(0x1F,0x92)
        SPI_WriteREG(0x27,0x0c)
        baseFreq = 165.0
    else:
        print("Unsupport frequency!")
    SPI_WriteREG(0x64,0x0a) #FH_OFFSET = 10
    channel = round((freq - baseFreq) / 0.025)
    print(f"freq:{freq} baseFreq:{baseFreq} offset:{channel}")
    SPI_WriteREG(0x63,channel) #FH_CHANNEL
    #进入sleep模式
    SPI_WriteREG(0x60,0x10)
    while SPI_ReadREG(0x61) & 0b00001111 != 0x01:
        pass
    
def CMT2300A_FIFO_Clear():
    SPI_WriteREG(0x6c,0x01)

def CMT2300A_GoTX():
    SPI_WriteREG(0x60,0x40)

def CMT2300A_Go_IDLE():
    SPI_WriteREG(0x60,0x02)
    

        

